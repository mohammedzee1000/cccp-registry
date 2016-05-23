#!/bin/python

import yaml
import os
import sys
from subprocess import call
from enum import Enum
import re


# Globals Variables :
class InpMode(Enum):
    interactive = 1
    cmdline = 2


class AtomicRegistryConfigManager:
    """Class contains the parameters used for customizing the atomic registry"""

    def __init__(self):

        # self.OC_MASTER_CONFIG = "/etc/origin/master/master-config.yaml"
        self.oc_master_config = "test.yaml"  # test
        self.oc_test_config = "temp.yaml"

        with open(self.oc_master_config) as ymlfile:
            self.config = yaml.load(ymlfile)

        return

    # All the configurable sections functions are located here.

    # * Certs
    def add_named_certs(self, certfile = None, keyfile = None):

        thesection = self.config["assetConfig"]["servingInfo"]["namedCertificates"]

        print thesection

        return


    # Section Ends


    # Test functions
    def test_print_config(self):
        """Test function"""

        print self.config

        return


    def test_finalize_config(self):

        with open(self.oc_test_config, "w") as yamlfile:
            yamlfile.write(yaml.dump(self.config))

        return

    # Finalize Function
    def finalize_config(self):

        with open(self.oc_master_config, "w") as ymlfile:
            ymlfile.write(yaml.dump(self.config))

        return


class AtomicRegistryQuickstartSetup:
    """Class sets up the atomic registry"""

    def __init__(self, mode="--interactive"):
        """Initializes the objects by setting instance variables"""

        # Constants

        self.container_image = "mohammedzee1000/centos-atomic-registry-quickstart"  # The name of the container image
        self.dn_or_ip = "localhost"
        self.config = None

        if mode == "--interactive" or mode == "-i":
            self.inp_mode = InpMode.interactive

        # Config params
        self.config_manager = None

        return

    def install_containers(self):
        """Installs the atomic registry containers"""

        cmd = ["sudo",
               "atomic",
               "install",
               self.container_image,
               self.dn_or_ip]

        print cmd  # test
        # call(cmd)

        return

    def customize(self):
        """Applying configuration changes to the atomic registry"""

        self.config_manager = AtomicRegistryConfigManager()


        return

    def test_customize(self):
        """Applying configuration changes to the atomic registry test"""

        self.config_manager = AtomicRegistryConfigManager()

        #self.config_manager.test_print_config()  # Test
        self.config_manager.test_finalize_config() # Test

        return

    def run_containers(self):
        """Runs the containers that have been installed"""

        cmd = ["sudo",
               "atomic",
               "run",
               self.container_image,
               self.dn_or_ip]

        print cmd  # test
        # call(cmd)

        return

    def get_input_interactive(self):

        inp = ""
        # FIXME : Complete this

        return

    def get_input(self):

        if self.inp_mode == InpMode.interactive:
            self.get_input_interactive()

        # FIXME : Complete this

        return

    def get_preinstall(self):
        """Gets the domain name or ip to be used to setup the atomic registry.."""
        if self.inp_mode == InpMode.interactive:

            inp = ""
            doi = ""
            defval = ""

            ipr = re.compile(
                "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}"
                "([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

            dnr = re.compile(
                "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
                "([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

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

                inp = raw_input(" ** What is the " +
                                doi +
                                " of the atomic registry service [" +
                                defval +
                                "] : ")

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

    setup = AtomicRegistryQuickstartSetup()

    # Step 1 : Get the dn or ip
    print "\n * STEP 1 : Getting basic information needed to install atomic registry\n"
    setup.get_preinstall()
    print

    # Step 2 : Install the containers :
    print "\n * STEP 2 : Installing the registry : \n"
    setup.install_containers()

    # Step 3 : Customize the configurations
    print "\n * STEP 3 : Customizing : \n"
    setup.test_customize()

    # Step 4 : Run the containers :
    print "\n * STEP 4 : Running the registry : \n"
    setup.run_containers()

    print

    return


if __name__ == '__main__':
    main()
