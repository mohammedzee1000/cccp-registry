#!/bin/python

import yaml
import os
import sys
from subprocess import call, Popen, PIPE
import re
import pprint
from shutil import copy2
from urlparse import urlparse

pp = pprint.PrettyPrinter(indent=4)

# Globals Variables :
class InpMode():
    interactive = 1
    cmdline = 2


class Validator:

    def is_valid_file(pth):
        """Checks if a path is a valid file"""

        valid_file = True

        if not os.path.isabs(pth):

            print " **E Please provide absolute path, try again..."
            valid_file = False

        elif not os.path.exists(pth):

            print " **E The file path you provided does not exist, try again..."
            valid_file = False

        elif not os.path.isfile(pth):

            print " **E Please provide the path of a file, try again..."
            valid_file = False

        return valid_file


    def _is_valid_ip(ip):

        ipr = re.compile(
            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}"
            "([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(:[0-9].)?$")

        retval = True

        if ipr.match(ip) == None:
            retval = False

        return retval

    def _is_matchable_ip(ip):

        ipr = re.compile(
            "^((([0-9])+\.){3}([0-9]+)([:][0-9]+)?)"
        )

        retval = True

        if ipr.match(ip) == None:
            retval = False

        return retval

    def _is_valid_dn(dn):

        dnr = re.compile(
            "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
            "([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])(:[0-9].)?$")

        retval = True

        if dnr.match(dn) == None:
            retval = False

        return retval

    def is_valid_url(url, schemarequired=True):
        """Checks if a specified url is valid"""

        validurl = True

        parsed_url = urlparse(url)
        url_main = ""

        while True:

            if len(parsed_url.netloc) == 0 and len(parsed_url.path) == 0:
                validurl = False
                break

            if schemarequired:
                url_main = parsed_url.netloc
                if not bool(parsed_url.scheme):
                    validurl = False
                    break
            else:
                url_main = parsed_url.path

            if Validator._is_matchable_ip(url_main) and not Validator._is_valid_ip(url_main):
                validurl = False
                break

            else:
                break

        return validurl


