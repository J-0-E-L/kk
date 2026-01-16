#!/usr/bin/env python3

import itertools as it

def do_nothing(left, right, groups, buy, avoid):
    return

def make_groups(left, right, groups, buy, avoid):
    if right in groups and left in flatten(right, groups):
        print("Cannot define group circularly") # TODO: fix this
        raise Exception

    if left not in groups:
        groups[left] = []
    groups[left].append(right)

def make_buy_constraints(left, right, groups, buy, avoid):
    for l_name in flatten(left, groups):
        for r_name in flatten(right, groups):
            if l_name not in buy:
                buy[l_name] = []
            buy[l_name].append(r_name)

def make_avoid_constraints(left, right, groups, buy, avoid):
    for l_name in flatten(left, groups):
        for r_name in flatten(right, groups):
            if l_name not in avoid:
                avoid[l_name] = []
            avoid[l_name].append(r_name)

def flatten(name, groups):
    if name not in groups:
        return [name]

    return list(it.chain(*[flatten(member, groups) for member in groups[name]]))

def resolve_expand_keyword(l_name, r_name, groups):
    if l_name != keyword_expand and r_name != keyword_expand:
        return [(l_name, r_name)]

    members_iter = lambda name: [name] if name not in groups else groups[name]

    if l_name == keyword_expand and r_name == keyword_expand:
        print(f"Cannot expand {keyword_expand} keyword")
        raise Exception

    if l_name == keyword_expand:
        name = r_name
    if r_name == keyword_expand:
        name = l_name

    if name not in groups:
        return [(name, name)]
    return [(member, member) for member in groups[name]]

comment = '#'
delimeter = ','
operator_group = ':'
operator_buy = '->'
operator_avoid = '-x'
keyword_expand = '.'

operators = {operator_buy: make_buy_constraints,
             operator_avoid: make_avoid_constraints,
             operator_group: make_groups}


def rdrop(string, sub): # remove first occurence of sub as well as all characters to the right of it
    return string[:string.find(sub) % (len(string) + 1)]

def extract_names(side):
    names = []

    for name in side.split(delimeter):
        name = clean_name(name)

        if not is_valid_name(name):
            print(f"invalid name {name}") # TODO: fix this message
            raise Exception

        names.append(name)

    return names

def clean_name(name):
    return " ".join(name.split()).lower()

def is_valid_name(name):
    nospaces = "".join(name.split())
    return name == clean_name(name) and (nospaces.isalnum() or name == keyword_expand)


def parse(filename):
    commands = []

    with open(filename, 'r') as fp:
        for i, line in enumerate(fp):
            line = rdrop(line, comment) # remove comments 
            if not line or line.isspace(): # ignore any empty lines
                continue
            
            counts = {op: line.count(op) for op in operators}
            if sum(counts.values()) > 1:
                print("Too many operators") # TODO: fix this message
                raise Exception
            if sum(counts.values()) == 0:
                print(f"No operator detected on line {i}") # TODO: fix this message
                raise Exception

            # get the operator on this line
            operator = max(counts.keys(), key=lambda op: counts[op])

            left, right = line.split(operator) # NOTE: unpacking works because there is guaranteed to be exactly one occurence of operator
            left = extract_names(left)
            right = extract_names(right)
            
            if not left or not right:
                print("Operator is missing an argument") # TODO: fix this message
                raise Exception
            
            if len(left) != len(set(left)) or len(right) != len(set(right)):
                print("Duplicate names in operator argument")
                raise Exception
            commands.append((i, operator, left, right))

    return commands

def resolve(commands):
    groups, buy, avoid = dict(), dict(), dict()

    for i, op, left, right in commands:
         for _l_name, _r_name in it.product(left, right):
             #print(list(_l_name), list(_r_name))
             for l_name, r_name in resolve_expand_keyword(_l_name, _r_name, groups):
                 # print(l_name, r_name)
                 operators[op](l_name, r_name, groups, buy, avoid) # TODO: fix this

    people = set(name for names in groups.values() for name in names if name not in groups)
    for name in avoid:
        avoid[name] = set(avoid[name])
    for name in buy:
        buy[name] = set(buy[name])

    return people, buy, avoid

