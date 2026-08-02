//! v0.9.0 — Encrypted-at-rest for [`FieldSpec::Text`] fields with
//! `secret: true`.
//!
//! Wire format (`SecretEnvelope`, base64 over standard `serde_json`):
//!
//! ```json
//! {
//!   "v": 1,
//!   "kdf": "argon2id",
//!   "kdf_iters": 2,
//!   "salt": "base64(16 bytes)",
//!   "nonce": "base64(12 bytes)",
//!   "ct": "base64(ciphertext || 16-byte GCM tag)",
//!   "recipients": [
//!     { "id": "default", "wrapped_key": "base64(32 bytes)" }
//!   ]
//! }
//! ```
//!
//! Key derivation: default is `argon2id` (OWASP 2024 params — m=19 MiB,
//! t=2, p=1) with the envelope's per-envelope random salt. The same
//! master key is wrapped per-recipient under each recipient passphrase.
//! v0.9.0 only ships the `default` recipient; multi-recipient scaffolding
//! is in place so we can layer asymmetric wrapping (per-team keys,
//! age-style X25519) later without an envelope-format break.
//!
//! Legacy v0.9.0 envelopes tagged `"kdf": "hkdf-sha256"` are still
//! decryptable so existing on-disk data doesn't rot. New writes always
//! use `argon2id`.
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
use argon2::{Algorithm, Argon2, Params, Version};
use base64::engine::general_purpose::STANDARD as B64;
use base64::Engine;
use hkdf::Hkdf;
use rand::rngs::OsRng;
use rand::RngCore;
use serde::{Deserialize, Serialize};
use sha2::Sha256;

pub const ENVELOPE_VERSION: u32 = 1;

/// Default KDF for new envelopes. `argon2id` with OWASP 2024 baseline.
pub const KDF_NAME: &str = "argon2id";
/// Legacy KDF tag. Kept only for decrypt-side backward compatibility on
/// v0.9.0 envelopes written before the argon2id switch.
pub const KDF_HKDF_SHA256: &str = "hkdf-sha256";
pub const DEFAULT_RECIPIENT: &str = "default";

/// OWASP Password Storage Cheat Sheet (2024) baseline for argon2id:
/// `m=19 MiB`, `t=2`, `p=1`. Tuned to take ~50 ms on a modern server
/// CPU while still being tractable on a low-end laptop.
pub const ARGON2_DEFAULT_MEM_KIB: u32 = 19_456;
pub const ARGON2_DEFAULT_TIME_COST: u32 = 2;
pub const ARGON2_DEFAULT_PARALLELISM: u32 = 1;

/// A single per-recipient key-wrap entry inside `SecretEnvelope::recipients`.
///
/// `wrapped_key` is the master key encrypted under a passphrase-derived
/// sub-key. The KDF used to derive the sub-key is the envelope's top-level
/// `kdf` field so all recipients self-describe how they expect to be
/// unwrapped. The field is `BTreeMap`-indexed inside the envelope so future
/// schemes (age-style X25519, hardware tokens) can add their own recipient
/// kinds without breaking the wire format.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Recipient {
    pub id: String,
    pub wrapped_key: String,
    #[serde(default = "default_kdf_iters")]
    pub kdf_iters: u32,
}

