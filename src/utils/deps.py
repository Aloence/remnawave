"""Список зависимостей (по сути синглтонов), создающихся на стартапе"""

from typing import Any

DEPS = {}


def add_dep(name: type, dep: Any):
    DEPS[name] = dep


def add_deps(deps: dict):
    DEPS.update(deps)


def get_dep(name: type) -> Any:
    return DEPS.get(name)
