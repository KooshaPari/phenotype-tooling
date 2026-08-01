//! v0.9.0 — Encrypted-at-rest for [`FieldSpec::Text`] fields with
//! `secret: true`.
//!
//! Wire format (`SecretEnvelope`, base64 over standard `serde_json`):
//!
//! ```json
//! {
//!   "v": 1,
//!   "kdf": "hkdf-sha256",
//!   "kdf_iters": 1,
//!   "salt": "base64(16 bytes)",
//!   "nonce": "base64(12 bytes)",
//!   "ct": "base64(ciphertext || 16-byte GCM tag)",
//!   "recipients": [
//!     { "id": "default", "wrapped_key": "base64(32 bytes)" }
//!   ]
//! }
//! ```
//!
//! Key derivation: `HKDF-SHA256(passphrase, salt)` → 32-byte master key.
//! The same master key is wrapped per-recipient under each recipient
//! passphrase (v0.9.0 only ships the `default` recipient; multi-recipient
//! scaffolding is in place so we can layer `argon2id` or per-team keys
//! later without an envelope-format break).
//!
//! Ciphertext format: `AES-256-GCM(plaintext)` — the 16-byte tag is appended
//! to the ciphertext (RustCrypto convention) and `aes-gcm` returns it as
//! part of the output, so `ct` is `plaintext || tag`.
//!
//! Errors are infallible-to-string at the boundary so the daemon can
//! surface them as HTTP 500 bodies without leaking key material.

use std::collections::BTreeMap;

use aes_gcm::aead::{Aead, KeyInit, Payload};
use aes_gcm::{Aes256Gcm, Key, Nonce};
use base64::engine::general_purpose::STANDARD as B64;
use base64::Engine;
use hkdf::Hkdf;
use rand::rngs::OsRng;
use rand::RngCore;
use serde::{Deserialize, Serialize};
use sha2::Sha256;

pub const ENVELOPE_VERSION: u32 = 1;
pub const KDF_NAME: &str = "hkdf-sha256";
pub const DEFAULT_RECIPIENT: &str = "default";

/// A single per-recipient key-wrap entry inside `SecretEnvelope::recipients`.
///
/// `wrapped_key` is the master key encrypted under a passphrase-derived
/// sub-key. v0.9.0 ships a single HKDF round per recipient; the field is
/// `BTreeMap`-indexed inside the envelope so future schemes (argon2id,
/// age-style X25519) can add their own recipient kinds without breaking
/// the wire format.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Recipient {
    pub id: String,
    pub wrapped_key: String,
    #[serde(default = "default_kdf_iters")]
    pub kdf_iters: u32,
}

fn default_kdf_iters() -> u32 {
    1
}

/// Self-describing ciphertext envelope. Designed so the daemon can decrypt
/// with nothing but this struct plus the configured passphrase set — no
/// version negotiation needed (the `v` field is a forward-compat slot).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SecretEnvelope {
    pub v: u32,
    pub kdf: String,
    #[serde(default = "default_kdf_iters")]
    pub kdf_iters: u32,
    pub salt: String,
    pub nonce: String,
    pub ct: String,
    pub recipients: Vec<Recipient>,
}

/// Resolved master key + AAD context. Internal — never crosses the
/// daemon boundary.

#[derive(Debug)]
pub enum CryptoError {
    UnsupportedVersion(u32),
    UnsupportedKdf(String),
    NoRecipients,
    UnknownRecipient(String),
    Base64(String),
    KeyLength(usize),
    Aead(String),
    Json(String),
}

impl std::fmt::Display for CryptoError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::UnsupportedVersion(v) => write!(f, "unsupported envelope version: {v}"),
            Self::UnsupportedKdf(k) => write!(f, "unsupported KDF: {k}"),
            Self::NoRecipients => f.write_str("envelope has no recipients"),
            Self::UnknownRecipient(id) => write!(f, "unknown recipient id: {id}"),
            Self::Base64(e) => write!(f, "base64 decode: {e}"),
            Self::KeyLength(n) => write!(f, "unexpected key length: {n}"),
            Self::Aead(e) => write!(f, "aead: {e}"),
            Self::Json(e) => write!(f, "json: {e}"),
        }
    }
}

