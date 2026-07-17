# CLI Design Best Practices Reference

## 1. Framework Comparison

| Framework | Language | Best For |
|-----------|----------|----------|
| **Typer** | Python | Type-hint native CLIs |
| **Click** | Python | Complex CLIs with plugins |
| **Clap** | Rust | Performant Rust CLIs |
| **Cobra** | Go | Production Go CLIs |
| **Commander.js** | Node.js | Simple Node CLIs |
| **Oclif** | Node.js | Enterprise Node CLIs |

---

## 2. Python: Typer (Recommended)

```python
import typer

app = typer.Typer()

@app.command()
def greet(name: str = typer.Argument(..., help="Your name")):
    """Greet a user."""
    typer.echo(f"Hello, {name}!")

@app.command()
def create(
    name: str = typer.Option(..., help="Project name"),
    force: bool = typer.Option(False, "--force", help="Overwrite"),
):
    """Create a new project."""
    pass
```

---

## 3. Python: Click

```python
import click

@click.group()
def cli():
    """Main entry point."""
    pass

@cli.command()
@click.argument("filename")
@click.option("--format", "-f", type=click.Choice(["json", "yaml"]))
def convert(filename, format):
    """Convert FILE to FORMAT."""
    pass
```

---

## 4. Argument vs Option

| Type | Definition | Example |
|------|------------|---------|
| **Argument** | Positional, required | `git commit <msg>` |
| **Option** | Named flag | `git commit -m "msg"` |
| **Flag** | Boolean | `ls -a` |

---

## 5. Input Validation

### 5.1 Built-in

```python
@click.argument("port", type=int, clamp=True)
@click.option("--host", default="localhost")
def serve(port, host):
    if port < 1 or port > 65535:
        raise click.ClickException("Port must be 1-65535")
```

### 5.2 Pydantic Integration

```python
from pydantic import BaseModel, Field
import typer

class ConfigInput(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(ge=1, le=65535)
    debug: bool = Field(default=False)

@app.command()
def serve(config: ConfigInput):
    pass
```

---

## 6. Error Handling

```python
EXIT_SUCCESS = 0
EXIT_USAGE_ERROR = 1
EXIT_EXECUTION_ERROR = 2

try:
    # logic
except PermissionError:
    raise click.ClickException("Permission denied")
    sys.exit(EXIT_USAGE_ERROR)
```

---

## 7. User Experience

### 7.1 Help Text

```python
@click.command(
    help="Manage users in the system.",
    short_help="Manage users",
    epilog="Examples: %(prog)s add john"
)
```

### 7.2 Interactive Prompts

```python
name = click.prompt("Project name", type=str, default="my-project")
framework = click.prompt("Framework", type=click.Choice(["fastapi", "flask"]))
force = click.confirm("Overwrite?", default=False)
```

### 7.3 Progress Bars

```python
with click.progressbar(files, label="Downloading") as bar:
    for f in bar:
        download(f)
```

---

## 8. Output Formatting

### 8.1 Colors

```python
click.echo(click.style("Success!", fg="green"))
click.echo(click.style("Error!", fg="red", bold=True))
```

### 8.2 Tables

```python
from tabulate import tabulate

headers = ["Name", "Status"]
rows = [["alice", "active"], ["bob", "inactive"]]
click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
```

---

## 9. Configuration

```python
# Priority (highest to lowest)
# 1. Flags/args
# 2. Environment variables
# 3. Config file (~/.config/app/)
# 4. Defaults

@click.option("--config", "-c", type=click.Path())
def load_config(config):
    pass
```

---

## 10. Testing

```python
from click.testing import CliRunner

def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output
```

---

## 11. Common Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Misuse of command |
| 126 | Not executable |
| 127 | Command not found |

---

## Quick Reference

| Need | Use | NOT |
|------|-----|-----|
| Python CLI | typer (modern) | argparse (verbose) |
| Go CLI | cobra | Custom parsing |
| Rust CLI | clap | Manual |
| Node CLI | commander.js | Custom |
| Colors | click.style | ANSI codes |
| Testing | CliRunner | subprocess |

---

*For detailed examples, see full CLI design research document.*
