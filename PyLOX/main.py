import sys

from PyLOX.scanner import Scanner


def main(args):
    if len(args) > 2:
        print("Usage: {name} [script]".format(name=args[0]))
    elif len(args) == 2:
        run_file(args[1])
    else:
        run_prompt()


def run_file(path):
    with open(path, "r") as f:
        source = f.read()
    return run(source)


def run_prompt():
    while True:
        print("> ", end="")
        prompt = input()
        if prompt == "exit":
            # exit is an additional keyword for this interpreter
            return
        run(prompt)


def run(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(token)


if __name__ == "__main__":
    main(sys.argv)