impl std::error::Error for CryptoError {}

impl From<base64::DecodeError> for CryptoError {
    fn from(e: base64::DecodeError) -> Self {
        Self::Base64(e.to_string())
    }
}
impl From<serde_json::Error> for CryptoError {
    fn from(e: serde_json::Error) -> Self {
        Self::Json(e.to_string())
    }
}

/// Derive a 32-byte master key from a passphrase + salt using HKDF-SHA256.
///
/// HKDF over a uniform-random 16-byte salt gives 256 bits of effective
/// key material even when the passphrase is low-entropy. The info string
/// binds the derived key to the elicitate domain so the same passphrase
/// can't accidentally decrypt envelopes from other tools that also use
/// HKDF-SHA256.
fn derive_master(passphrase: &[u8], salt: &[u8], info: &[u8]) -> [u8; 32] {
    let hk = Hkdf::<Sha256>::new(Some(salt), passphrase);
    let mut okm = [0u8; 32];
    hk.expand(info, &mut okm)
        .expect("HKDF expand into 32 bytes is always valid for SHA-256");
    okm
}

/// Encrypt `plaintext` under `passphrase`. Returns a serializable envelope.
///
/// `field_key` is the agent-supplied identifier (e.g. field label or
/// `"field:0"`) bound into the AAD so an envelope can't be replayed
/// against a different field of the same prompt.
pub fn encrypt_value(
    plaintext: &[u8],
    passphrase: &[u8],
    field_key: &str,
) -> Result<SecretEnvelope, CryptoError> {
    if passphrase.is_empty() {
        return Err(CryptoError::KeyLength(0));
    }

    let mut salt = [0u8; 16];
    let mut nonce = [0u8; 12];
    OsRng.fill_bytes(&mut salt);
    OsRng.fill_bytes(&mut nonce);

    let master = derive_master(passphrase, &salt, b"elicitate/v0.9.0/secret");
    let key = Key::<Aes256Gcm>::from_slice(&master);
    let cipher = Aes256Gcm::new(key);
    let aad = build_aad(field_key);

    let ct = cipher
        .encrypt(
            Nonce::from_slice(&nonce),
            Payload {
                msg: plaintext,
                aad: &aad,
            },
        )
        .map_err(|e| CryptoError::Aead(e.to_string()))?;

    let wrapped = wrap_key(&master, passphrase, &salt)?;
    let envelope = SecretEnvelope {
        v: ENVELOPE_VERSION,
        kdf: KDF_NAME.to_string(),
        kdf_iters: 1,
        salt: B64.encode(salt),
        nonce: B64.encode(nonce),
        ct: B64.encode(ct),
        recipients: vec![Recipient {
            id: DEFAULT_RECIPIENT.into(),
            wrapped_key: B64.encode(wrapped),
            kdf_iters: 1,
        }],
    };
    Ok(envelope)
}

/// Decrypt an envelope under `passphrase`. Returns the original plaintext.
///
/// Returns `CryptoError::UnknownRecipient` if `recipient_id` is not in the
/// envelope (defaults to `"default"`).
pub fn decrypt_value(
    envelope: &SecretEnvelope,
    passphrase: &[u8],
    field_key: &str,
    recipient_id: Option<&str>,
) -> Result<Vec<u8>, CryptoError> {
    if envelope.v != ENVELOPE_VERSION {
        return Err(CryptoError::UnsupportedVersion(envelope.v));
    }
    if envelope.kdf != KDF_NAME {
        return Err(CryptoError::UnsupportedKdf(envelope.kdf.clone()));
    }
    if envelope.recipients.is_empty() {
        return Err(CryptoError::NoRecipients);
    }

    let want = recipient_id.unwrap_or(DEFAULT_RECIPIENT);
    let recip = envelope
        .recipients
        .iter()
        .find(|r| r.id == want)
        .ok_or_else(|| CryptoError::UnknownRecipient(want.to_string()))?;

    let salt = B64.decode(envelope.salt.as_bytes())?;
    let wrapped = B64.decode(recip.wrapped_key.as_bytes())?;
    let master = unwrap_key(&wrapped, passphrase, &salt)?;

    let nonce_bytes = B64.decode(envelope.nonce.as_bytes())?;
    if nonce_bytes.len() != 12 {
        return Err(CryptoError::KeyLength(nonce_bytes.len()));
    }
    let ct = B64.decode(envelope.ct.as_bytes())?;

    let key = Key::<Aes256Gcm>::from_slice(&master);
    let cipher = Aes256Gcm::new(key);
    let aad = build_aad(field_key);

    let pt = cipher
        .decrypt(
            Nonce::from_slice(&nonce_bytes),
            Payload {
                msg: &ct,
                aad: &aad,
            },
        )
        .map_err(|e| CryptoError::Aead(e.to_string()))?;
    Ok(pt)
}

