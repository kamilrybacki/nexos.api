import logging
from pathlib import Path
from shutil import rmtree

from compile import compile_initial_stubs
from rewrites.controllers import RequestMakerRewriter
from rewrites.models import BindModelTypeTransformer, DomainModelsDictionariesWriter

from nexosapi.common.logging import setup_logging

STUBGEN_OUTPUT_DIR = "stubs"
FILES_TO_EXPLICITLY_REWRITE = [
    "tests/mocks.pyi",
    "nexosapi/api/endpoints/__init__.pyi",
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


def remove_stub_if_not_needed(file_path: str) -> bool:
    if not any(file in file_path for file in FILES_TO_EXPLICITLY_REWRITE):
        if any(
            [
                Path(file_path.removesuffix(".pyi")).is_dir(),  # Skip directories
                "__pycache__" in file_path,  # Skip __pycache__ directories
                "__init__.py" in file_path,  # Skip __init__.py files
                all([part not in Path(file_path.removesuffix(".pyi")).as_posix() for part in ["/api/", "/domain/"]]),  # noqa: C419
                "/domain/base.pyi" in file_path,  # Skip base.pyi file for domain models
            ]
        ):
            logging.debug(f"Removing stub file: {file_path}")
            Path(file_path).unlink(missing_ok=True)
            return True
    return False


def process_endpoint_controllers(output_dir_tree: list[str]) -> None:
    """
    Processes endpoint controllers and applies rewrites to the generated stubs.

    :param output_dir_tree: A list of file paths in the output directory tree.
    """
    for stub_file_path in output_dir_tree:
        if remove_stub_if_not_needed(stub_file_path):
            continue
        RequestMakerRewriter.apply(stub_path=stub_file_path, exclude_classes=["NexosAIAPIEndpointController"])


def try_rewriting_stubs(
    output_dir: str = STUBGEN_OUTPUT_DIR,
    src_dir: str = "src",
    test_dir: str = "tests",
) -> None:
    """
    Attempts to rewrite stubs.
    """
    output_dir_as_path = Path(output_dir)
    src_dir_as_path = Path(src_dir)
    test_dir_as_path = Path(test_dir)

    tests_tree = generate_file_tree_paths_for_directory(test_dir_as_path)
    sources_tree = generate_file_tree_paths_for_directory(src_dir_as_path)
    full_tree = tests_tree + sources_tree

    remove_existing_stubs_from_file_tree(full_tree)
    try:
        compile_initial_stubs(output_dir=output_dir_as_path)
        stub_files_tree = generate_file_tree_paths_for_directory(output_dir_as_path)
        process_endpoint_controllers(stub_files_tree)
        writer = DomainModelsDictionariesWriter.apply(
            domain_models_path=str(output_dir_as_path / "nexosapi" / "domain"), extra_paths=FILES_TO_EXPLICITLY_REWRITE
        )
        models_map = writer.build_basemodel_to_typeddict_map()
        BindModelTypeTransformer.apply(models=models_map, stubs_tree=stub_files_tree)
        include_stubs(output=output_dir_as_path, src=src_dir_as_path, tests=test_dir_as_path)
    except Exception as e:
        logging.exception("An error occurred during stub generation and rewriting.", exc_info=e)
    else:
        rmtree(output_dir)


if __name__ == "__main__":
    setup_logging(level=logging.INFO)
    try_rewriting_stubs()