class AtomicRegistryConfigManager:
    """Class contains the parameters used for customizing the atomic registry"""

    _configchange = " [\033[1;32mCONFIGCHANGE\033[0m] "

    def __init__(self, drycreate=False):

        #self._oc_master_config  = "/etc/origin/master/master-config.yaml"
        self._oc_master_config = "test.yaml"  # test FIXME: Set this up before shipping
        self._oc_test_config = "temp.yaml"

        if not drycreate:
            with open(self._oc_master_config) as ymlfile:
                self._config = yaml.load(ymlfile)

        return

    # All the configurable sections functions are located here.

    # * Certs - All functions that handle certificate related configs

    # ** Named certs : Function related to configuring named certs
    def get_named_certs(self):
        """P : Returns the list of dictionaries representing named certs configured or None."""
        return self._config["assetConfig"]["servingInfo"]["namedCertificates"]

    def set_named_certs(self, value):
        """I : Sets the named certs to specified value"""

        self._config["assetConfig"]["servingInfo"]["namedCertificates"] = value

        return

    def add_named_cert(self, certfile, keyfile, names=None):
        """P : Function adds a named certificate to the config file."""

        # Get what is already present in the config section to modify
        currconfig = self.get_named_certs()

        # Add the cert file and key file to the content to be added to the section
        content = {"keyFile": keyfile, "certFile": certfile}

        # If any names list has been passed
        if names != None:
            nmlist = []

            # Go through the list and make every item quoted, so yaml dumper can handle it appropriately.
            for item in names:
                nmlist.append(item)

            # Add the name list to the content to be written as 'names'
            content["names"] = nmlist

        toadd = None

        # If current section is emply, then set current content to list, otherwise, append it to existing certs config
        if currconfig is None:
            toadd = [content]

        else:
            temp = currconfig
            toadd = temp + [content]

        # Update the section with appropriate changes.
        print AtomicRegistryConfigManager._configchange + "Appending entry for named cert " + certfile + " and " + keyfile + "..."
        self.set_named_certs(toadd)

        return

    def delete_named_cert(self, certfile, keyfile):
        """P : Deletes a specified named certs entry"""

        currconfig = self.get_named_certs()
        newconfig = []

        for item in currconfig:
            icertfile = item.get("certFile")
            ikeyfile = item.get("keyFile")

            if icertfile != certfile and ikeyfile != keyfile:
                newconfig.append(item)

        print AtomicRegistryConfigManager._configchange + \
              "Deleting entry for named cert "\
              + certfile +\
              " and " +\
              keyfile +\
              "..."

        self.set_named_certs(newconfig)

        return

    # ** Section ends

    # * Default serving cert

    def get_default_cert(self):
        """I : Gets the default cert"""
        return [self._config["assetConfig"]["servingInfo"]["certFile"], self._config["assetConfig"]["servingInfo"]["keyFile"]]

    def set_default_cert(self, certfile, keyfile):
        """Sets the default certs"""

        print AtomicRegistryConfigManager._configchange + \
              "Altering default serving cert to " + \
              certfile +\
              " and " +\
              keyfile +\
              " ..."

        self._config["assetConfig"]["servingInfo"]["certFile"] = certfile
        self._config["assetConfig"]["servingInfo"]["keyFile"] = keyfile

        return

    # ** Section ends

    # * Section ends

    # * Authentication - Handles all config changes related to authentication

    def get_identity_providers(self):
        """I : Gets the identity providers"""
        return self._config["oauthConfig"]["identityProviders"]

    def set_identity_providers(self, value, append=True):
        """I : Sets the identity providers"""

        newconfig = None

        if append:

            currconfig = self.get_identity_providers()

            if currconfig is None:
                newconfig = value

            else:
                newconfig = currconfig + value
        else:
            newconfig = value

        self._config["oauthConfig"]["identityProviders"] = newconfig

        return

    def get_mappingmethods(self):
        """P : Gets a list of possible claim methods"""
        return ["claim", "lookup", "generate", "add"]

    def _validate_mappingmethod(self, mappingmethod):
        """Validates mapping method."""

        isvalid = False

        validmappingmethods = self.get_mappingmethods();

        for item in validmappingmethods:
            if mappingmethod == item:
                isvalid = True
        
        return isvalid

    def add_identityprovider_htpasswd(self, name, file, apiversion="v1", challenge=True, login=True, mappingmethod="claim"):
        """P: Adds htpassword identity provider"""

        if not self._validate_mappingmethod(mappingmethod):
            raise Exception("Invalid Mapping method.")

        toadd = [
            {
                "name": name,
                "challenge": challenge,
                "login": login,
                "mappingMethod": mappingmethod,
                "provider":
                {
                    "apiVersion": apiversion,
                    "kind": "HTPasswdPasswordIdentityProvider",
                    "file": file
                }
            }
        ]

        print AtomicRegistryConfigManager._configchange + \
              "Adding htpasswd identity provider " +\
              name +\
              " referring database file " +\
              file + \
              " ..."

        self.set_identity_providers(toadd)

        return

    def add_identityprovider_basicauth_remote(self, name, url, cafile=None, certfile=None, keyfile=None, apiversion="v1", challenge=True, login=True, mappingmethod="claim"):
        """P: Adds a remote basic auth provider"""

        if not self._validate_mappingmethod(mappingmethod):
            raise Exception("Invalid Mapping method.")

        toadd = [
            {
                "name": name,
                "challenge": challenge,
                "login": login,
                "mappingMethod": mappingmethod,
                "provider":
                    {
                        "apiVersion": apiversion,
                        "kind": "BasicAuthPasswordIdentityProvider",
                        "url": url
                    }
            }
        ]

        if cafile is not None:
            toadd[0]["provider"]["ca"] = cafile

        if certfile is not None:
            if keyfile is None:
                raise Exception("You need to provide certfile and keyfile together")
            else:
                toadd[0]["provider"]["certFile"] = certfile
                toadd[0]["provider"]["keyFile"] = keyfile

        print AtomicRegistryConfigManager._configchange + \
              "Adding basic auth remote provider " + name + " at " + url + " ..."
        self.set_identity_providers(toadd)

        return

    def add_identityprovider_requestheader(self, name, challengeurl, loginurl, clientca = None, apiversion="v1", challenge=True, login=True, mappingmethod="claim"):
        """P: Add a request header identity provider."""

        if not self._validate_mappingmethod(mappingmethod):
            raise Exception("Invalid Mapping method.")

        toadd = [
            {
                "name": name,
                "challenge": challenge,
                "login": login,
                "mappingMethod": mappingmethod,
                "provider":
                    {
                        "apiVersion": apiversion,
                        "kind": "RequestHeaderIdentityProvider",
                        "challengeURL": challengeurl,
                        "loginURL": loginurl,
                        "headers":
                        [
                            "X-Remote-User",
                            "SSO-User"
                        ],
                        "emailHeaders":
                        [
                            "X-Remote-User-Email"
                        ],
                        "nameHeaders":
                        [
                            "X-Remote-User-Display-Name"
                        ],
                        "preferredUsernameHeaders":
                        [
                            "X-Remote-User-Login"
                        ]
                    }
            }
        ]

        if clientca is not None:
            toadd[0]["provider"]["clientCA"] = clientca

        print " [CONFIGCHANGE] Adding request header auth provider " +\
              name +\
              " with challenge url : " +\
              challengeurl +\
              " and loginurl : " +\
              loginurl +\
              "..."

        self.set_identity_providers(toadd)

        return

    def add_identityprovider_ldap(self, apiversion="v1", challenge=True, login=True, mappingmethod="claim"):
        """Add an ldap provider."""
        # FIXME: Complete this method
        return

    def delete_identity_provider(self, name):
        """P: Deletes an identity provider based on name"""

        currconfig = self.get_identity_providers()
        newconfig = []

        for item in currconfig:
            if item["name"] != name:
                newconfig.append(item)

        print AtomicRegistryConfigManager._configchange + \
              "Removing entry for auth provider " +\
              name +\
              " ..."

        self.set_identity_providers(newconfig, append=False)

        return

    # Section Ends

    # * Test functions - Handles testing of the functionality of code

    def test_config(self):
        """Test the finalize config on a test yaml output file."""

        with open(self._oc_test_config, "w") as yamlfile:
                yamlfile.write(yaml.dump(self._config, default_flow_style=False))
        return

    # Finalize Function
    def finalize_config(self):
        """Writes the config back to config file, making it permanent"""

        with open(self._oc_master_config, "w") as ymlfile:
            ymlfile.write(yaml.dump(self._config, default_flow_style=False))

        return


