from pathlib import Path

import mypy.stubgen


def compile_stubs(output_dir: Path) -> None:
    """
    Generates type stubs for the current project and saves them to the given output directory.

    :param output_dir: The directory where the generated stubs will be saved.
    """
    mypy.stubgen.main(["src", "-o", str(output_dir), "--include-docstrings"])
    mypy.stubgen.main(["tests", "-o", str(output_dir), "--include-docstrings"])
