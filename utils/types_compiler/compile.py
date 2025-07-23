import ast
import dataclasses
import logging
import re
import typing
from pathlib import Path
from shutil import rmtree

import mypy.stubgen

from nexosapi.common.logging import setup_logging

STUBGEN_OUTPUT_DIR = "stubs"


@dataclasses.dataclass
class RequestMakerRewriter(ast.NodeTransformer):
    exclude_classes: set[str] = dataclasses.field()
    class_stack: list[str] = dataclasses.field(default_factory=list)
    modified: bool = False

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:  # noqa: N802
        self.class_stack.append(node.name)

        if node.name in self.exclude_classes:
            self.class_stack.pop()
            return node

        # Find and remove inner class Operations
        operations_body = None
        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef) and stmt.name == "Operations":
                operations_body = stmt.body
                self.modified = True
            else:
                new_body.append(stmt)

        if operations_body is not None:
            # Construct new RequestMaker class
            class_name = node.name
            request_maker_class = ast.ClassDef(
                name="RequestMaker",
                bases=[
                    ast.Attribute(value=ast.Name(id=class_name, ctx=ast.Load()), attr="_RequestMaker", ctx=ast.Load())
                ],
                keywords=[],
                body=operations_body,
                decorator_list=[],
            )
            request_maker_assignment = ast.Assign(
                targets=[ast.Name(id="REQUEST_MAKER_CLASS", ctx=ast.Store())],
                value=ast.Name(id="RequestMaker", ctx=ast.Load()),
            )

            new_body.append(request_maker_class)
            new_body.append(request_maker_assignment)

        node.body = new_body
        self.class_stack.pop()
        return node


class RewriteDefinition(typing.TypedDict):
    description: str
    target: str
    replacement: str
    exclude: dict[str, list[str]]


def generate_file_tree_paths_for_directory(path: str) -> list[str]:
    """
    Generates a list of file paths for the specified module, including all subdirectories.

    :param path: The path to the module directory for which to generate file paths.
    :return: A list of file paths for the module.
    """
    module_path = Path(path)
    if not module_path.exists() or not module_path.is_dir():
        raise ValueError(f"The specified path '{path}' does not exist or is not a directory.")

    return [str(file) for file in module_path.rglob("*") if file.is_file()]


def apply_rewrites_to_stub(stub_path: str, exclude_classes: list[str]) -> None:
    """
    Applies AST-based rewrite to replace Operations class with RequestMaker class in controllers.

    :param stub_path: Path to the Python stub file.
    :param exclude_classes: List of class names to exclude from rewriting.
    """
    path = Path(stub_path)
    if not path.exists():
        logging.warning(f"Stub file {stub_path} does not exist. Skipping rewrite.")
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
        new_code = ast.unparse(transformed_tree)
        path.write_text(new_code, encoding="utf-8")
        logging.info(f"Rewrites applied to {stub_path}.")
    else:
        logging.info(f"No rewrites applied to {stub_path}.")


def generate_stubs_for_module() -> None:
    """
    Generates type stubs for the current project and saves them to the given output directory.
    """
    mypy.stubgen.main(["src", "-o", STUBGEN_OUTPUT_DIR, "--include-docstrings"])
    mypy.stubgen.main(["tests", "-o", STUBGEN_OUTPUT_DIR, "--include-docstrings"])


def move_stubs_to_src() -> None:
    """
    Moves the generated stubs from the output directory to their corresponding location in the src directory,
    so the pyi files lay alongside the source files.
    """
    output_dir = Path(STUBGEN_OUTPUT_DIR)
    src_dir = Path("src")
    test_dir = Path("tests")

    if not output_dir.exists():
        logging.warning(f"Stubgen output directory '{output_dir}' does not exist. Skipping move.")
        return

    for stub_file in output_dir.rglob("*.pyi"):
        relative_path = stub_file.relative_to(output_dir)
        target_path = src_dir / relative_path

        if "tests" in str(relative_path):
            target_path = test_dir / relative_path.relative_to("tests")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        stub_file.rename(target_path)
        logging.info(f"Moved stub {stub_file} to {target_path}.")


if __name__ == "__main__":
    setup_logging(level=logging.INFO)
    generate_stubs_for_module()
    file_tree = generate_file_tree_paths_for_directory(STUBGEN_OUTPUT_DIR)
    for stub_file_path in file_tree:
        if stub_file_path.endswith(".pyi"):
            if any(
                [
                    Path(stub_file_path.removesuffix(".pyi")).is_dir(),  # Skip directories
                    re.match("(.*)test_(.*).pyi", stub_file_path),  # Skip test files
                ]
            ):
                Path(stub_file_path).unlink(missing_ok=True)
            apply_rewrites_to_stub(stub_file_path, exclude_classes=["NexosAIEndpointController"])
    move_stubs_to_src()
    rmtree(STUBGEN_OUTPUT_DIR)
