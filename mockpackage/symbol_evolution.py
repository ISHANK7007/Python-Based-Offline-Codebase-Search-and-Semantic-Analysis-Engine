from typing import List, Dict, Any, Optional


class SymbolEvolutionGenerator:
    """Generator for realistic code symbol evolutions."""

    @staticmethod
    def add_function(name: str, complexity: int = 1) -> str:
        """Generate code for a new function."""
        docs = [f'"""Function {name}."""']
        if complexity > 1:
            docs = [
                f'"""Function {name}.',
                "",
                "Args:",
                "    param1: First parameter",
                "    param2: Second parameter",
                "",
                "Returns:",
                "    Result of the operation",
                '"""'
            ]

        params = "param1, param2=None"
        if complexity > 2:
            params = "param1: str, param2: Optional[Dict[str, Any]] = None"

        body = ["    return param1"]
        if complexity > 1:
            body = [
                "    result = param1",
                "    if param2:",
                "        result = f\"{result}_{param2}\"",
                "    return result"
            ]

        lines = [f"def {name}({params}):"] + [f"    {d}" for d in docs] + body
        return "\n".join(lines)

    @staticmethod
    def add_class(name: str, methods: List[str], complexity: int = 1) -> str:
        """Generate code for a new class."""
        docs = [f'"""Class {name}."""']
        if complexity > 1:
            docs = [
                f'"""Class {name}.',
                "",
                "Attributes:",
                "    attr1: First attribute",
                "    attr2: Second attribute",
                '"""'
            ]

        lines = [f"class {name}:"] + [f"    {d}" for d in docs]

        init = [
            "    def __init__(self, attr1=None, attr2=None):",
            '        """Initialize the class."""',
            "        self.attr1 = attr1",
            "        self.attr2 = attr2"
        ]
        lines.extend(init)

        for method in methods:
            method_code = [
                f"    def {method}(self, param):",
                f'        """Method {method}."""',
                "        return param"
            ]
            if complexity > 1:
                method_code = [
                    f"    def {method}(self, param, extra=None):",
                    f'        """Method {method}.',
                    "",
                    "        Args:",
                    "            param: Parameter",
                    "            extra: Optional extra parameter",
                    "",
                    "        Returns:",
                    "            Processed parameter",
                    '        """',
                    "        if extra:",
                    "            return f\"{param}_{extra}\"",
                    "        return param"
                ]
            lines.extend(method_code)
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def modify_function(original: str, change_type: str) -> str:
        """Modify an existing function."""
        lines = original.split("\n")
        signature = lines[0]

        if change_type == "signature":
            if "=" not in signature:
                signature = signature.replace(")", ", new_param=None)")
            else:
                signature = signature.replace(")", ", new_param='default')")
            lines[0] = signature

        elif change_type == "body":
            body_start = 0
            for i, line in enumerate(lines):
                if line and not line.strip().startswith('"""'):
                    if i > 0 and "def " not in line:
                        body_start = i
                        break

            if body_start > 0:
                for i in range(body_start, len(lines)):
                    if "return" in lines[i]:
                        lines[i] = lines[i].replace("return ", "return f\"modified_{")
                        lines[i] = lines[i] + "}\""
                        break

        elif change_type == "docstring":
            in_docstring = False
            for i, line in enumerate(lines):
                if '"""' in line:
                    if not in_docstring:
                        in_docstring = True
                        if line.strip() == '"""':
                            lines[i] = lines[i] + "Modified docstring."
                        else:
                            lines[i] = lines[i].replace('"""', '"""Modified: ')
                    else:
                        in_docstring = False

        return "\n".join(lines)
