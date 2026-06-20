# Submodule bump procedure

1. Gate passes on interim canonical fork `main` (`go build ./...` minimum).
2. In fork: note merge PR on `main`.
3. In phenotype-gateway:

```bash
cd third_party/<plane>
git fetch origin
git checkout <sha>
cd ../..
git add third_party/<plane>
```

4. Update [docs/UPSTREAM.md](../UPSTREAM.md) pin table.
5. Registry PR: disposition note + `GATEWAY_FEATURE_PARITY` if smoke status changed.

## Current pins (see UPSTREAM.md)

Update only after fork gates green.
