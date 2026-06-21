# authkit — AuthKit Python SDK aggregator

> **Status:** Re-export aggregator. The canonical home for the underlying
> implementation is **`KooshaPari/phenotype-python-sdk`** at
> `packages/auth-kit/`.  This aggregator exists for backwards compatibility
> with code that imports `from authkit import …` and to give a single,
> stable import surface for downstream consumers.

`authkit` re-exports the public APIs of three sibling packages that
historically lived under `AuthKit/python/`:

| Sub-package        | PyPI / canonical target                                     | Purpose                                            |
|--------------------|-------------------------------------------------------------|----------------------------------------------------|
| `pheno-auth`       | `phenotype-auth`  (in `phenotype-python-sdk/packages/auth-kit/python/pheno-auth`)  | Auth core: managers, MFA, JWT, SAML, SCIM, RBAC    |
| `pheno-credentials`| `phenotype-credentials`  (pending publication)              | Secure credential broker: keyring, encrypted store |
| `pheno-security`   | `phenotype-security`  (in `phenotype-python-sdk/packages/auth-kit/python/pheno-security`)  | Security: encryption, hashing, PII/secret scanning |

## Quickstart

```python
from authkit import AuthManager, CredentialBroker, PIIScanner

mgr = AuthManager(provider="auth0", client_id="...", client_secret="...")
creds = CredentialBroker()
api_key = creds.get_credential("OPENAI_API_KEY")

scanner = PIIScanner()
findings = scanner.scan_text("contact me at alice@example.com")
```

## Installation

Until the underlying packages are published to PyPI, install directly from
`phenotype-python-sdk` and add the local path for the three sub-packages:

```bash
pip install "phenotype-python-sdk @ git+https://github.com/KooshaPari/phenotype-python-sdk.git#subdirectory=packages/auth-kit/python/pheno-auth"
pip install "phenotype-python-sdk @ git+https://github.com/KooshaPari/phenotype-python-sdk.git#subdirectory=packages/auth-kit/python/pheno-security"
# pheno-credentials is staged for publication; until then install from
# this repo's source tree:
pip install "git+https://github.com/KooshaPari/AuthKit.git#subdirectory=python/pheno-credentials"
```

## Stability

`authkit.__version__` follows the latest published `pheno-auth` version.  The
re-exports track the union of the public APIs of the three underlying
packages; removed symbols are kept behind a `DeprecationWarning` for one
minor release before being dropped from `__all__`.

## Migration

| Old import path                                  | New canonical path                                     |
|--------------------------------------------------|--------------------------------------------------------|
| `from pheno_auth import AuthManager`             | `from authkit import AuthManager`  (or keep `pheno_auth`) |
| `from pheno_credentials import CredentialBroker` | `from authkit import CredentialBroker`                 |
| `from pheno_security import PIIScanner`          | `from authkit import PIIScanner`                       |

## See also

* `KooshaPari/phenotype-python-sdk` — canonical substrate
* `AuthKit/python/pheno-auth/README.md` — auth package details
* `AuthKit/python/pheno-credentials/README.md` — credentials details
* `AuthKit/python/pheno-security/README.md` — security utilities details

## License

MIT — see `AuthKit/LICENSE`.
