# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a vulnerability

Please report security issues to `security@phenotype.dev` (or open a
private GitHub issue). Do not open a public issue for security
vulnerabilities.

We aim to acknowledge reports within 2 business days and ship a fix
within 14 days for high-severity issues.

## Scope

`pheno-capacity` is a **pure-math library** with no I/O, no
network, no FFI, and no `unsafe` code. The attack surface is
limited to:

1. **Numeric overflow**: `vram_estimate` saturates to `u64::MAX` on
   overflow rather than panicking. `model_fits_in` treats saturated
   vram as "does not fit." Callers should not use saturated values
   for security-relevant decisions.
2. **Documentation examples**: doc tests are validated by
   `cargo test --doc` and the values shown in examples match
   published model-card numbers.

## Out-of-scope

- Numerical precision in downstream consumers (we use `u64` for
  byte counts and `f32` for the Chinchilla ratio; consumers needing
  higher precision should pre-validate inputs).
