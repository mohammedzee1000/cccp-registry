#!/bin/python

import yaml
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)


def resolve_dependencies(dependencymap):
    """
        Dependency resolver

    "dependencymap" is a dependency dictionary in which
    the values are the dependencies of their respective keys.
    """
    d = dict((k, set(dependencymap[k])) for k in dependencymap)
    r = []

    while d:

        # values not in keys (items without dep)
        t = set(i for v in d.values() for i in v)-set(d.keys())
        # and keys without value (items without dep)
        t.update(k for k, v in d.items() if not v)
        # can be done right away
        r.append(t)
        # and cleaned up
        d = dict(((k, v-t) for k, v in d.items() if v))

    return r


def mainfunction():

    testfile = "./test.yml"

    with open(testfile) as ymlfile:
        data = yaml.load(ymlfile)

    dm = dict()

    for item in data["Projects"]:

        if "deplist" in item.keys():

            dm[item["id"]] = item["deplist"]

        else:

            dm[item["id"]] = []

    print "Original data : \n"
    pp.pprint(data)

    print "\nDependency Map : \n"
    pp.pprint(dm)

    print "\nExecution order : \n"
    print resolve_dependencies(dm)
    print

if __name__ == '__main__':
    mainfunction()