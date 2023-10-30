from sys import argv
import lox # I have to load lox.py as a module due to some module importing shenanigans

if __name__ == "__main__":
    if len(argv) > 2:
        print("Usage: python lox.py [script]")
        exit(64)
    elif len(argv) == 2:
        lox.run_file(argv[1])
    else:
        lox.run_prompt()