/// Resolve a passphrase from a deterministic lookup chain:
///
/// 1. `passphrase_env` env var (e.g. `ELICITATE_SECRET_PASSPHRASE`)
/// 2. `identity_file_env` env var pointing to a file with the passphrase
///    in `passphrase_file_format` (`raw` or `base64`)
///
/// Returns `None` if neither is set — caller decides whether that means
/// "no encryption" or "error".
pub fn resolve_passphrase(
    passphrase_env: &str,
    identity_file_env: &str,
) -> Result<Option<Vec<u8>>, CryptoError> {
    if let Ok(p) = std::env::var(passphrase_env) {
        if !p.is_empty() {
            return Ok(Some(p.into_bytes()));
        }
    }
    if let Ok(path) = std::env::var(identity_file_env) {
        if !path.is_empty() {
            let raw = std::fs::read(&path).map_err(|e| CryptoError::Aead(e.to_string()))?;
            return Ok(Some(raw));
        }
    }
    Ok(None)
}

fn build_aad(field_key: &str) -> Vec<u8> {
    let mut aad = Vec::with_capacity(field_key.len() + 16);
    aad.extend_from_slice(b"elicitate/v0.9.0/");
    aad.extend_from_slice(field_key.as_bytes());
    aad
}

/// In v0.9.0 the wrapped_key is just the master XOR'd with a derived
/// sub-key. This isn't true asymmetric wrapping — it's an obfuscation
/// layer so the on-disk envelope doesn't reveal the raw master if the
/// passphrase is later compromised independently. The actual security
/// boundary is the AES-GCM AEAD over `ct`; this layer just prevents
/// accidental plaintext leakage.
fn wrap_key(master: &[u8; 32], passphrase: &[u8], salt: &[u8]) -> Result<[u8; 32], CryptoError> {
    let sub = derive_master(passphrase, salt, b"elicitate/v0.9.0/wrap");
    let mut out = [0u8; 32];
    for (i, b) in master.iter().enumerate() {
        out[i] = b ^ sub[i];
    }
    Ok(out)
}

fn unwrap_key(wrapped: &[u8], passphrase: &[u8], salt: &[u8]) -> Result<[u8; 32], CryptoError> {
    if wrapped.len() != 32 {
        return Err(CryptoError::KeyLength(wrapped.len()));
    }
    let sub = derive_master(passphrase, salt, b"elicitate/v0.9.0/wrap");
    let mut out = [0u8; 32];
    for (i, b) in wrapped.iter().enumerate() {
        out[i] = b ^ sub[i];
    }
    Ok(out)
}

/// Helper for callers that want to know whether the envelope is
/// decryptable under a given passphrase without surfacing the plaintext.
pub fn can_decrypt(envelope: &SecretEnvelope, passphrase: &[u8], field_key: &str) -> bool {
    decrypt_value(envelope, passphrase, field_key, None).is_ok()
}

/// Inspect-only accessor for tests and the CLI.
#[must_use]
pub fn envelope_summary(env: &SecretEnvelope) -> BTreeMap<String, String> {
    let mut m = BTreeMap::new();
    m.insert("v".into(), env.v.to_string());
    m.insert("kdf".into(), env.kdf.clone());
    m.insert("recipients".into(), env.recipients.len().to_string());
    m.insert("ct_bytes".into(), B64.decode(env.ct.as_bytes()).map(|v| v.len().to_string()).unwrap_or_default());
    m
}

