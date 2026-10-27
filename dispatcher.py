from typing import Dict, Optional, Protocol


class MethodLike(Protocol):
    def call(self, args: list, caller_env) -> object:
        """PA 7 Closure-compatible call interface."""


class ClassDecl:
    """Given: a minimal class declaration -- just a name and its own (non-inherited) methods."""

    __slots__ = ("name", "methods")

    def __init__(self, name: str, methods: Dict[str, MethodLike]) -> None:
        self.name = name
        self.methods = methods  # methods declared on THIS class only


class VTable:
    def __init__(self, entries: Dict[str, MethodLike], owning_class_name: str = "?") -> None:
        self.entries = entries
        self.owning_class_name = owning_class_name

    def resolve(self, method_name: str) -> MethodLike:
        if method_name not in self.entries:
            raise AttributeError(
                f"Class '{self.owning_class_name}' has no method '{method_name}'"
            )

        return self.entries[method_name]


def build_vtable(class_node: ClassDecl, parent_vtable: Optional[VTable] = None) -> VTable:
    if parent_vtable is None:
        entries = {}
    else:
        entries = parent_vtable.entries.copy()

    entries.update(class_node.methods)

    return VTable(entries, class_node.name)


class USIObject:
    def __init__(self, class_descriptor: VTable, fields: dict) -> None:
        self.class_descriptor = class_descriptor
        self.fields = fields


def dispatch(obj: USIObject, method_name: str, args: list, caller_env) -> object:
    resolved_method = obj.class_descriptor.resolve(method_name)
    return resolved_method.call([obj, *args], caller_env)
