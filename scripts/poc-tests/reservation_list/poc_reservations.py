#!/bin/python

import yaml
from pprint import PrettyPrinter
import re

with open("reservations.yml") as testfile:
    ymldata = yaml.load(testfile)

pp = PrettyPrinter(indent=4)

def testinp(theid, appid):

    success = True
    theid = int(theid)

    for reservation in ymldata["Reservations"]:

        for rappid in reservation["appid"]:

            if not rappid.startswith("re=") and appid == rappid:

                print "App ID Reserved, checking reservation list"
                print reservation["id"]

                if theid not in reservation["theid"]:

                    success = False

            elif rappid.startswith("re="):

                appidre = re.compile(rappid.split("=")[1])

                if appidre.match(appid):

                    print "App ID Reserved, checking reservation list"

                    if theid not in reservation["id"]:

                        success = False

    print str.format("ID : {0}\nAPPID : {1}\nRESULT : {2}", theid, appid, success)

    return

print "Input : \n"

tid = raw_input("Test ID : ")
tappid = raw_input("Test APPID : ")

print

print "\nReservations : \n"

pp.pprint(ymldata)

print "\nResult\n"

testinp(tid, tappid)

print
