from pathlib import Path

import mypy.stubgen

ADDITIONAL_ARGUMENTS = [
    "--include-private",
    "--include-docstrings",
]

DOMAIN_MODELS_PATH = "src/domain"


def compile_initial_stubs(output_dir: Path) -> None:
    """
    Generates type stubs for the current project and saves them to the given output directory.

    :param output_dir: The directory where the generated stubs will be saved.
    """
    ".venv/lib/python3.13/site-packages/mypy/types.py:182"
    mypy.stubgen.main(["src", "-o", str(output_dir), *ADDITIONAL_ARGUMENTS])
    mypy.stubgen.main(["tests", "-o", str(output_dir), *ADDITIONAL_ARGUMENTS])
