#!/bin/python

import yaml
import os, sys
from subprocess import call
from enum import Enum
import re

# Globals Variables :
class inp_mode(Enum):
    interactive = 1
    cmdline = 2

class atomic_registry_setup:
    """Class sets up the atomic registry"""

    def __init__(self, mode = "--interactive"):

        self.container_image = "mohammedzee1000/centos-atomic-registry-quickstart" # The name of the container image
        # self.OC_MASTER_CONFIG = "/etc/origin/master/master-config.yaml"
        self.oc_master_config = "test.yaml" # test
        self.dn_or_ip = "localhost"
        self.config = None

        if mode == "--interactive" or mode == "-i":
            self.inp_mode = inp_mode.interactive

        return

    def install_containers(self):

        CMD = ["sudo", "atomic", "install", self.container_image, self.dn_or_ip]
        print CMD #test
        #call(cmd)

        return

    def customize(self):

        with open(self.oc_master_config) as ymlfile:
            self.config = yaml.load(ymlfile)

        return

    def run_containers(self):

        CMD = ["sudo", "atomic", "run", self.container_image, self.dn_or_ip]
        print CMD #test
        #call(CMD)

        return

    def get_input_interactive(self):

        inp = ""
        # FIXME : Complete this

        return

    def get_input(self):

        if self.inp_mode == inp_mode.interactive:
            self.get_input_interactive()

        # FIXME : Complete this

        return


    def get_dn_or_ip(self):
        """Gets the domain name or ip to be used to setup the atomic registry."""
        if self.inp_mode == inp_mode.interactive:

            inp = ""
            doi = ""
            defval = ""
            ipr = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
            dnr = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

            while True:

                while True:
                    doi = raw_input("Domain or IP (D/I): ")

                    if doi == "D" or doi == "I":
                        break

                if doi == "D":
                    doi = "Domain Name"
                    defval = "localhost"
                elif doi == "I":
                    doi = "IP Address"
                    defval = "127.0.0.1"

                inp = raw_input(" ** What is the " + doi + " of the atomic registry service [" + defval + "] : ")

                if len(inp) == 0:
                    self.dn_or_ip = defval
                    break
                elif (doi == "Domain Name" and dnr.match(inp)) or (doi == "IP Address" and ipr.match(inp)):
                    self.dn_or_ip = inp
                    break

                print " *E Invalid format of " + doi + ".\n"

        return

def main():
    """This is the main method"""

    print "\n Lets get started : \n"

    setup = atomic_registry_setup()

    # Step 1 : Get the dn or ip
    setup.get_dn_or_ip()
    print

    # Step 2 : Install the containers :
    print "\n * STEP 2 : Installing the registry : \n"
    setup.install_containers()

    # Step 3 : Customizing the configurations (input)
    print  "\n * STEP 3 : Reading parameters needed for configuring the registry\n"
    setup.get_input()

    # Step 4 : Customize the configurations
    print "\n * STEP 4 : Applying changes : \n"
    setup.customize()

    # Step 5 : Run the containers :
    print "\n * STEP 5 : Running the registry : \n"
    setup.run_containers()

    print

    return

if __name__ == '__main__':
    main()