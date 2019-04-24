"""
    Generates class definitions for expressions from an input file and writes to
    an output file

    base class is named Expr

    entry format
    <name_of class> : <type> <name> (, <type> <name>)*
"""
import sys


def indent(string, level=0):
    return 4 * level * " " + string


def generate_expression(out_file, description):
    name, definitions = description.split(":")
    lines = [indent("class {name}(Expr):".format(name=name.strip()))]

    definitions = [[part.strip() for part in definition.strip().split()]
                   for definition in definitions.split(",")]
    arguments = ["{name}: {type}".format(name=definition[1], type=definition[0])
                 for definition in definitions]

    lines.append(indent("def __init__(self, {args}):".format(
        args=", ".join(arguments)), 1))

    for definition in definitions:
        lines.append(indent("self.{name} = {name}".format(name=definition[1]), 2))

    lines.append("")
    lines.append(indent("def visit(self, visitor, *args, **kwargs):", 1))
    lines.append(indent("return visitor.visit_{name}(self, *args, **kwargs)".format(name=name.strip().lower()), 2))
    lines.append("")

    print("\n".join(lines), file=out_file)


def generate_base(out_file):
    lines = [indent("class Expr(object):"),
             indent("def visit(self, visitor, *args, **kwargs):", 1),
             indent("pass", 2),
             ""]
    print("\n".join(lines), file=out_file)


def generate_header(out_file):
    lines = ["from PyLOX.token import Token", "", ""]
    print("\n".join(lines), file=out_file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python {name} <source> <output>".format(name=sys.argv[0]))
        sys.exit(0)
    with open(sys.argv[1], "r") as f:
        descriptions = f.readlines()
    with open(sys.argv[2], "w") as f:
        generate_header(f)
        generate_base(f)
        for description in descriptions:
            print("", file=f)
            generate_expression(f, description)
