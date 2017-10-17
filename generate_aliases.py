#!/usr/bin/env python2

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools

def main():
    # (alias, full, restrict_to_aliases, incompatible_with)

    cmds=[
        ('k', 'kubectl', None, None),
    ]

    globs=[
        ('sys','--namespace=kube-system', None, None),
    ]

    ops=[
        ('a','apply -f', None, None),
        ('ex','exec -i -t', None, None),
        ('lo','logs -f', None, None),
        ('g','get', None, None),
        ('d','describe', None, None),
        ('rm','delete', None, None),
    ]

    res=[
        ('po','pod', ['g','d','rm','lo'], None),
        ('dep','deployment', ['g','d','rm','lo'], None),
        ('svc','service', ['g','d','rm'], None),
        ('ing','ingress', ['g','d','rm'], None),
        ('cm','configmap', ['g','d','rm'], None),
        ('sec','secret', ['g','d','rm'], None),
    ]

    args=[
        ('oyaml','-o=yaml', ['g'], ['owide','ojson']),
        ('owide','-o=wide', ['g'], ['oyaml','ojson']),
        ('ojson','-o=json', ['g'], ['owide','oyaml']),
        ('all', '--all-namespaces', ['g'], ['f']),
        ('w', '--watch', ['g'], ['oyaml','ojson','owide']),
    ]

    # these accept a value, so they need to be at the end and
    # mutually exclusive within each other.
    positional_args=[
        ('f', '-f', ['g', 'd', 'rm'], [r[0] for r in res]),
    ]

    # [(part, optional, take_exactly_one)]
    parts=[
        (cmds, False, True),
        (globs, True, False),
        (ops, True, True),
        (res, True, True),
        (args, True, False),
        (positional_args, True, True),
    ]

    out = gen(parts)
    out = filter(is_valid, out)

    for cmd in out:
        print "alias {}='{}'".format(
            ''.join([a[0] for a in cmd]),
            ' '.join([a[1] for a in cmd]),
        )

def gen(parts):
    out = [()]
    for (items, optional, take_exactly_one) in parts:
        orig=list(out)
        combos = []

        if optional and take_exactly_one: combos=combos.append([])

        if take_exactly_one: combos = combinations(items, 1, include_0=optional)
        else: combos = combinations(items, len(items), include_0=optional)

        # permutate the combinations if optional (args are not positional)
        if optional:
            new_combos = []
            for c in combos:
                new_combos += list(itertools.permutations(c))
            combos = new_combos

        new_out=[]
        for segment in combos:
            for stuff in orig:
                new_out.append(stuff+segment)
        out=new_out
    return out

def is_valid(cmd):
    for i in xrange(0, len(cmd)):
        # check at least one of requirements are in the cmd
        requirements=cmd[i][2]
        if requirements:
            found=False
            for r in requirements:
                for j in xrange(0, i):
                    if cmd[j][0] == r:
                        found=True
                        break
                if found:
                    break
            if not found:
                return False

        # check none of the incompatibilities are in the cmd
        incompatibilities=cmd[i][3]
        if incompatibilities:
            found=False
            for inc in incompatibilities:
                for j in xrange(0, i):
                    if cmd[j][0] == inc:
                        found=True
                        break
                if found:
                    break
            if found:
                return False

    return True

def combinations(a, n, include_0=True):
    l = []
    for j in xrange(0, n+1):
        if not include_0 and j == 0: continue
        l += list(itertools.combinations(a, j))
    return l

if __name__=='__main__':
    main()
