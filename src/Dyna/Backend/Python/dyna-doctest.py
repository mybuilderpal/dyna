#!/usr/bin/env python
import re, sys

from interpreter import Interpreter
from repl import REPL
from cStringIO import StringIO

from utils import red, green, yellow, strip_comments


def extract(code):
    for block in re.compile('^> ', re.MULTILINE).split(code):
        cmd = []
        expect = []
        for i, line in enumerate(block.split('\n')):
            if line.startswith('|') or i == 0:
                if line.startswith('|'):
                    line = line[1:]
                cmd.append(line)
            else:
                expect.append(line)

        yield '\n'.join(cmd).strip(), '\n'.join(expect).strip()


def clean(x):
    return re.sub('\033\[\d+m', '', strip_comments(x)).strip()


def run(code):
    interp = Interpreter()
    repl = REPL(interp)
    errors = []
    for cmd, expect in extract(code):
        if not clean(cmd):
            print
            continue
        print yellow % '> %s' % cmd

        if clean(cmd) == '*resume*':
            repl.cmdloop()
            continue

        sys.stdout = x = StringIO()
        try:
            repl.onecmd(cmd)
        finally:
            sys.stdout = sys.__stdout__

        got = clean(x.getvalue())
        expect = clean(got)

        if clean(expect) == '*ignore*':
            continue

        if expect != got:
            print green % expect
            print red % got
            errors.append([cmd, expect, got])
        else:
            print
            print got

        print

    if not errors:
        print green % 'PASS!'
        print
    else:
        print red % '%s errors' % len(errors)
        print
        sys.exit(1)


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        with file(filename) as f:
            run(f.read())
