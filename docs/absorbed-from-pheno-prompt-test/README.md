# pheno-prompt-test

> pytest plugin for prompt regression tests (LLM behavior as test cases).

This is the canonical implementation of the **`pheno-prompt-test`** AI-DD
crutch described in `FLEET_100TASK_DAG_V4.md` §70.3 + §77.3.

## What it does

Auto-collects every `tests/prompts/*.prompt` file in your repo and runs each
as a pytest test case. The case specifies:

- **`input`** — the user message / tool input
- **`runner`** — the function to call (a `module::attr` spec)
- **`expected_output_matches`** — regex the output must match
- **`expected_tool_calls`** — list of tool calls the runner must invoke
- **`expected_no_calls`** — list of tool calls the runner must NOT invoke

## Install

```bash
pip install pheno-prompt-test
```

## Usage

### 1. Drop a prompt file in `tests/prompts/`

```yaml
# tests/prompts/issue_token.prompt
name: issue_token_basic
input: |
  Issue a token with scope=read for user=alice
runner: my_pkg.runners::dispatch
expected_output_matches: "scope.*read.*alice"
expected_tool_calls: [create_token]
expected_no_calls: [delete_user, rotate_keys]
```

### 2. Implement the runner

```python
# my_pkg/runners.py
def dispatch(user_input: str) -> dict:
    """Call the LLM, return {output: str, tool_calls: [str, ...]}."""
    ...
```

### 3. Run pytest

```bash
$ pytest
tests/prompts/issue_token.prompt::issue_token_basic PASSED
```

The plugin auto-registers itself as a `pytest11` entry point, so no
`conftest.py` is required.

## Spec

- The plugin entry point is `pheno_prompt_test.plugin`.
- The YAML schema is `PromptCase` in [`src/pheno_prompt_test/plugin.py`](src/pheno_prompt_test/plugin.py).
- The DAG reference is `FLEET_100TASK_DAG_V4.md` §77.3.

## Eat your own dogfood

This repo uses itself. See [`AGENTS.md`](AGENTS.md) and [`llms.txt`](llms.txt).

## License

MIT
