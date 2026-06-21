# Configuration Guide for thegent-cli-share

All runtime configuration is centralised in a single module:
`src/thegent_cli_share/config.py`

## Mechanism

Configuration values are **module-level constants** defined in `config.py`.
You can override any value without touching code by setting the corresponding
environment variable before launching the CLI.

    export THEGENT_LOCK_TIMEOUT=7200   # 2-hour lock timeout
    thegent-sharecli lock-acquire my-hash --pid 1234

## Configuration Reference

### Lock Configuration

| Variable                  | Default | Description                                      |
| ------------------------- | ------- | ------------------------------------------------ |
| `THEGENT_LOCK_TIMEOUT`    | 3600    | Seconds before a command lock is stale/released. |
| `THEGENT_LOCK_TTL`        | 3600    | TTL for a freshly-acquired lock status object.   |

### Task Queue Configuration

| Variable               | Default | Description                                      |
| ---------------------- | ------- | ------------------------------------------------ |
| `THEGENT_QUEUE_TIMEOUT`| 3600    | Seconds before a queued task is considered dead. |

### Hash Configuration

| Variable                 | Default | Description                                          |
| ------------------------ | ------- | ---------------------------------------------------- |
| `THEGENT_HASH_ALGORITHM` | sha256  | Hash algorithm for command deduplication (e.g. sha256). |

### Health Score Thresholds

| Variable                             | Default | Description                                        |
| ------------------------------------ | ------- | -------------------------------------------------- |
| `THEGENT_HEALTH_HEALTHY_THRESHOLD`   | 0.8     | Minimum score for "healthy" status.                |
| `THEGENT_HEALTH_DEGRADED_THRESHOLD`  | 0.5     | Minimum score for "degraded" (below this = dead).  |

## Adding a New Configuration Key

1. Add the constant to `src/thegent_cli_share/config.py` with a `Final` type
   annotation and a default that reads from `os.environ.get("THEGENT_…", …)`.
2. Add the variable name to the `ALL_CONFIG_KEYS` tuple.
3. Update the `.env.example` and this document.
4. Import and use the constant in place of any hardcoded literal.

## .env File (Optional)

Copy `.env.example` to `.env` at the project root to keep overrides local.
The `.env` file is git-ignored and will **not** be committed.

    cp .env.example .env
    # edit .env to taste

> **Note:** The current `config.py` does **not** automatically load `.env`.
> Use `source .env` or your shell's equivalent, or wire in `python-dotenv`
> if automatic loading is desired.
