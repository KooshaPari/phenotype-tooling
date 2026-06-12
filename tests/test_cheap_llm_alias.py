import importlib
import sys
import types
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _install_fake_provider(monkeypatch):
    module_names = [
        "phenotype_ops_mcp",
        "phenotype_ops_mcp.providers",
        "phenotype_ops_mcp.providers.cheap_llm",
    ]
    for name in module_names:
        monkeypatch.delitem(sys.modules, name, raising=False)

    package = types.ModuleType("phenotype_ops_mcp")
    providers = types.ModuleType("phenotype_ops_mcp.providers")
    cheap_llm = types.ModuleType("phenotype_ops_mcp.providers.cheap_llm")
    cheap_llm.ExampleProvider = type("ExampleProvider", (), {})
    cheap_llm.DEFAULT_MODEL = "cheap-model"

    monkeypatch.setitem(sys.modules, "phenotype_ops_mcp", package)
    monkeypatch.setitem(sys.modules, "phenotype_ops_mcp.providers", providers)
    monkeypatch.setitem(sys.modules, "phenotype_ops_mcp.providers.cheap_llm", cheap_llm)
    monkeypatch.delitem(sys.modules, "cheap_llm", raising=False)
    return cheap_llm


def test_alias_reexports_provider_class(monkeypatch):
    canonical = _install_fake_provider(monkeypatch)

    alias = importlib.import_module("cheap_llm")

    assert alias.ExampleProvider is canonical.ExampleProvider


def test_alias_reexports_provider_constant(monkeypatch):
    _install_fake_provider(monkeypatch)

    alias = importlib.import_module("cheap_llm")

    assert alias.DEFAULT_MODEL == "cheap-model"
