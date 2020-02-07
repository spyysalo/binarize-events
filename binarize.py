#!/usr/bin/env python3

import sys
import re

from collections import namedtuple
from itertools import combinations

from logging import warning


TEXTBOUND_RE = re.compile(r'^(T[0-9]+)\t(\S+) (\d+) (\d+)\t(.*)')

RELATION_RE = re.compile(r'^(R[0-9]+)\t(\S+) (\S+) (\S+)\t(.*)')

EVENT_RE = re.compile(r'^(E[0-9]+)\t(\S+):(\S+)(.*)')

MODIFICATION_RE = re.compile(r'^(M[0-9]+)\t(\S+) (\S+)$')

EQUIV_RE = re.compile(r'^(\*)\t(Equiv) (.*)$')


Textbound = namedtuple('Textbound', ['id', 'type', 'start', 'end', 'text'])

Relation = namedtuple('Relation', ['id', 'type', 'arg1', 'arg2'])

Event = namedtuple('Event', ['id', 'type', 'trigger_id', 'args'])

Modification = namedtuple('Modification', ['id', 'type', 'target'])

Equiv = namedtuple('Equiv', ['id', 'type', 'args'])

Binarized = namedtuple('Binarized', ['type', 'arg1', 'arg2'])


PHYSICAL_ENTITY_TYPES = set([
    'Protein',
    'Entity',
])

EVENT_TYPES = set([
    'Binding',
    'Gene_expression',
    'Localization',
    'Negation',
    'Negative_regulation',
    'Phosphorylation',
    'Positive_regulation',
    'Protein_catabolism',
    'Regulation',
    'Speculation',
    'Transcription',
])


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('file', nargs='+',
                    help='BioNLP ST .ann file(s)')
    return ap


def parse_textbound_line(line, fn, ln):
    m = TEXTBOUND_RE.match(line)
    if not m:
        raise ValueError('Failed to parse {} in {}: {}'.format(ln, fn, line))
    id_, type_, start, end, text = m.groups()
    start, end = int(start), int(end)
    t = Textbound(id_, type_, start, end, text)
    return [t]


def parse_relation_line(line, fn, ln):
    m = RELATION_RE.match(line)
    if not m:
        raise ValueError('Failed to parse {} in {}: {}'.format(ln, fn, line))
    id_, type_, arg1, arg2 = m.groups()
    r = Relation(id_, type_, arg1, arg2)
    return [r]


def parse_event_line(line, fn, ln):
    m = EVENT_RE.match(line)
    if not m:
        raise ValueError('Failed to parse {} in {}: {}'.format(ln, fn, line))
    id_, type_, trigger_id, args = m.groups()
    args = args.strip().split()
    e = Event(id_, type_, trigger_id, args)
    return [e]


def parse_modification_line(line, fn, ln):
    m = MODIFICATION_RE.match(line)
    if not m:
        raise ValueError('Failed to parse {} in {}: {}'.format(ln, fn, line))
    id_, type_, target = m.groups()
    m = Modification(id_, type_, target)
    return [m]


def parse_equiv_line(line, fn, ln):
    m = EQUIV_RE.match(line)
    if not m:
        raise ValueError('Failed to parse {} in {}: {}'.format(ln, fn, line))
    id_, type_, args = m.groups()
    e = Equiv(id_, type_, args)
    return [e]


def is_negated(id_, modifications):
    for m in modifications:
        if m.type == 'Negation' and m.target == id_:
            return True
    return False


def binarize(fn, options):
    textbounds = []
    relations = []
    events = []
    modifications = []
    equivs = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if l.isspace() or not l:
                pass
            elif l[0] == 'T':
                textbounds.extend(parse_textbound_line(l, fn, ln))
            elif l[0] == 'R':
                relations.extend(parse_relation_line(l, fn, ln))
            elif l[0] == 'E':
                events.extend(parse_event_line(l, fn, ln))
            elif l[0] == 'M':
                modifications.extend(parse_modification_line(l, fn, ln))
            elif l[0] == '*':
                equivs.extend(parse_equiv_line(l, fn, ln))
            else:
                warning('Cannot parse line: {}'.format(l))
    for t in textbounds:
        if t.type in ('Protein', ):
            print('{}\t{} {} {}\t{}'.format(*t))
    next_idx = 1
    for e in equivs:
        print('{}\t{} {}'.format(*e))
    for e in events:
        if e.type == 'Binding':
            theme_args = [a for a in e.args if a.startswith('Theme')]
            for a, b in combinations(theme_args, 2):
                if is_negated(e.id, modifications):
                    out_type = 'Negated'
                else:
                    out_type = 'Complex_formation'
                a1 = 'Arg1:{}'.format(a.split(':')[1])
                a2 = 'Arg2:{}'.format(b.split(':')[1])
                print('R{}\t{} {} {}'.format(next_idx, out_type, a1, a2))
                next_idx += 1



def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        binarize(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
