from pathlib import Path

import mypy.stubgen

ADDITIONAL_ARGUMENTS = [
    "--include-private",
    "--include-docstrings",
]


def compile_stubs(output_dir: Path) -> None:
    """
    Generates type stubs for the current project and saves them to the given output directory.

    :param output_dir: The directory where the generated stubs will be saved.
    """
    mypy.stubgen.main(["src", "-o", str(output_dir), *ADDITIONAL_ARGUMENTS])
    mypy.stubgen.main(["tests", "-o", str(output_dir), *ADDITIONAL_ARGUMENTS])
