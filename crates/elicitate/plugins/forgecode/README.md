# Forge plugin — elicitate

This directory contains the Forgecode plugin manifest for the `elicitate`
native OS popup elicitation tool.

## Install

```bash
./install.sh /path/to/your/host-repo
```

Or, manually:

```bash
mkdir -p /path/to/your/host-repo/.forgecode/plugins/elicitate
cp plugin.toml /path/to/your/host-repo/.forgecode/plugins/elicitate/

mkdir -p /path/to/your/host-repo/.forgecode/skills
ln -s "$(pwd)/../../.elicitate/skills/elicitate" \
       /path/to/your/host-repo/.forgecode/skills/elicitate
```

Then make sure `elicitate-mcp` is on PATH (e.g., `cargo install --path
../../crates/elicitate`) and restart Forgecode.

## What this plugin does

- Registers the `elicitate_mcp` tool with Forgecode.
- Loads the `elicitate` skill so the agent knows when to invoke the tool.
- Wires up the schema so the tool's `inputSchema` / `outputSchema` is
  visible in Forgecode's tool picker.

## Verify

```bash
forgecode plugins list | grep elicitate
forgecode skills list | grep elicitate
```

## Uninstall

```bash
rm -rf /path/to/your/host-repo/.forgecode/plugins/elicitate
rm /path/to/your/host-repo/.forgecode/skills/elicitate
```