from sys import argv

import scanner as scan

had_error : bool = False

def run(source : str) -> None:
    scanner = scan.Scanner(source)
    tokens = scanner.scan_tokens()

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

def error(line : int, message : str) -> None:
    report(line, "", message)

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
