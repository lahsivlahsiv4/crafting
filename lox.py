from sys import argv
from typing import Union

import token
import scanner as scan
import parser
import ast_printer

had_error : bool = False

def run(source : str) -> None:
    scanner = scan.Scanner(source)
    tokens = scanner.scan_tokens()

    _parser = parser.Parser(tokens)
    expression = _parser.parse()

    if had_error:
        return
    else:
        print(ast_printer.AstPrinter().print_ast(expression))
    for token in tokens:
        print(token)

def run_file(path : str) -> None:
    global had_error 

    try:
        with open(path) as f:
            source_code = f.read()
    except FileNotFoundError:
        print("File not found")
        exit(2)

    run(source_code)

    if had_error:
        exit(65)

def run_prompt() -> None:
    global had_error 

    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        run(line)
        had_error = False

def error(line : Union[int, token.Token], message : str) -> None:
    if type(line) == int:
        report(line, "", message)
    else:
        _token = line
        if (_token.token_type == token.TokenType.EOF):
            report(_token.line, " at end", message)
        else:
            report(_token.line, f" at '{_token.lexeme}'", message)

def report(line : int, where : str, message : str) -> None:
    global had_error
    print(f"[line {line}] Error{where}: {message}")

    had_error = True

if __name__ == "__main__":
    if len(argv) > 2:
        print("Usage: python lox.py [script]")
        exit(64)
    elif len(argv) == 2:
        run_file(argv[1])
    else:
        run_prompt()
