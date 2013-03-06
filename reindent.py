#!/usr/bin/env python

from __future__ import print_function
import sys
import getopt
import codecs
import tempfile
import shutil
import os


def find_indentation(line, config):
    if len(line) and line[0] in (" ", "\t"):
        if line[0] == "\t":
            config['is-tabs'] = True
        # Find indentation
        i = 0
        for char in list(line):
            if char not in (" ", "\t"):
                break
            i += 1
        config["from"] = i


def run(filenames, config):
    for filename in filenames:
        with codecs.open(filename, encoding=config['encoding']) as f:
            if config['dry-run']:
                print("Filename: %s" % filename)
                tmp = sys.stdout
            else:
                tmp = tempfile.NamedTemporaryFile(mode='wb', delete=False)

            while True:
                line = f.readline()
                if not line:
                    break
                line = line.rstrip('\r\n')

                if config['from'] < 0:
                    find_indentation(line, config)
                if config['from'] < 0:
                    # Continue to the next line, indentation not found
                    print(line, file=tmp)
                    continue

                indent = " " if not config['is-tabs'] else "\t"
                indent = indent * config['from']

                newindent = " " if not config['tabs'] else "\t"
                if not config['tabs']:
                    newindent = newindent * config['to']

                # Find current indentation level
                level = 0
                while True:
                    whitespace = line[:len(indent) * (level + 1)]
                    if whitespace == indent * (level + 1):
                        level += 1
                    else:
                        break

                line = (newindent * level) + line[len(indent) * level:]
                print(line, file=tmp)

            if not config["dry-run"]:
                tmp.close()
                shutil.copy(tmp.name, filename)
                os.remove(tmp.name)


def main(args):
    config = {
        "dry-run": False,
        "help": False,
        "to": 4,
        "from": -1,
        "tabs": False,
        "encoding": "utf-8",
        "is-tabs": False,
    }
    possible_args = {
        "d":  "dry-run",
        "h":  "help",
        "t:": "to=",
        "f:": "from=",
        "n":  "tabs",
        "e:": "encoding=",
    }
    optlist, filenames = getopt.getopt(
        args[1:],
        "".join(possible_args.keys()),
        possible_args.values()
    )

    shortargs, longargs = [], []
    for shortarg in possible_args:
        shortargs.append(shortarg.rstrip(":"))
        longargs.append(possible_args[shortarg].rstrip("="))

    for opt, val in optlist:
        opt = opt.lstrip("-")
        if opt in shortargs:
            opt = longargs[shortargs.index(opt)]
        if isinstance(config[opt], bool):
            config[opt] = True
        elif isinstance(config[opt], int):
            config[opt] = int(val)
        else:
            config[opt] = val

    if config['help'] or not filenames:
        help = """
        Usage: %s [options] filename(s)

        Options:
            -h, --help              Show this message
            -d, --dry-run           Don't save anything, just print
                                    the result
            -t <n>, --to <n>        Convert to this number of spaces
                                    (default: 4)
            -f <n>, --from <n>      Convert from this number of spaces
                                    (default: auto-detect, will also
                                    detect tabs)
            -n, --tabs              Don't convert indentation to spaces,
                                    convert to tabs instead. -t and
                                    --to will have no effect.
            -e <s>, --encoding <s>  Open files with specified encoding
                                    (default: utf-8)
        """ % args[0]

        # Also removes 8 leading spaces to remove our indentation
        print("\n".join([x[8:] for x in help[1:].split("\n")]))
        sys.exit(0)

    run(filenames, config)

if __name__ == "__main__":
    main(sys.argv)