class AtomicRegistryQuickstartSetup:
    """Class sets up the atomic registry"""

    def __init__(self, mode="--interactive"):
        """Initializes the objects by setting instance variables"""

        # Constants

        self._container_image = "projectatomic/atomic-registry-quickstart"  # The name of the container image
        #self._container_image = "mohammedzee1000/centos-atomic-registry-quickstart" # Actual FIXME: Set this up before shipping
        self._dn_or_ip = "localhost"
        #self._path_files = "/etc/origin/master/"
        self._path_files = os.path.abspath(".") # test FIXME : Set this up before shipping

        if mode == "--interactive" or mode == "-i":
            self._inp_mode = InpMode.interactive

        # Config params
        self._config_manager = AtomicRegistryConfigManager(drycreate=True)

        return

    def install_containers(self):
        """Installs the atomic registry containers"""

        cmd = ["sudo",
               "atomic",
               "install",
               self._container_image,
               self._dn_or_ip]

        print cmd  # test # FIXME : Change this before shipping
        #call(cmd)

        return

    def _copy_file(self, src):
        """Copies necessary file to the atomic registry directory."""

        print " ** Copying over necessary file..."
        copy2(src, self._path_files)

        return os.path.basename(src)

    def customize_interactive(self):

        # FIXME : Finish this method

        while True:

            print "MAIN\n"
            print "1. Customize Certificates"
            print "2. Customize Authentication"
            print "c. Commit configuration and continue"
            ch = raw_input(" >> ")
            print

            if ch == "1":

                while True:

                    print "MAIN > CERTS\n"
                    print "1. List named certificate"
                    print "2. Add named certificate"
                    print "3. Delete Named Certificate"
                    print "4. List current default serving certificate"
                    print "5. Modify default serving certificate"
                    print "b. Back"
                    ch1 = raw_input(" >> ")
                    print

                    if ch1 == "1":

                        pp.pprint(self._config_manager.get_named_certs())

                    elif ch1 == "2":

                        nckey = raw_input(" * Path of the key file : ")

                        if Validator.is_valid_file(nckey):
                            nccert = raw_input(" * Path of the cert file : ")

                            if Validator.is_valid_file(nccert):

                                ncnames = []

                                inp = raw_input(" * Domain names to associate with this pair (comma separated list : Leave empty if nothing) : ")

                                if len(inp) < 0:
                                    ncnames = None

                                else:

                                    ncnames = inp.split(',')

                                self._config_manager.add_named_cert(self._copy_file(nccert), self._copy_file(nckey), ncnames)

                    elif ch1 == "3":

                        # FIXME: Functional now make it cleaner
                        nccert = raw_input(" * Name (only) of the name certificate file : ")
                        nckey = raw_input(" * Name (only) of the corresponding name key file")

                        self._config_manager.delete_named_cert(nccert, nckey)

                    elif ch1 == "4":

                        print self._config_manager.get_default_cert()

                    elif ch1 == "b":

                        break

                    elif ch1 == "5":

                        nckey = raw_input(" * Path of the key file : ")

                        if Validator.is_valid_file(nckey):
                            nccert = raw_input(" * Path of the cert file : ")

                            if Validator.is_valid_file(nccert):
                                self._config_manager.set_default_cert(self._copy_file(nccert), self._copy_file(nckey))

                    else:

                        print "\nInvalid choice"

                    print "\n"

            elif ch == "2":

                while True:

                    print "MAIN > AUTH\n"
                    print "1. List Identity providers"
                    print "2. Add htpasswd identity provider"
                    print "3. Add Remote Basic Authentication identity provider"
                    print "4. Add Request Header Identity provider"
                    print "d. Delete Identity Provider"
                    print "b. Back"
                    ch2 = raw_input(" >> ")
                    print

                    if ch2 == "1":

                        pp.pprint(self._config_manager.get_identity_providers())

                    elif ch2 == "2":

                        nm = ""
                        while len(nm) < 4:
                            nm = raw_input(" * Name of the provider (atleast 4 characters) : ")

                        htpasswdfile = raw_input(" * Path of the htpasswd file : ")

                        if Validator.is_valid_file(htpasswdfile):
                            self._config_manager.add_identityprovider_htpasswd(nm, self._copy_file(htpasswdfile))

                    elif ch2 == "3":

                        # name, url, cafile, certfile, keyfile
                        nm = ""
                        while len(nm) < 4:
                            nm = raw_input(" * Name of the provider (atleast 4 characters) : ")

                        url = ""
                        while not Validator.is_valid_url(url, schemarequired=True):
                            url = raw_input(" * URL : ")

                    elif ch2 == "4":

                        print "a3"

                    elif ch2 == "d":

                        nm = ""
                        while len(nm) < 4:
                            nm = raw_input(" * Name of the provider (atleast 4 characters) : ")

                        self._config_manager.delete_identity_provider(nm)

                    elif ch2 == "b":

                        break

                    else:

                        print "\n Invalid choice"

                    print "\n"

            elif ch == "c":
                break
            else:
                print "\nInvalid choice"

            print "\n"

        return

    def customize(self):
        """Applying configuration changes to the atomic registry - based on user input"""

        self._config_manager = AtomicRegistryConfigManager()

        # FIXME : Finish this methed

        # Customize stuff based on user input
        if self._inp_mode == InpMode.interactive:
            self.customize_interactive()

        # Add default account if /root/cred present
        if os.path.exists("/root/cred"):
            users = {}
            default_htpasswd = self._path_files + "/" + "default.htpasswd"
            with open("./cred") as credfile:
                lineno = 0
                for line in credfile:
                    lineno += 1
                    if lineno % 2 != 0:
                        uname = line.partition("=")[2]
                        uname = uname.rstrip()
                        users[uname] = None
                    else:
                        passwd = line.partition("=")[2]
                        passwd = passwd.rstrip()
                        users[uname] = passwd

            with open(default_htpasswd, "w") as htpasswdfile:
                for user in users.keys():
                    thepass = users[user]
                    cmd = ["openssl", "passwd", "-apr1", thepass]
                    p = Popen(cmd, stdout=PIPE)
                    out, err = p.communicate()
                    htpasswdfile.write(user + ":" + out)
            self._config_manager.delete_identity_provider("anypassword")
            self._config_manager.add_identityprovider_htpasswd("system_default_auth", os.path.basename(default_htpasswd))

        self._config_manager.finalize_config()

        return

    def test_customize(self):
        """Applying configuration changes to the atomic registry - testing"""

        self._config_manager = AtomicRegistryConfigManager()

        # Customize stuff based on user input
        if self._inp_mode == InpMode.interactive:
            self.customize_interactive()

        # Add default account if /root/cred present
        if os.path.exists("./cred"):  # FIXME : Set path of cred file before shipping.
            users = {}
            default_htpasswd = self._path_files + "/" + "default.htpasswd"
            with open("./cred") as credfile:
                lineno = 0
                for line in credfile:
                    lineno += 1
                    if lineno % 2 != 0:
                        uname = line.partition("=")[2]
                        uname = uname.rstrip()
                        users[uname] = None
                    else:
                        passwd = line.partition("=")[2]
                        passwd = passwd.rstrip()
                        users[uname] = passwd

            with open(default_htpasswd, "w") as htpasswdfile:
                for user in users.keys():
                    thepass = users[user]
                    cmd = ["openssl", "passwd", "-apr1", thepass]
                    p = Popen(cmd, stdout=PIPE)
                    out, err = p.communicate()
                    htpasswdfile.write(user + ":" + out)
            self._config_manager.delete_identity_provider("anypassword")
            self._config_manager.add_identityprovider_htpasswd("system_default_auth", os.path.basename(default_htpasswd))

        self._config_manager.test_config()

        return

    def run_containers(self):
        """Runs the containers that have been installed"""

        cmd = ["sudo",
               "atomic",
               "run",
               self._container_image,
               self._dn_or_ip]

        print cmd  # test # FIXME : Change this before shipping
        #call(cmd)

        return

    def preinstall(self):
        """Gets the domain name or ip to be used to setup the atomic registry.."""
        if self._inp_mode == InpMode.interactive:

            inp = ""
            defval = "localhost"
            doi = "Domain Name or IP"

            while True:
                inp = raw_input(" ** What is the " +
                                doi +
                                " of the atomic registry service [" +
                                defval +
                                "] : ")

                if len(inp) == 0:
                    self._dn_or_ip = defval
                    break

                elif Validator.is_valid_url(inp, schemarequired=False):
                    self._dn_or_ip = inp
                    break

                else:
                    print " *E Invalid format of " + doi + ".\n"

        return

    def preins(self):



        return

