from typing import Any, List


class HeapNode:
    def __init__(self, **fields: Any) -> None:
        self.fields = fields

    def get_child_handles(self) -> List[int]:
        return [v for v in self.fields.values() if isinstance(v, int)]


class GCHeap:
    def __init__(self) -> None:
        self.objects = {}
        self.next_handle = 1

    def allocate(self, obj: Any) -> int:
        handle = self.next_handle
        self.next_handle += 1

        self.objects[handle] = (obj, 1)

        return handle

    def incref(self, handle: int) -> None:
        if handle not in self.objects:
            return

        obj, refcount = self.objects[handle]
        self.objects[handle] = (obj, refcount + 1)

    def decref(self, handle: int) -> None:
        if handle not in self.objects:
            return

        obj, refcount = self.objects[handle]
        refcount -= 1

        if refcount > 0:
            self.objects[handle] = (obj, refcount)
            return

        if hasattr(obj, "get_child_handles"):
            child_handles = obj.get_child_handles()
        else:
            child_handles = []

        del self.objects[handle]

        for child_handle in child_handles:
            self.decref(child_handle)

    def is_alive(self, handle: int) -> bool:
        return handle in self.objects

    def live_count(self) -> int:
        return len(self.objects)
