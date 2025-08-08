import ast
import importlib
import logging
import typing
from pathlib import Path

from .base import StubTransformer


class DomainModelsDictionariesWriter(StubTransformer):
    exclude_classes: typing.ClassVar[set[str]] = set()

    def __init__(self) -> None:
        super().__init__()
        self.domain_model_stubs: list[Path] = []
        self.modified = False
        self.domain_models_root: Path | None = None

    @staticmethod
    def get_domain_model_stubs(domain_models_path: str) -> list[Path]:
        domain_model_stubs_dir = Path(domain_models_path)
        if not domain_model_stubs_dir.exists():
            logging.warning(f"Domain models directory {domain_models_path} does not exist.")
            return []

        domain_model_stubs = list(domain_model_stubs_dir.glob("*.pyi"))
        if not domain_model_stubs:
            logging.warning(f"No Python stub files found in the domain models directory {domain_models_path}.")
            return []

        domain_model_stubs = [stub for stub in domain_model_stubs if stub.name not in {"__init__.pyi", "base.pyi"}]
        if not domain_model_stubs:
            logging.warning("No valid domain model stubs found after filtering.")
            return []
        return domain_model_stubs

    def run_rewrites(self, *_: typing.Any, **kwargs: typing.Any) -> None:
        domain_models_path = kwargs.get("domain_models_path")
        extra_paths = kwargs.get("extra_paths", "")
        if not domain_models_path:
            logging.error("Domain models path is not provided. Cannot apply rewrites.")
            return
        if not isinstance(domain_models_path, str):
            logging.error("Domain models path must be a string. Cannot apply rewrites.")
            return

        self.domain_models_root = Path(domain_models_path)
        self.domain_model_stubs = self.get_domain_model_stubs(domain_models_path)
        if not self.domain_model_stubs:
            logging.warning("No domain model stubs found to apply rewrites.")
            return

        self.domain_model_stubs.extend([Path(domain_models_path.split("/")[0] + f"/{file}") for file in extra_paths])

        for stub in self.domain_model_stubs:
            changed = self._process_stub_file(stub)
            if changed:
                logging.info(f"Updated TypedDicts in {stub}")

    def _process_stub_file(self, stub: Path) -> bool:
        content = stub.read_text(encoding="utf-8")
        models = self.extract_base_models_definitions(content)
        models = {k: v for k, v in models.items() if k not in self.exclude_classes}

        mapping = set(models.keys())
        typed_dicts_src = self._generate_typed_dicts_src(models, mapping, use_qualified_names=True)

        new_content = content.rstrip()
        for td_src in typed_dicts_src:
            if td_src not in content:
                new_content += "\n\n" + td_src

        if new_content != content:
            stub.write_text(new_content, encoding="utf-8")
            self.modified = True
            return True

        return False

    def rewrite_type_annotation(self, node: ast.expr, basemodel_names: set[str]) -> ast.expr:
        # If simple name and in basemodel_names, replace with TypedDict name
        if isinstance(node, ast.Name):
            if node.id in basemodel_names:
                return ast.Name(id=node.id + "Data", ctx=ast.Load())
            return node

        # Handle qualified names like module.ModelName
        if isinstance(node, ast.Attribute):
            # Check if the attribute name is in basemodel_names and replace just the attr
            if node.attr in basemodel_names:
                return ast.Attribute(value=node.value, attr=node.attr + "Data", ctx=ast.Load())
            return node

        # Recursively rewrite for subscripts, tuples, unions, annotated
        if isinstance(node, ast.Subscript):
            node.value = self.rewrite_type_annotation(node.value, basemodel_names)
            if isinstance(node.slice, ast.Tuple):
                node.slice.elts = [self.rewrite_type_annotation(e, basemodel_names) for e in node.slice.elts]
            else:
                node.slice = self.rewrite_type_annotation(node.slice, basemodel_names)
            return node

        if isinstance(node, ast.Tuple):
            node.elts = [self.rewrite_type_annotation(e, basemodel_names) for e in node.elts]
            return node

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            node.left = self.rewrite_type_annotation(node.left, basemodel_names)
            node.right = self.rewrite_type_annotation(node.right, basemodel_names)
            return node

        if isinstance(node, ast.Subscript) and (
            (isinstance(node.value, ast.Name) and node.value.id == "Annotated")
            or (isinstance(node.value, ast.Attribute) and node.value.attr == "Annotated")
        ):
            slice_value = node.slice
            if isinstance(slice_value, ast.Tuple):
                original_type = slice_value.elts[0]
                slice_value.elts[0] = self.rewrite_type_annotation(original_type, basemodel_names)
            else:
                node.slice = self.rewrite_type_annotation(slice_value, basemodel_names)
            return node

        return node

    def _generate_typed_dicts_src(
        self,
        models: dict[str, list[tuple[str, bool]]],
        basemodel_names: set[str],
        use_qualified_names: bool = False,
    ) -> list[str]:
        typed_dicts_src = []

        not_required = "typing.NotRequired" if use_qualified_names else "NotRequired"
        typed_dict = "typing.TypedDict" if use_qualified_names else "TypedDict"
        any_type = "typing.Any" if use_qualified_names else "Any"

        for model_name, fields in models.items():
            td_name = f"{model_name}Data"

            lines = [f"class {td_name}({typed_dict}):"]

            if not fields:
                lines.append("    pass")
            else:
                for field_name, is_optional in fields:
                    annotation_str = self._get_field_annotation_as_string(model_name, field_name)
                    if annotation_str is None:
                        annotation_code = any_type
                    else:
                        try:
                            ann_tree = ast.parse(annotation_str, mode="eval")
                            ann_tree.body = self.rewrite_type_annotation(ann_tree.body, basemodel_names)
                            annotation_code = ast.unparse(ann_tree.body)
                        except Exception as e:  # noqa: BLE001
                            logging.warning(
                                f"Failed to parse/transform annotation for {field_name} in {model_name}: {e}"
                            )
                            annotation_code = any_type

                    if is_optional:
                        annotation_code = f"{not_required}[{annotation_code}]"
                    lines.append(f"    {field_name}: {annotation_code}")

            typed_dicts_src.append("\n".join(lines))

        return typed_dicts_src

    def _get_field_annotation_as_string(self, model_name: str, field_name: str) -> str | None:
        for stub in self.domain_model_stubs:
            content = stub.read_text(encoding="utf-8")
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == model_name:
                    for stmt in node.body:
                        if (
                            isinstance(stmt, ast.AnnAssign)
                            and isinstance(stmt.target, ast.Name)
                            and stmt.target.id == field_name
                        ):
                            if stmt.annotation:
                                return ast.unparse(stmt.annotation)
        return None

    @staticmethod
    def extract_base_models_definitions(content: str) -> dict[str, list[tuple[str, bool]]]:
        class_definitions = {}
        try:
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    if any(
                        isinstance(base, ast.Name)
                        and base.id in {"BaseModel", "NullableBaseModel", "NexosAPIRequest", "NexosAPIResponse"}
                        for base in node.bases
                    ):
                        fields = []

                        for stmt in node.body:
                            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                                field_name = stmt.target.id

                                # Default: optional if assigned a value (like None)
                                is_optional = stmt.value is not None

                                # Also check annotation for Optional/Union[..., None]
                                if stmt.annotation is not None:
                                    # Define helper to check if NoneType is in annotation
                                    def annotation_contains_none(node: ast.AST) -> bool:
                                        # Check for Subscript (like Optional[X] or Union[X, None])
                                        if isinstance(node, ast.Subscript):
                                            # For Python 3.9+: node.slice is expr
                                            slice_val = node.slice
                                            # For Union or Optional, check args
                                            if isinstance(slice_val, ast.Tuple):
                                                return any(annotation_contains_none(elt) for elt in slice_val.elts)
                                            # We check slice value recursively too
                                            return annotation_contains_none(slice_val)
                                        if isinstance(node, ast.Name):
                                            # If name is 'None' or 'NoneType'
                                            return node.id in {"None", "NoneType"}
                                        if isinstance(node, ast.Constant):
                                            # For literals
                                            return node.value is None
                                        if isinstance(node, ast.Attribute):
                                            # For typing.NoneType (unlikely, but just in case)
                                            return node.attr == "NoneType"
                                        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                                            # PEP 604 Union types: X | None
                                            return annotation_contains_none(node.left) or annotation_contains_none(
                                                node.right
                                            )
                                        if isinstance(node, ast.Tuple):
                                            return any(annotation_contains_none(elt) for elt in node.elts)
                                        return False

                                    if annotation_contains_none(stmt.annotation):
                                        is_optional = True

                                fields.append((field_name, is_optional))
                        class_definitions[node.name] = fields
        except SyntaxError as e:
            logging.exception("Syntax error parsing stub file", exc_info=e)
        return class_definitions

    def _module_path_for_stub(self, stub_path: Path) -> str:
        if not self.domain_models_root:
            logging.error("Domain models root is not set. Cannot compute module path.")
            return ""
        try:
            relative_path = stub_path.relative_to(self.domain_models_root)
        except ValueError:
            relative_path = stub_path
        module_path = relative_path.with_suffix("").as_posix().replace("/", ".")
        return f"nexosapi.domain.{module_path}"

    def build_basemodel_to_typeddict_map(self) -> dict[str, tuple[str, str]]:
        """
        Returns dict mapping:
          DomainModelName -> (TypedDictName, module_path)

        where module_path is the Python import path of the stub file containing the model.
        """
        mapping: dict[str, tuple[str, str]] = {}
        if not self.domain_model_stubs:
            logging.warning("Domain model stubs list is empty, cannot build mapping.")
            return mapping

        for stub in self.domain_model_stubs:
            content = stub.read_text(encoding="utf-8")
            models = self.extract_base_models_definitions(content)
            module_path = self._module_path_for_stub(stub)
            try:
                importlib.import_module(module_path)
            except ImportError:
                module_path = ""

            for model_name in models:
                if model_name not in self.exclude_classes:
                    typed_dict_name = f"{model_name}Data"
                    mapping[model_name] = (typed_dict_name, module_path)

        return mapping


