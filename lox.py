from typing import Union

import Token
import scanner as scan
import parser
import ast_printer
import interpreter

had_error : bool = False
had_runtime_error : bool = False
interprter = interpreter.Interpreter() # The typo is intentional

def run(source : str) -> None:
    scanner = scan.Scanner(source)
    tokens = scanner.scan_tokens()

    _parser = parser.Parser(tokens)
    statements = _parser.parse()

    if had_error:
        return
    else:
        #print(ast_printer.AstPrinter().print_ast(expression))
        interprter.interpret(statements)
    # for token in tokens:
    #     print(token)

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
    if had_runtime_error:
        exit(70)

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

def error(line : Union[int, Token.Token], message : str) -> None:
    if type(line) == int:
        report(line, "", message)
    else:
        _token = line
        if (_token.token_type == Token.TokenType.EOF):
            report(_token.line, " at end", message)
        else:
            report(_token.line, f" at '{_token.lexeme}'", message)

def runtime_error(e : interpreter.RuntimeError):
    global had_runtime_error
    print(f"{str(e)}\n[line{e.token.line}]")
    had_runtime_error = True

def report(line : int, where : str, message : str) -> None:
    global had_error
    print(f"[line {line}] Error{where}: {message}")

    had_error = True
