import math
import tokenize

from typing_extensions import final

from wemake_python_styleguide.violations import best_practices
from wemake_python_styleguide.visitors import base


@final
class _Function(object):

    _tokens: tuple[tokenize.TokenInfo]

    def __init__(self, file_tokens: tuple[tokenize.TokenInfo]):
        self._tokens = file_tokens

    def name_token(self):
        return self._tokens[1]

    def body(self):
        target_tokens = []
        for token in self._tokens:
            if '#' in token.line or token.type == tokenize.STRING or '"""' in token.line:
                continue
            target_tokens.append(
                token,
            )
        from pprint import pprint
        pprint(list(token for token in target_tokens))
        return ''.join(list(token.string for token in target_tokens))


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
            if token.type == tokenize.NAME and token.string == 'def':
                in_function = True
            elif token.type == tokenize.DEDENT and token.string == '' and function_tokens:
                in_function = False
                functions.append(_Function(tuple(function_tokens)))
                function_tokens = []
            if in_function:
                function_tokens.append(token)
        return functions


@final
class _FileTokens(object):
    """Class for checking all file_tokens."""

    def __init__(
        self,
        file_functions: _FileFunctions,
        exps_for_one_empty_line: int
    ):
        self._file_functions = file_functions
        self._exps_for_one_empty_line = exps_for_one_empty_line

    def analyze(self):
        violations = []
        for function in self._file_functions.as_list():
            splitted_function_body = function.body().strip().split('\n')
            print('----------')
            print(function.body())
            empty_lines_count = len([
                line for line
                in splitted_function_body
                if line == ''
            ])
            print(f'{empty_lines_count=}')
            print('----------')
            if not empty_lines_count:
                return []
            available_empty_lines = self._available_empty_lines(
                len(splitted_function_body), empty_lines_count
            )
            print(f'{available_empty_lines=}')
            print('----------')
            if empty_lines_count > available_empty_lines:
                violations.append(
                    best_practices.WrongEmptyLinesCountViolation(
                        function.name_token(),
                        text=str(empty_lines_count),
                        baseline=available_empty_lines,
                    ),
                )
        return violations

    def _available_empty_lines(
        self,
        function_len: int,
        empty_lines: int,
    ) -> int:
        option = self._exps_for_one_empty_line
        if option == 0:
            return 0
        lines_with_expressions = function_len - empty_lines
        return math.floor(lines_with_expressions / option)


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
        if token.type != tokenize.ENDMARKER:
            return
        violations = _FileTokens(
            _FileFunctions(
                self._file_tokens
            ),
            self.options.exps_for_one_empty_line,
        ).analyze()
        if not violations:
            return
        for violation in violations:
            self.add_violation(violation)