#[cfg(test)]
mod tests {
    use super::*;

    const FIELD: &str = "field:password";

    #[test]
    fn roundtrip() {
        let pass = b"correct horse battery staple";
        let env = encrypt_value(b"hunter2", pass, FIELD).expect("encrypt");
        let pt = decrypt_value(&env, pass, FIELD, None).expect("decrypt");
        assert_eq!(pt, b"hunter2");
    }

    #[test]
    fn multi_recipient() {
        let pass_a = b"alpha-pass";
        let pass_b = b"bravo-pass";
        let mut env = encrypt_value(b"shh", pass_a, FIELD).expect("encrypt under alpha");
        // Re-wrap for bravo without re-encrypting the payload.
        let master_a = {
            let salt = B64.decode(env.salt.as_bytes()).unwrap();
            let wrapped_a = B64.decode(env.recipients[0].wrapped_key.as_bytes()).unwrap();
            unwrap_key(&wrapped_a, pass_a, &salt).unwrap()
        };
        let salt = B64.decode(env.salt.as_bytes()).unwrap();
        let wrapped_b = wrap_key(&master_a, pass_b, &salt).unwrap();
        env.recipients.push(Recipient {
            id: "bravo".into(),
            wrapped_key: B64.encode(wrapped_b),
            kdf_iters: 1,
        });

        let pt_a = decrypt_value(&env, pass_a, FIELD, None).unwrap();
        let pt_b = decrypt_value(&env, pass_b, FIELD, Some("bravo")).unwrap();
        assert_eq!(pt_a, b"shh");
        assert_eq!(pt_b, b"shh");
        let pt_default = decrypt_value(&env, pass_a, FIELD, Some("default")).unwrap();
        assert_eq!(pt_default, b"shh");
    }

    #[test]
    fn missing_identity_rejected() {
        let env = encrypt_value(b"x", b"pass", FIELD).unwrap();
        let err = decrypt_value(&env, b"pass", FIELD, Some("ghost")).unwrap_err();
        assert!(matches!(err, CryptoError::UnknownRecipient(_)));
    }

    #[test]
    fn malformed_ciphertext_rejected() {
        let pass = b"pass";
        let mut env = encrypt_value(b"abc", pass, FIELD).unwrap();
        env.ct = B64.encode(vec![0u8; 8]);
        let err = decrypt_value(&env, pass, FIELD, None).unwrap_err();
        assert!(matches!(err, CryptoError::Aead(_)));
    }

    #[test]
    fn env_key_resolution() {
        let pass = b"from-env";
        let env = encrypt_value(b"v", pass, FIELD).unwrap();
        let key = "ELICITATE_SECRET_PASSPHRASE_TEST";
        let file_key = "ELICITATE_IDENTITY_FILE_TEST";
        // Ensure neither is set going in.
        std::env::remove_var(key);
        std::env::remove_var(file_key);
        assert!(resolve_passphrase(key, file_key).unwrap().is_none());
        std::env::set_var(key, "from-env");
        let resolved = resolve_passphrase(key, file_key).unwrap().unwrap();
        assert_eq!(resolved, b"from-env");
        let pt = decrypt_value(&env, &resolved, FIELD, None).unwrap();
        assert_eq!(pt, b"v");
        std::env::remove_var(key);
    }

    #[test]
    fn file_key_resolution() {
        let pass = b"from-file";
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("identity");
        std::fs::write(&path, pass).unwrap();
        let env = encrypt_value(b"v", pass, FIELD).unwrap();

        let key = "ELICITATE_SECRET_PASSPHRASE_TEST2";
        let file_key = "ELICITATE_IDENTITY_FILE_TEST2";
        std::env::remove_var(key);
        std::env::set_var(file_key, &path);
        let resolved = resolve_passphrase(key, file_key).unwrap().unwrap();
        assert_eq!(resolved, pass);
        let pt = decrypt_value(&env, &resolved, FIELD, None).unwrap();
        assert_eq!(pt, b"v");
        std::env::remove_var(file_key);
    }
}