import math
import tokenize

from typing_extensions import final

from wemake_python_styleguide.violations import best_practices
from wemake_python_styleguide.visitors import base


@final
class _FileFunction(object):

    _file_tokens: tuple[tokenize.TokenInfo]

    def __init__(self, file_tokens: tuple[tokenize.TokenInfo]):
        self._file_tokens = file_tokens

    def __str__(self):
        return '"{0}" function'.format(self._file_tokens[1].string)

    def find(self):
        for token in self._file_tokens:
            print(token)
        assert False


@final
class _FileFunctions(object):

    _file_tokens: list[tokenize.TokenInfo]

    def __init__(self, file_tokens: list[tokenize.TokenInfo]):
        self._file_tokens = file_tokens

    def as_list(self):
        functions = []
        function_tokens = []
        in_function = False
        for token in self._file_tokens:
            if token.string == 'def':
                print('def')
                in_function = True
            # ------------------
            if token.type == tokenize.DEDENT:
                print(token)
            # ------------------
            elif token.type == tokenize.DEDENT and token.line == '':
                in_function = False
                functions.append(_FileFunction(tuple(function_tokens)))
                function_tokens = []
            if in_function:
                function_tokens.append(token)
        return functions


@final
class _FileTokens(object):
    """Class for checking all file_tokens."""

    def __init__(self, file_functions: _FileFunctions):
        self._file_functions = file_functions

    def analyze(self):
        for function in self._file_functions.as_list():
            print(function)
        assert False


@final
class WrongEmptyLinesCountVisitor(base.BaseTokenVisitor):
    """Restricts empty lines in function or method body."""

    _file_tokens: list[tokenize.TokenInfo]

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a counter."""
        super().__init__(*args, **kwargs)
        self._file_tokens = []

    def visit(self, token: tokenize.TokenInfo) -> None:
        """Find empty lines count."""
        self._file_tokens.append(token)
        if token.type == tokenize.ENDMARKER:
            _FileTokens(
                _FileFunctions(
                    self._file_tokens
                )
            ).analyze()
        # print(token)
        # self._try_mark_function_start(token)
        # if self._function_start_line:
        #     if token.type == tokenize.NL and token.line == '\n':
        #         self._empty_lines_count += 1
        #     self._check_empty_lines(token)

    def _check_empty_lines(self, token: tokenize.TokenInfo):
        if token.type == tokenize.DEDENT and token.line == '':
            func_lines = token.start[0] - self._function_start_line - 1
            if self._empty_lines_count:
                available_empty_lines = self._available_empty_lines(
                    func_lines,
                    self._empty_lines_count,
                )
                if self._empty_lines_count > available_empty_lines:
                    self.add_violation(
                        best_practices.WrongEmptyLinesCountViolation(
                            token,
                            text=str(self._empty_lines_count),
                            baseline=available_empty_lines,
                        ),
                    )
                self._function_start_line = 0

    def _try_mark_function_start(self, token: tokenize.TokenInfo):
        if token.string == 'def':
            self._empty_lines_count = 0
            self._function_start_line = token.start[0]

    def _available_empty_lines(
        self,
        function_len: int,
        empty_lines: int,
    ) -> int:
        option = self.options.exps_for_one_empty_line
        if option == 0:
            return 0
        lines_with_expressions = function_len - empty_lines
        return math.floor(lines_with_expressions / option)