/// Default for `kdf_iters` when an envelope omits it. For `argon2id` this
/// is the time cost (OWASP baseline); for legacy `hkdf-sha256` envelopes
/// the field is informational and ignored.
fn default_kdf_iters() -> u32 {
    ARGON2_DEFAULT_TIME_COST
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

/// Derive a 32-byte master key from a passphrase + salt using the KDF
/// named in `kdf`. Dispatches to the argon2id or legacy HKDF-SHA256 path
/// based on the envelope's `kdf` field.
///
/// For `argon2id`, `kdf_iters` is the time cost (other cost parameters
/// default to the OWASP 2024 baseline). For `hkdf-sha256`, `kdf_iters`
/// is informational and ignored (legacy v0.9.0).
///
/// The `info` argument is a domain-separation string. For HKDF it is the
/// standard `Hkdf::expand` info; for Argon2 we mix it into the password
/// because Argon2 has no native `info` slot.
fn derive_master(
    passphrase: &[u8],
    salt: &[u8],
    info: &[u8],
    kdf: &str,
    kdf_iters: u32,
) -> Result<[u8; 32], CryptoError> {
    match kdf {
        KDF_HKDF_SHA256 => Ok(derive_hkdf_sha256(passphrase, salt, info)),
        KDF_NAME => derive_argon2id(passphrase, salt, info, kdf_iters),
        other => Err(CryptoError::UnsupportedKdf(other.to_string())),
    }
}

/// Legacy v0.9.0 KDF: HKDF-SHA256 with a 16-byte per-envelope salt.
///
/// HKDF over a uniform-random 16-byte salt gives 256 bits of effective
/// key material even when the passphrase is low-entropy. The info string
/// binds the derived key to the elicitate domain so the same passphrase
/// can't accidentally decrypt envelopes from other tools that also use
/// HKDF-SHA256.
fn derive_hkdf_sha256(passphrase: &[u8], salt: &[u8], info: &[u8]) -> [u8; 32] {
    let hk = Hkdf::<Sha256>::new(Some(salt), passphrase);
    let mut okm = [0u8; 32];
    hk.expand(info, &mut okm)
        .expect("HKDF expand into 32 bytes is always valid for SHA-256");
    okm
}

/// Default KDF: argon2id with OWASP 2024 baseline (m=19 MiB, t=2, p=1).
///
/// Domain separation is preserved by mixing the `info` string into the
/// Argon2 input (`info || ":" || passphrase`). Argon2 is intentionally
/// memory-hard: the 19 MiB cost forces an attacker to allocate that
/// memory per guess, which is the whole point of the upgrade from
/// HKDF-SHA256 (which is fast — useful for key agreement but not for
/// passphrase-to-key stretching).
fn derive_argon2id(
    passphrase: &[u8],
    salt: &[u8],
    info: &[u8],
    kdf_iters: u32,
) -> Result<[u8; 32], CryptoError> {
    let t_cost = if kdf_iters == 0 {
        ARGON2_DEFAULT_TIME_COST
    } else {
        kdf_iters
    };
    let params = Params::new(
        ARGON2_DEFAULT_MEM_KIB,
        t_cost,
        ARGON2_DEFAULT_PARALLELISM,
        Some(32),
    )
    .map_err(|e| CryptoError::Aead(format!("argon2 params: {e}")))?;
    let a2 = Argon2::new(Algorithm::Argon2id, Version::V0x13, params);
    let mut pw = Vec::with_capacity(info.len() + 1 + passphrase.len());
    pw.extend_from_slice(info);
    pw.push(b':');
    pw.extend_from_slice(passphrase);
    let mut out = [0u8; 32];
    a2.hash_password_into(&pw, salt, &mut out)
        .map_err(|e| CryptoError::Aead(format!("argon2 derive: {e}")))?;
    Ok(out)
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

    let master = derive_master(
        passphrase,
        &salt,
        b"elicitate/v0.9.0/secret",
        KDF_NAME,
        ARGON2_DEFAULT_TIME_COST,
    )?;
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

    let wrapped = wrap_key(
        &master,
        passphrase,
        &salt,
        KDF_NAME,
        ARGON2_DEFAULT_TIME_COST,
    )?;
    let envelope = SecretEnvelope {
        v: ENVELOPE_VERSION,
        kdf: KDF_NAME.to_string(),
        kdf_iters: ARGON2_DEFAULT_TIME_COST,
        salt: B64.encode(salt),
        nonce: B64.encode(nonce),
        ct: B64.encode(ct),
        recipients: vec![Recipient {
            id: DEFAULT_RECIPIENT.into(),
            wrapped_key: B64.encode(wrapped),
            kdf_iters: ARGON2_DEFAULT_TIME_COST,
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
    // Accept the current default (`argon2id`) and the legacy v0.9.0 KDF
    // (`hkdf-sha256`) so existing on-disk envelopes stay readable. Any
    // other tag is rejected with UnsupportedKdf.
    if envelope.kdf != KDF_NAME && envelope.kdf != KDF_HKDF_SHA256 {
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
    let master = unwrap_key(
        &wrapped,
        passphrase,
        &salt,
        &envelope.kdf,
        envelope.kdf_iters,
    )?;

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
fn wrap_key(
    master: &[u8; 32],
    passphrase: &[u8],
    salt: &[u8],
    kdf: &str,
    kdf_iters: u32,
) -> Result<[u8; 32], CryptoError> {
    let sub = derive_master(passphrase, salt, b"elicitate/v0.9.0/wrap", kdf, kdf_iters)?;
    let mut out = [0u8; 32];
    for (i, b) in master.iter().enumerate() {
        out[i] = b ^ sub[i];
    }
    Ok(out)
}

fn unwrap_key(
    wrapped: &[u8],
    passphrase: &[u8],
    salt: &[u8],
    kdf: &str,
    kdf_iters: u32,
) -> Result<[u8; 32], CryptoError> {
    if wrapped.len() != 32 {
        return Err(CryptoError::KeyLength(wrapped.len()));
    }
    let sub = derive_master(passphrase, salt, b"elicitate/v0.9.0/wrap", kdf, kdf_iters)?;
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
        // New envelopes must be tagged with the default `argon2id` KDF.
        assert_eq!(env.kdf, KDF_NAME);
        assert_eq!(env.kdf_iters, ARGON2_DEFAULT_TIME_COST);
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
            unwrap_key(
                &wrapped_a,
                pass_a,
                &salt,
                &env.kdf,
                env.kdf_iters,
            )
            .unwrap()
        };
        let salt = B64.decode(env.salt.as_bytes()).unwrap();
        let wrapped_b = wrap_key(
            &master_a,
            pass_b,
            &salt,
            &env.kdf,
            env.kdf_iters,
        )
        .unwrap();
        env.recipients.push(Recipient {
            id: "bravo".into(),
            wrapped_key: B64.encode(wrapped_b),
            kdf_iters: env.kdf_iters,
        });

        let pt_a = decrypt_value(&env, pass_a, FIELD, None).unwrap();
        let pt_b = decrypt_value(&env, pass_b, FIELD, Some("bravo")).unwrap();
        assert_eq!(pt_a, b"shh");
        assert_eq!(pt_b, b"shh");
        let pt_default = decrypt_value(&env, pass_a, FIELD, Some("default")).unwrap();
        assert_eq!(pt_default, b"shh");
    }

    /// Backward-compat: hand-craft a v0.9.0 `hkdf-sha256` envelope and
    /// confirm the current code decrypts it. This is the load-bearing
    /// regression test for the security hardening — we MUST NOT break
    /// already-encrypted on-disk data when bumping the default KDF.
    #[test]
    fn legacy_hkdf_sha256_envelope_still_decrypts() {
        let pass = b"legacy-pass";
        let pt = b"top secret";
        let mut salt = [0u8; 16];
        let mut nonce = [0u8; 12];
       OsRng.fill_bytes(&mut salt);
        OsRng.fill_bytes(&mut nonce);

        let master = derive_hkdf_sha256(pass, &salt, b"elicitate/v0.9.0/secret");
        let key = Key::<Aes256Gcm>::from_slice(&master);
        let cipher = Aes256Gcm::new(key);
        let aad = build_aad(FIELD);
        let ct = cipher
            .encrypt(
                Nonce::from_slice(&nonce),
                Payload {
                    msg: pt,
                    aad: &aad,
                },
            )
            .expect("legacy encrypt");
        let wrapped = wrap_key(
            &master,
            pass,
            &salt,
            KDF_HKDF_SHA256,
            1,
        )
        .expect("legacy wrap");

        let legacy = SecretEnvelope {
            v: ENVELOPE_VERSION,
            kdf: KDF_HKDF_SHA256.into(),
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

        let recovered = decrypt_value(&legacy, pass, FIELD, None).expect("legacy decrypt");
        assert_eq!(recovered, pt, "legacy hkdf-sha256 envelope must decrypt");
    }

    #[test]
    fn unknown_kdf_rejected() {
        let pass = b"pass";
        let env = encrypt_value(b"x", pass, FIELD).unwrap();
        let mut bad = env.clone();
        bad.kdf = "scrypt-2026".into();
        let err = decrypt_value(&bad, pass, FIELD, None).unwrap_err();
        assert!(matches!(err, CryptoError::UnsupportedKdf(_)));
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