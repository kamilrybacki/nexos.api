import abc
import ast
import dataclasses
import typing


class StubTransformer(ast.NodeTransformer, abc.ABC):
    """
    Base class for transforming Python stub files.
    This class can be extended to implement specific transformations.

    :ivar exclude_classes: A set of class names to exclude from rewriting.
    :ivar modified: A boolean indicating if any modifications were made to the AST.
    """

    exclude_classes: set[str] = dataclasses.field()
    modified: bool = False
    _instance: typing.ClassVar[typing.Self | None] = None

    @staticmethod
    def _indent_docstring(docstring: str, indent: int) -> str:
        """
        Indents the docstring to match the indentation level of the method.

        :param docstring: The original docstring to be indented.
        :return: The indented docstring.
        """
        if not docstring:
            return ""
        lines = docstring.splitlines()
        indented_lines = [lines[0]] + [indent * " " + line for line in lines[1:]]
        return "\n".join(indented_lines)

    @classmethod
    def apply(cls, **kwargs: typing.Any) -> typing.Self:
        """
        Applies the given AST transformer to the specified stub file.

        :param kwargs: Keyword arguments for the transformer, such as `exclude_classes`.
        :raises NotImplementedError: If the `run_rewrites` method is not implemented in
        """
        if cls._instance is None:
            cls._instance = cls()

        instance: typing.Self = cls._instance
        instance.run_rewrites(**kwargs)
        return instance

    @abc.abstractmethod
    def run_rewrites(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """
        Abstract method to run the specific rewrites on the AST.
        This method must be implemented by subclasses.

        :param args: Positional arguments for the rewrite.
        :param kwargs: Keyword arguments for the rewrite.
        """
        raise NotImplementedError("Subclasses must implement this method.")
