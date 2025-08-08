import ast
import dataclasses
import inspect
import logging
import textwrap
import typing
from pathlib import Path

from nexosapi.api.controller import EndpointResponseType, NexosAIAPIEndpointController

from .base import StubTransformer


class ControllerDataModelsDict(typing.TypedDict):
    request_model: str
    response_model: str


@dataclasses.dataclass
class RequestMakerRewriter(StubTransformer):
    _generics: typing.ClassVar[dict[str, ControllerDataModelsDict]] = {}
    _current_controller_class: typing.ClassVar[str] = ""
    exclude_classes: set[str] = dataclasses.field(default_factory=set)

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

        transformed_tree = self.visit(tree)
        ast.fix_missing_locations(transformed_tree)

        new_code = ast.unparse(transformed_tree)
        if self.modified:
            new_code = (
                "\n".join(additional_imports or ["from __future__ import annotations", "import typing"])
                + "\n"
                + new_code
            )
            path.write_text(new_code, encoding="utf-8")
            logging.info(f"Rewrites applied to {stub_path}.")

    @staticmethod
    def get_method_ast_node(class_node, method_name):
        try:
            source = inspect.getsource(class_node)
        except Exception as e:
            logging.exception(f"Could not get source for class {class_node}", exc_info=e)
            return None

        source = textwrap.dedent(source)
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logging.exception(f"Syntax error parsing source for class {class_node}", exc_info=e)
            return None

        class_node = next(
            (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_node.__name__), None
        )
        if class_node is None:
            logging.error(f"Class {class_node.__name__} node not found in source")
            return None

        func_def = next(
            (
                node
                for node in class_node.body
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))) and node.name == method_name
            ),
            None,
        )
        if func_def is None:
            logging.error(f"Method {method_name} not found in class {class_node.__name__}")
            return None

        return func_def

    def add_original_request_manager_body(
        self, body: list[ast.stmt], data_models: dict[str, ControllerDataModelsDict] | None
    ) -> None:
        """
        Adds the original RequestMaker body to the new body of the class.

        :param body: The body of the Operations class to be added.
        :param data_models: The data models dictionary containing request and response models.
        """
        original_request_maker = NexosAIAPIEndpointController._RequestManager
        if not hasattr(original_request_maker, "__dict__"):
            logging.warning("Original RequestManager does not have a __dict__ attribute. Skipping method addition.")
            return

        # Get the original methods from the RequestManager class
        original_methods: list[ast.FunctionDef] = []
        for method_name in original_request_maker.__dict__:
            if method_name.startswith("__"):
                continue

            if callable(getattr(original_request_maker, method_name, None)):
                original_method = getattr(original_request_maker, method_name)
                logging.info(f"Adding method {method_name} from {original_request_maker.__name__}")
                variable_type_hints = typing.get_type_hints(original_method, include_extras=True)
                docstring = self._indent_docstring(original_method.__doc__, indent=12)

                func_def = self.get_method_ast_node(original_request_maker, method_name)
                if func_def is None:
                    logging.warning(f"Skipping method {method_name}, AST node not found.")
                    continue

                args_to_process = (
                    func_def.args.args[1:]
                    if func_def.args.args and func_def.args.args[0].arg == "self"
                    else func_def.args.args
                )

                compiled_arguments: list[ast.arg] = [
                    ast.arg(arg=arg_node.arg, annotation=arg_node.annotation) for arg_node in args_to_process
                ]

                return_annotation = variable_type_hints.get("return", None)
                if type(return_annotation) in [typing._GenericAlias, typing.Union, typing._UnionGenericAlias]:  # type: ignore
                    # If the return type is a Union, we need to extract the first type
                    return_annotation = typing.get_args(return_annotation)[0]

                if return_annotation.__name__ in str(EndpointResponseType):  # type: ignore
                    # If the return type is EndpointResponseType, we need to use the response model from data_models
                    if data_models:  # noqa: SIM108
                        return_annotation = data_models.get("response_model", "typing.Any")
                    else:
                        return_annotation = "typing.Any"

                serialized_return_annotation = (
                    return_annotation.__name__ if isinstance(return_annotation, type) else str(return_annotation)
                )
                if serialized_return_annotation == "_RequestManager":
                    serialized_return_annotation = (
                        f"{self._current_controller_class}.{serialized_return_annotation.removeprefix('_')}"
                    )
                returned_objects = (
                    {"returns": ast.Name(id=serialized_return_annotation, ctx=ast.Load())} if return_annotation else {}
                )

                compiled_method = ast.FunctionDef(
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
            if isinstance(stmt, ast.FunctionDef):
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
                # Change the method return type to the following type hint: "RequestManager"
                stmt.returns = ast.Name(id=f"{self._current_controller_class}.RequestManager", ctx=ast.Load())
                new_body.append(stmt)
            else:
                new_body.append(stmt)
        return new_body

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:  # noqa: N802
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

        self._current_controller_class = node.name

        # Find and remove inner class Operations
        new_request_maker_body = []
        new_endpoint_controller_body = []

        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef) and stmt.name == "Operations":
                new_request_maker_body = self.remove_request_argument_from_methods(stmt.body)
                self.modified = True
            else:
                new_endpoint_controller_body.append(stmt)

        data_models = None
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self._generics:
                data_models = self._generics[base.id]
                break

        original_request_maker_class_name = NexosAIAPIEndpointController._RequestManager.__name__
        new_request_maker_class_name = original_request_maker_class_name.removeprefix("_")
        if new_request_maker_body:
            # Construct new RequestMaker class
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
                        attr=original_request_maker_class_name,
                        ctx=ast.Load(),
                    )
                ],
                keywords=[],
                body=new_request_maker_body,
                decorator_list=[],
            )
            request_maker_type_assignment = ast.Assign(
                targets=[ast.Name(id=NexosAIAPIEndpointController.REQUEST_MANAGER_CLASS.__name__, ctx=ast.Store())],
                value=ast.Name(id=new_request_maker_class_name, ctx=ast.Load()),
            )
            request_maker_accessor_assignment = ast.Assign(
                targets=[ast.Name(id="request", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id=new_request_maker_class_name, ctx=ast.Load()),
                    args=[],
                    keywords=[],
                ),
            )

            new_endpoint_controller_body.append(request_maker_class)
            new_endpoint_controller_body.append(request_maker_type_assignment)
            new_endpoint_controller_body.append(request_maker_accessor_assignment)

        node.body = new_endpoint_controller_body
        return node
