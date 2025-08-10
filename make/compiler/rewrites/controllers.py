import ast
import dataclasses
import inspect
import logging
import textwrap
import typing
from pathlib import Path

from nexosapi.api.controller import EndpointRequestType, EndpointResponseType, NexosAIAPIEndpointController

from .base import StubTransformer


class ControllerDataModelsDict(typing.TypedDict):
    request_model: str
    response_model: str


RequestModelGenericName = str(EndpointRequestType.__name__)
ResponseModelGenericName = str(EndpointResponseType.__name__)

EndpointControllerClass = NexosAIAPIEndpointController
OperationsTemporaryMixingClass = EndpointControllerClass.Operations
RequestManagerNestedClass = EndpointControllerClass._RequestManager


@dataclasses.dataclass
class RequestMakerRewriter(StubTransformer):
    DEFAULT_ADDITIONAL_IMPORTS: typing.ClassVar[list[str]] = ["from __future__ import annotations", "import typing"]

    _generics: dict[str, ControllerDataModelsDict] = dataclasses.field(default_factory=dict, init=False)
    _current_controller_class: str = dataclasses.field(default_factory=str, init=False)
    exclude_classes: set[str] = dataclasses.field(default_factory=set, init=False)

    def run_rewrites(self, **kwargs: typing.Any) -> None:
        exclude_classes = kwargs.get("exclude_classes")
        additional_imports = kwargs.get("additional_imports", [])
        stub_path = kwargs.get("stub_path")

        if any(
            [
                not isinstance(exclude_classes, (list, set)),
                not isinstance(additional_imports, (list, set)),
                not isinstance(stub_path, str),
            ]
        ):
            raise TypeError("Invalid types for exclude_classes, additional_imports, or stub_path.")

        self.exclude_classes = set(exclude_classes or [])
        path = Path(stub_path)  # type: ignore
        if not path.exists():
            return

        content = path.read_text()

        try:
            tree = ast.parse(content)
        except SyntaxError as syntax_error_during_compilation:
            logging.exception(f"Failed to parse {stub_path}", exc_info=syntax_error_during_compilation)
            return

        self._current_controller_class = ""
        transformed_tree = self.visit(tree)
        ast.fix_missing_locations(transformed_tree)

        imports_to_inject = [
            import_statement
            for import_statement in (additional_imports or self.DEFAULT_ADDITIONAL_IMPORTS)
            if import_statement not in content
        ]

        new_code = ast.unparse(transformed_tree)
        if self.modified:
            new_code = "\n".join(imports_to_inject) + "\n" + new_code
            path.write_text(new_code, encoding="utf-8")
            logging.info(f"Rewrites applied to {stub_path}.")

    @staticmethod
    def get_method_ast_node(
        input_class: type | None, method_name: str
    ) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
        if input_class is None:
            return None

        try:
            class_source_code = inspect.getsource(input_class)
        except Exception as e:
            logging.exception(f"Could not get source for class {input_class}", exc_info=e)
            return None

        sanitized_class_source = textwrap.dedent(class_source_code)
        try:
            tree = ast.parse(sanitized_class_source)
        except SyntaxError as e:
            logging.exception(f"Syntax error parsing source for class {input_class}", exc_info=e)
            return None

        nested_class_node = next(
            (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == input_class.__name__), None
        )
        if nested_class_node is None:
            logging.error("Class node not found in source")
            return None

        found_definition_of_function = next(
            (
                node
                for node in nested_class_node.body
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))) and node.name == method_name
            ),
            None,
        )
        if found_definition_of_function is None:
            logging.error(f"Method {method_name} not found in class {input_class.__name__}")
            return None

        return found_definition_of_function

    def add_original_request_manager_body(
        self, body: list[ast.stmt], data_models: dict[str, ControllerDataModelsDict] | None
    ) -> None:
        """
        Adds the original RequestManager body to the new body of the class.

        :param body: The body of the Operations class to be added.
        :param data_models: The data models dictionary containing request and response models.
        """
        if not hasattr(RequestManagerNestedClass, "__dict__"):
            logging.warning("Original RequestManager does not have a __dict__ attribute. Skipping method addition.")
            return

        # Get the original methods from the RequestManager class
        original_methods: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        for method_name in RequestManagerNestedClass.__dict__:
            if method_name.startswith("__"):
                continue

            if callable(getattr(RequestManagerNestedClass, method_name, None)):
                original_method = getattr(RequestManagerNestedClass, method_name)
                logging.debug(f"Adding method {method_name} from {RequestManagerNestedClass.__name__}")
                variable_type_hints = typing.get_type_hints(original_method, include_extras=True)
                docstring = self._indent_docstring(original_method.__doc__, indent=12)

                found_definition_of_function = self.get_method_ast_node(RequestManagerNestedClass, method_name)
                if found_definition_of_function is None:
                    logging.warning(f"Skipping method {method_name}, AST node not found.")
                    continue

                self._add_typing_override_decorator_to_function(found_definition_of_function)

                args_to_process = (
                    found_definition_of_function.args.args[1:]
                    if found_definition_of_function.args.args
                    and found_definition_of_function.args.args[0].arg == "self"
                    else found_definition_of_function.args.args
                )

                compiled_arguments: list[ast.arg] = [
                    ast.arg(arg=arg_node.arg, annotation=arg_node.annotation) for arg_node in args_to_process
                ]

                return_annotation = variable_type_hints.get("return", None)
                if type(return_annotation) in [typing._GenericAlias, typing.Union, typing._UnionGenericAlias]:  # type: ignore
                    # If the return type is a Union, we need to extract the first type
                    return_annotation = typing.get_args(return_annotation)[0]

                if return_annotation is None:
                    return_annotation = typing.Any

                if return_annotation.__name__ in str(EndpointResponseType):
                    # If the return type is EndpointResponseType, we need to use the response model from data_models
                    if data_models:  # noqa: SIM108
                        return_annotation = data_models.get("response_model", typing.Any)
                    else:
                        return_annotation = "typing.Any"

                serialized_return_annotation = (
                    return_annotation.__name__ if isinstance(return_annotation, type) else str(return_annotation)
                )
                if serialized_return_annotation == RequestManagerNestedClass.__name__:
                    serialized_return_annotation = (
                        f"{self._current_controller_class}.{serialized_return_annotation.removeprefix('_')}"
                    )
                returned_objects = (
                    {"returns": ast.Name(id=serialized_return_annotation, ctx=ast.Load())} if return_annotation else {}
                )

                is_function_async = ast.AsyncFunctionDef.__name__ in found_definition_of_function.__class__.__name__
                method_compiler_class = ast.AsyncFunctionDef if is_function_async else ast.FunctionDef

                compiled_method = method_compiler_class(
                    name=method_name,
                    args=ast.arguments(
                        args=[ast.arg(arg="self", annotation=None), *compiled_arguments],
                    ),
                    body=[ast.Pass() if not docstring else ast.Expr(value=ast.Constant(value=docstring))],
                    decorator_list=[],
                    **returned_objects,  # type: ignore
                )

                original_methods.append(compiled_method)

        # Add the original methods to the new body
        for method in original_methods:
            if method.name not in body:
                body.append(method)

    def remove_request_argument_from_methods(self, body: list[ast.stmt]) -> list[ast.stmt]:
        """
        Removes the 'request' argument from all methods in the Operations class.

        :param body: The body of the Operations class.
        :return: The modified body with 'request' argument removed from methods.
        """
        new_body: list[ast.stmt] = []
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Remove 'request' argument if it exists
                new_args = [arg for arg in stmt.args.args if arg.arg != "request"]
                stmt.args.args = new_args
                if hasattr(stmt, "__doc__") and stmt.__doc__:
                    # Remove :param definition for 'request' in the docstring
                    docstring_lines = (ast.get_docstring(stmt) or "").splitlines()
                    new_docstring_content = "\n".join(line for line in docstring_lines if ":param request:" not in line)
                    new_docstring = self._indent_docstring(new_docstring_content, indent=12)
                    new_docstring_expr = ast.Expr(value=ast.Constant(value=new_docstring))
                    stmt.body[0] = new_docstring_expr
                stmt.returns = ast.Name(
                    id=f"{self._current_controller_class}.{RequestManagerNestedClass.__name__.removeprefix('_')}",
                    ctx=ast.Load(),
                )
                new_body.append(stmt)
            else:
                new_body.append(stmt)
        return new_body

    def _add_typing_override_decorator_to_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """
        Adds a typing override decorator to the function if it has a return type annotation.

        :param node: The function node to modify.
        """
        decorator_id = "typing.override"
        if any([decorator.id == decorator_id for decorator in node.decorator_list if isinstance(decorator, ast.Name)]):
            return

        decorator = ast.Name(id=decorator_id, ctx=ast.Load())
        node.decorator_list.append(decorator)

    def rewrite_function_parameters(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
        if node.name.startswith("__"):
            return node

        if self._current_controller_class:
            models = self._generics.get(self._current_controller_class)
            if models:
                possible_prefixes = ["", "_", "~_"]
                models_mapping = {
                    **{f"{prefix}{RequestModelGenericName}": models["request_model"] for prefix in possible_prefixes},
                    **{f"{prefix}{ResponseModelGenericName}": models["response_model"] for prefix in possible_prefixes},
                }

                def replace_annotation(ann: ast.expr) -> ast.expr:
                    if isinstance(ann, ast.BinOp):
                        for side in ["left", "right"]:
                            part = getattr(ann, side)
                            if not isinstance(part, ast.Name):
                                continue
                            if part.id in models_mapping:
                                setattr(ann, side, ast.Name(id=models_mapping[part.id], ctx=ast.Load()))
                    if isinstance(ann, ast.Name):
                        if ann.id in models_mapping:
                            return ast.Name(id=models_mapping[ann.id], ctx=ast.Load())
                    elif isinstance(ann, ast.Subscript):
                        ann.value = replace_annotation(ann.value)
                        if isinstance(ann.slice, ast.AST):
                            ann.slice = replace_annotation(ann.slice)
                    return ann

                # Replace return annotation
                if node.returns:
                    node.returns = replace_annotation(node.returns)
                # Replace argument annotations
                for arg in node.args.args + node.args.kwonlyargs:
                    if arg.annotation:
                        arg.annotation = replace_annotation(arg.annotation)
                for arg in [node.args.vararg, node.args.kwarg]:  # type: ignore
                    if arg and arg.annotation:
                        arg.annotation = replace_annotation(arg.annotation)

        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self.rewrite_function_parameters(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self.rewrite_function_parameters(node)

    @staticmethod
    def get_model_assignment_info(assign_node: ast.Assign) -> tuple[str, ...] | None:
        """Return (model_type, assigned_type_name) if this is a request/response_model assignment."""
        # Step 1: check the left-hand side (target)
        if not assign_node.targets:
            return None

        target = assign_node.targets[0]
        if not isinstance(target, ast.Name):
            return None

        target_name = target.id
        if target_name not in ("request_model", "response_model"):
            return None

        # Step 2: extract RHS type name
        def extract_name(node: ast.expr) -> str:
            """Extract a dotted name from an AST node."""
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Attribute):
                # recursively handle a.b.c
                return extract_name(node.value) + "." + node.attr
            if isinstance(node, ast.Subscript):
                # handle something like List[SomeType]
                return extract_name(node.value)
            return ""

        assigned_type_name = extract_name(assign_node.value)
        return (target_name, assigned_type_name)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:  # noqa: N802
        type_params = node.__dict__.get("type_params")
        if type_params and node.name != NexosAIAPIEndpointController.__name__:
            # If the class has type parameters, store them for later use
            request_model, response_model = type_params
            self._generics[node.name] = ControllerDataModelsDict(
                request_model=request_model.__dict__["name"],
                response_model=response_model.__dict__["name"],
            )

        if node.name in self.exclude_classes:
            return node

        is_controller_subclass = any(
            (isinstance(base, ast.Name) and base.id == EndpointControllerClass.__name__)
            or (isinstance(base, ast.Attribute) and base.attr == EndpointControllerClass.__name__)
            for base in node.bases
        )

        if is_controller_subclass:
            self._current_controller_class = node.name
            # Get request/response model names from class vars if present
            found_models: dict[str, str | None] = {"request_model": None, "response_model": None}
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                    assignment_info = self.get_model_assignment_info(stmt)
                    if assignment_info is None:
                        continue
                    (assignee, assignment) = assignment_info
                    if assignee and assignment:
                        found_models[assignee] = assignment or "typing.Any"

            self._generics[node.name] = ControllerDataModelsDict(
                request_model=found_models.get("request_model") or "typing.Any",
                response_model=found_models.get("response_model") or "typing.Any",
            )

        self._is_current_controller = is_controller_subclass

        # Find and remove inner class Operations
        new_request_maker_body = []
        new_endpoint_controller_body = []

        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef) and stmt.name == OperationsTemporaryMixingClass.__name__:
                new_request_maker_body = self.remove_request_argument_from_methods(stmt.body)
                self.modified = True
            else:
                new_endpoint_controller_body.append(stmt)

        data_models = None
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self._generics:
                data_models = self._generics[base.id]
                break

        new_request_maker_class_name = RequestManagerNestedClass.__name__.removeprefix("_")
        if new_request_maker_body:
            self.add_original_request_manager_body(
                new_request_maker_body,
                data_models,  # type: ignore
            )
            class_name = node.name
            request_maker_class = ast.ClassDef(
                name=new_request_maker_class_name,
                bases=[
                    ast.Attribute(
                        value=ast.Name(id=class_name, ctx=ast.Load()),
                        attr=RequestManagerNestedClass.__name__,
                        ctx=ast.Load(),
                    )
                ],
                keywords=[],
                body=new_request_maker_body,
                decorator_list=[],
            )
            request_maker_accessor_assignment = ast.AnnAssign(
                target=ast.Name(id="request", ctx=ast.Store()),
                annotation=ast.Name(id=f"{node.name}.{new_request_maker_class_name}", ctx=ast.Load()),
                value=None,
                simple=1,
            )

            new_endpoint_controller_body.append(request_maker_class)
            new_endpoint_controller_body.append(request_maker_accessor_assignment)

        node.body = new_endpoint_controller_body
        return self.generic_visit(node)
