import logging
from pathlib import Path
from shutil import rmtree

from compile import compile_stubs
from rewrite import apply_rewrites_to_stub

from nexosapi.common.logging import setup_logging

STUBGEN_OUTPUT_DIR = "stubs"
FILES_TO_EXPLICITLY_REWRITE = [
    "tests/mocks.pyi",
]


def include_stubs(output: Path, src: Path, tests: Path) -> None:
    """
    Moves the generated stubs from the output directory to their corresponding location in the src directory,
    so the pyi files lay alongside the source files.

    :param output: The directory where the stubs are generated.
    :param src: The source directory where the stubs should be moved.
    :param tests: The test directory where the stubs should be moved if they are test-related.
    """
    if not output.exists():
        logging.warning(f"Stubgen output directory '{output}' does not exist. Skipping move.")
        return

    for stub_file in output.rglob("*.pyi"):
        if "tests" in str(stub_file):
            target_path = tests / stub_file.relative_to(output).relative_to("tests")
        else:
            relative_path = stub_file.relative_to(output)
            target_path = src / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        stub_file.rename(target_path)


def generate_file_tree_paths_for_directory(path: Path, prefix: str = "") -> list[str]:
    """
    Generates a list of file paths for the specified module, including all subdirectories.

    :param path: The path to the module directory for which to generate file paths.
    :param prefix: The prefix to prepend to file paths.

    :return: A list of file paths for the module.
    """
    if not path.exists() or not path.is_dir():
        raise ValueError(f"The specified path '{path}' does not exist or is not a directory.")

    return [str(f"{prefix}{file}") for file in path.rglob("*") if file.is_file()]


def remove_existing_stubs_from_file_tree(tree: list[str]) -> None:
    """
    Removes existing stub files from the file tree.

    :param tree: A list of file paths in the file tree.
    """
    for path_string in tree:
        path = Path(path_string)
        if path.suffix == ".pyi":
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    setup_logging(level=logging.INFO)
    output_dir = Path(STUBGEN_OUTPUT_DIR)
    src_dir = Path("src")
    test_dir = Path("tests")

    tests_tree = generate_file_tree_paths_for_directory(test_dir)
    sources_tree = generate_file_tree_paths_for_directory(src_dir)

    try:
        remove_existing_stubs_from_file_tree(
            [
                *tests_tree,
                *sources_tree,
            ]
        )
        compile_stubs(output_dir=output_dir)
        for stub_file_path in generate_file_tree_paths_for_directory(path=output_dir):
            if not any(file in stub_file_path for file in FILES_TO_EXPLICITLY_REWRITE):
                if any(
                    [
                        Path(stub_file_path.removesuffix(".pyi")).is_dir(),  # Skip directories
                        "__pycache__" in stub_file_path,  # Skip __pycache__ directories
                        "__init__.py" in stub_file_path,  # Skip __init__.py files
                        "/api/" not in Path(stub_file_path.removesuffix(".py")).as_posix(),  # Skip non-API files
                    ]
                ):
                    logging.debug(f"Removing stub file: {stub_file_path}")
                    Path(stub_file_path).unlink(missing_ok=True)
                    continue
            apply_rewrites_to_stub(stub_file_path, exclude_classes=["NexosAIAPIEndpointController"])
        include_stubs(output=output_dir, src=src_dir, tests=test_dir)
    except Exception as e:
        logging.exception("An error occurred during stub generation and rewriting.", exc_info=e)
    else:
        rmtree(output_dir)
