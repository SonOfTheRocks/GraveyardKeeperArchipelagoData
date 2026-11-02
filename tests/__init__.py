"""Load the same tooling modules in standalone unittest and nested pytest runs."""
from importlib import import_module


_tool_package = __package__.rpartition(".")[0]


def _import_tool(name):
    return import_module(f"{_tool_package}.{name}" if _tool_package else name)


validation = _import_tool("validate_data")
version_check = _import_tool("check_data_version")
