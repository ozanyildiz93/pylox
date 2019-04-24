import sys

from PyLOX.interpreter import Interpreter, PyLOXRuntimeError
from PyLOX.parser import Parser
from PyLOX.scanner import Scanner


def main(args, stream=sys.stdout):
    if len(args) > 2:
        print("Usage: {name} [script]".format(name=args[0]))
    elif len(args) == 2:
        return run_file(args[1], stream)
    else:
        return run_prompt(stream)


def run_file(path, stream):
    with open(path, "r") as f:
        source = f.read()
    interpreter = Interpreter(stream)
    return run(source, interpreter)


def run_prompt(stream):
    interpreter = Interpreter(stream)
    while True:
        print("> ", end="")
        prompt = input()
        if prompt == "exit":
            # exit is an additional keyword for this interpreter
            return 0
        run(prompt, interpreter)


def run(source, interpreter):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    if not scanner.valid:
        # there was a problem with tokens
        return -1
    parser = Parser(tokens)
    program = parser.parse()
    if not parser.valid:
        # there was a problem with parser
        return -1
    #    ExpressionPrinter().print(program)
    try:
        outcomes = [interpreter.interpret(stmt) for stmt in program]
    except PyLOXRuntimeError as e:
        print(e)
        return -1
    for outcome in outcomes:
        if outcome is not None:
            print(outcome)


if __name__ == "__main__":
    main(sys.argv)
