#!/bin/python

import os
import yaml
import collections

def dep(arg):
    '''
        Dependency resolver

    "arg" is a dependency dictionary in which
    the values are the dependencies of their respective keys.
    '''
    d=dict((k, set(arg[k])) for k in arg)
    r=[]
    while d:
        # values not in keys (items without dep)
        t=set(i for v in d.values() for i in v)-set(d.keys())
        # and keys without value (items without dep)
        t.update(k for k, v in d.items() if not v)
        # can be done right away
        r.append(t)
        # and cleaned up
        d=dict(((k, v-t) for k, v in d.items() if v))
    return r

def mainf():

    testfile = "./test.yml"

    with open(testfile) as ymlfile:
        data = yaml.load(ymlfile)

    dl = dict()

    for item in data["Projects"]:

        if "deplist" in item.keys():

            dl[item["id"]] = item["deplist"]

        else:

            dl[item["id"]] = []

    print data

    print dep(dl)

if __name__ == '__main__':
    mainf()