def prereq():

    print "\033[1m"
    print "* \033[35mIMPORTANT:The script runs with certain assumptions. Please make sure following prereq are met before proceeding ..."
    print "\033[0m\033[1m"
    print " - If you want to use a default username or password, please make sure the same are present in /root/cred"
    print " - If you plan to use your own serving certificates, please make sure the same are loaded into this machine and that"
    print "   you have access to them. You need to provide the path of the certificate and it will be copied over."
    print " - The cert files, key files, authfiles (such as htpasswd) file are valid. The only validation that the script"
    print "   does against files is that they are actually files and and nothing more."
    print "\033[0m"

    while True:
        cnt = raw_input("\nAre you sure you wish to proceed (y/n) : ")

        if cnt == "y":
            break

        elif cnt == "n":
            print
            sys.exit(0)

    return

def main():
    """This is the main method"""

    prereq()

    print "\n Lets get started : \n"

    setup = AtomicRegistryQuickstartSetup()

    # Step 1 : Get the dn or ip
    print "\n * STEP 1 : Getting basic information needed to install atomic registry\n"
    setup.preinstall()
    print

    # Step 2 : Install the containers :
    print "\n * STEP 2 : Installing the registry : \n"
    setup.install_containers()

    # Step 3 : Customize the configurations
    print "\n * STEP 3 : Customizing : \n"
    setup.test_customize() # FIXME : Change to customize() before shipping

    # Step 4 : Run the containers :
    print "\n * STEP 4 : Running the registry : \n"
    setup.run_containers()

    print "\nA very good documentation is available at http://www.projectatomic.io/registry/ Please do got through the same."

    print

    return


if __name__ == '__main__':
    main()


# TODO : Check if all types for files are copied over and that only their names are being added in the config file