from typing import Dict, List, Optional

from symtable import Environment


class ActivationRecord:
    def __init__(
        self,
        function_name: str,
        parameters: Dict[str, object],
        locals_env: Environment,
        return_address: str,
        static_link: Optional["ActivationRecord"],
        dynamic_link: Optional["ActivationRecord"],
    ) -> None:
        self.function_name = function_name
        self.parameters = parameters
        self.locals_env = locals_env
        self.return_address = return_address
        self.static_link = static_link
        self.dynamic_link = dynamic_link

class CallStack:
    def __init__(self) -> None:
        self._frames = []

    def push(self, record: ActivationRecord) -> None:
        self._frames.append(record)

    def pop(self) -> ActivationRecord:
        """Remove and return the top frame."""
        return self._frames.pop()

    def current(self) -> ActivationRecord:
        return self._frames[-1]

    def trace(self) -> List[str]:
        return [
            f"{frame.function_name} -> return: {frame.return_address}"
            for frame in self._frames
        ]