class BindModelTypeTransformer(StubTransformer):
    models_map: typing.ClassVar[dict[str, tuple[str, str]]] = {}

    def __init__(self) -> None:
        super().__init__()
        self._parent_map: dict[ast.AST, ast.AST] = {}

    def visit(self, node: ast.AST) -> ast.AST:
        # populate parent pointers for upward navigation
        for child in ast.iter_child_nodes(node):
            self._parent_map[child] = node
        return super().visit(node)

    def run_rewrites(self, *_: typing.Any, **kwargs: typing.Any) -> None:
        stubs_tree = kwargs.get("stubs_tree")
        models_map = kwargs.get("models")

        if not stubs_tree or not models_map:
            logging.error("Stubs directory or models map is not provided. Cannot apply rewrites.")
            return

        if not isinstance(models_map, dict):
            logging.error("Models map must be a dictionary. Cannot apply rewrites.")
            return

        self.models_map = models_map

        for stub_path in map(Path, stubs_tree):
            if not stub_path.is_file():
                continue

            if "/api/controller" in stub_path.as_posix():
                continue

            content = stub_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            self.modified = False
            self._parent_map.clear()
            self.visit(tree)  # populate parent map

            # Recursively process all classes and functions
            self._process_node_recursive(tree)

            if self.modified:
                new_content = ast.unparse(tree)
                new_content = self._insert_imports(new_content)
                stub_path.write_text(new_content, encoding="utf-8")
                logging.info("Updated %s", stub_path)

    def _process_node_recursive(self, node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._process_annotated_param_bind(node)
            self._process_annotated_return_bind(node)  # <-- NEW: handle return annotations

        if isinstance(node, (ast.ClassDef, ast.Module)):
            for child in node.body:
                self._process_node_recursive(child)

    def _process_annotated_param_bind(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for arg in node.args.args + node.args.kwonlyargs:
            ann = arg.annotation
            if ann is None:
                continue
            model_name = self._find_bind_model_in_annotation(ann)
            if model_name is None:
                continue

            hint_name = self._resolve_hint_name_from_model_ref(node, model_name)

            arg.annotation = ast.Name(id=hint_name, ctx=ast.Load())
            self.modified = True

    def _process_annotated_return_bind(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        ret_ann = node.returns
        if ret_ann is None:
            return

        model_name = self._find_bind_model_in_annotation(ret_ann)
        if model_name is None:
            return

        hint_name = self._resolve_hint_name_from_model_ref(node, model_name)
        node.returns = ast.Name(id=hint_name, ctx=ast.Load())
        self.modified = True

    @staticmethod
    def _find_bind_model_in_annotation(ann_node: ast.AST) -> str | None:  # noqa: PLR0912
        for sub in ast.walk(ann_node):
            if isinstance(sub, ast.Subscript):
                val = sub.value
                name = None
                if isinstance(val, ast.Name):
                    name = val.id
                elif isinstance(val, ast.Attribute):
                    name = val.attr
                elif isinstance(val, ast.Subscript) and isinstance(val.value, ast.Name):
                    name = val.value.id

                if name not in ("Annotated", "typing.Annotated"):
                    continue

                s = sub.slice
                elts = []
                if isinstance(s, ast.Tuple):
                    elts = s.elts
                elif hasattr(s, "value") and isinstance(s.value, ast.Tuple):
                    elts = s.value.elts
                else:
                    elts = [s] if not (hasattr(s, "value") and isinstance(s.value, ast.Tuple)) else s.value.elts

                if len(elts) >= 2:  # noqa: PLR2004
                    metas = elts[1:]
                    for m in metas:
                        if isinstance(m, ast.Constant) and isinstance(m.value, str):
                            txt = m.value
                            if txt.startswith("model:"):
                                _, model_name = txt.split(":", 1)
                                model_name = model_name.strip()
                                if model_name:
                                    return model_name
        return None

    def _resolve_hint_name_from_model_ref(self, func_node: ast.AST, model_name: str) -> str:
        if model_name in {"EndpointResponseType", "EndpointRequestType"}:
            base_model = self._find_base_model_from_parent_class(func_node, model_name)
            if base_model:
                typed_dict_name, _module = self.models_map.get(base_model, (base_model + "Data", ""))
                return typed_dict_name
            return model_name
        typed_dict_name, _module = self.models_map.get(model_name, (model_name, ""))
        return typed_dict_name

    def _find_base_model_from_parent_class(self, node: ast.AST, model_name: str) -> str | None:
        top_class = self._get_top_parent_class(node)
        if top_class is None:
            return None

        target_attr = "response_model" if model_name == "EndpointResponseType" else "request_model"
        for stmt in top_class.body:
            if isinstance(stmt, ast.AnnAssign):
                if isinstance(stmt.target, ast.Name) and stmt.target.id == target_attr and stmt.annotation is not None:
                    return self._extract_model_name_from_annotation(stmt.annotation)
            if isinstance(stmt, ast.Assign):
                if (
                    len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id == target_attr
                ):
                    return self._extract_model_name_from_annotation(stmt.value)
        return None

    @staticmethod
    def _extract_model_name_from_annotation(annotation_node: ast.AST) -> str | None:
        if isinstance(annotation_node, ast.Name):
            return annotation_node.id
        if isinstance(annotation_node, ast.Attribute):
            return annotation_node.attr
        return None

    def _get_top_parent_class(self, node: ast.AST) -> ast.ClassDef | None:
        current = node
        last_class = None
        while current in self._parent_map:
            parent = self._parent_map[current]
            if isinstance(parent, ast.ClassDef):
                last_class = parent
            current = parent
        return last_class

    def _insert_imports(self, content: str) -> str:
        """
        Insert import statements for TypedDicts that were referenced in models_map,
        grouped by module_path. This assumes models_map has shape:
          model_name -> (TypedDictName, module_path)
        """
        # Collect used TypedDict names and their modules from the rewritten content
        used_typed_dicts: dict[str, set[str]] = {}  # module_path -> set of TypedDictNames

        for typed_dict_name, module_path in self.models_map.values():
            if typed_dict_name in content:
                used_typed_dicts.setdefault(module_path, set()).add(typed_dict_name)

        if not used_typed_dicts:
            return content  # no imports to add

        # Find existing import statements start position or insert at top
        lines = content.splitlines()
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith(("import", "from")):
                insert_pos = i + 1

        import_lines = []
        for module_path, typed_dict_names in used_typed_dicts.items():
            # skip empty module_path (means unknown or local)
            if not module_path:
                continue
            names = ", ".join(sorted(typed_dict_names))
            import_lines.append(f"from {module_path} import {names}")

        if not import_lines:
            return content

        # Insert imports after last import or at top
        new_lines = lines[:insert_pos] + import_lines + [""] + lines[insert_pos:]
        return "\n".join(new_lines)
