import ast
import dataclasses
import inspect
import logging
import typing
from ast import get_docstring
from pathlib import Path

from nexosapi.api.controller import EndpointResponseType, NexosAIAPIEndpointController


class ControllerDataModelsDict(typing.TypedDict):
    request_model: str
    response_model: str


@dataclasses.dataclass
class RequestMakerRewriter(ast.NodeTransformer):
    exclude_classes: set[str] = dataclasses.field()
    modified: bool = False
    _generics: dict[str, ControllerDataModelsDict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def _indent_docstring(docstring: str) -> str:
        """
        Indents the docstring to match the indentation level of the method.

        :param docstring: The original docstring to be indented.
        :return: The indented docstring.
        """
        if not docstring:
            return ""
        lines = docstring.splitlines()
        indented_lines = [lines[0]] + [12 * " " + line for line in lines[1:]]
        return "\n".join(indented_lines)

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
                logging.info(f"[TYPES] Adding method {method_name} from {original_method.__qualname__}")
                arguments_spec = inspect.getfullargspec(original_method)
                docstring = self._indent_docstring(original_method.__doc__)
                variable_type_hints = typing.get_type_hints(original_method)
                compiled_arguments = []

                arguments_to_analyze = (
                    arguments_spec.args[1:]
                    if arguments_spec.args and arguments_spec.args[0] == "self"
                    else arguments_spec.args
                )
                for argument in arguments_to_analyze:
                    annotation = variable_type_hints.get(argument, None)
                    compiled_arguments.append(
                        ast.arg(
                            arg=argument,
                            annotation=ast.Name(id=annotation.__name__, ctx=ast.Load()) if annotation else None,
                        )
                    )

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
                    serialized_return_annotation = f'"{serialized_return_annotation.removeprefix("_")}"'
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

    @staticmethod
    def remove_request_argument_from_methods(body: list[ast.stmt]) -> list[ast.stmt]:
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
                    docstring_lines = (get_docstring(stmt) or "").splitlines()
                    new_docstring = "\n".join(line for line in docstring_lines if ":param request:" not in line)
                    logging.info(new_docstring)
                    stmt.docstring = new_docstring
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


def apply_rewrites_to_stub(stub_path: str, exclude_classes: list[str]) -> None:
    """
    Applies AST-based rewrite to replace Operations class with RequestMaker class in controllers.

    :param stub_path: Path to the Python stub file.
    :param exclude_classes: List of class names to exclude from rewriting.
    """
    path = Path(stub_path)
    if not path.exists():
        return

    content = path.read_text()
    try:
        tree = ast.parse(content)
    except SyntaxError as syntax_error_during_compilation:
        logging.exception(f"Failed to parse {stub_path}", exc_info=syntax_error_during_compilation)
        return

    transformer = RequestMakerRewriter(set(exclude_classes))
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)

    if transformer.modified:
        additional_imports = ["from __future__ import annotations", "import typing"]
        new_code = "\n".join(additional_imports) + "\n" + ast.unparse(transformed_tree)
        path.write_text(new_code, encoding="utf-8")
        logging.info(f"Rewrites applied to {stub_path}.")
