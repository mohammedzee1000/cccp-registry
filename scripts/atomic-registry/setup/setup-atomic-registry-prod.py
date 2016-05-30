#!/bin/python

import yaml
import os
import sys
from subprocess import call, Popen, PIPE
import re
from time import sleep
import pprint
from shutil import copy2
from urlparse import urlparse

pp = pprint.PrettyPrinter(indent=4)

# Globals Variables :


class InpMode:
    """Defines the input mode"""

    def __init__(self):

        return

    interactive = 1
    cmdline = 2


class Validator:
    """Handles validation tasks, such as url and file name validations"""

    def __init__(self):

        return

    @staticmethod
    def print_err(errmsg):
        """Prepends error message with appropriate label and prints it onto stdout"""

        theerror = "\n \033[1;31m[ERROR]\033[0m " + errmsg
        print theerror

        return

    @staticmethod
    def is_valid_file(pth):
        """Checks if a path is a valid file"""

        valid_file = True

        if not os.path.isabs(pth):

            Validator.print_err("Please provide absolute path, try again...")
            valid_file = False

        elif not os.path.exists(pth):

            Validator.print_err("The file path you provided does not exist, try again...")
            valid_file = False

        elif not os.path.isfile(pth):

            Validator.print_err("Please provide the path of a file, try again...")
            valid_file = False

        return valid_file

    @staticmethod
    def _is_valid_ip(ip):
        """Checks if an ip is of a valid format."""

        ipr = re.compile(
            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}"
            "([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(:[0-9].)?$")

        retval = True

        if ipr.match(ip) is None:
            retval = False

        return retval

    @staticmethod
    def _is_matchable_ip(ip):
        """Checks if a string is possibly an IP"""

        ipr = re.compile(
            "^((([0-9])+\.){3}([0-9]+)([:][0-9]+)?)"
        )

        retval = True

        if ipr.match(ip) is None:
            retval = False

        return retval

    @staticmethod
    def _is_valid_dn(dn):
        """Checks if a string is a valid domain name"""

        dnr = re.compile(
            "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
            "([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])(:[0-9].)?$")

        retval = True

        if dnr.match(dn) is None:
            retval = False

        return retval

    @staticmethod
    def is_valid_url(url, schemarequired=True):
        """Checks if a specified url is valid"""

        # Assume url is valid
        validurl = True

        # Parse the passed string to a url
        parsed_url = urlparse(url)
        uri = ""
        inval_reason = ""

        while True:

            # If both the network location and path components are empty then its not a valid url
            if len(parsed_url.netloc) == 0 and len(parsed_url.path) == 0:
                inval_reason = "URI or IP cannot be empty"
                validurl = False
                break

            # If the url needs a compulsory schema
            if schemarequired:
                # If it doesnt have a schema, then its not a valid url
                if not bool(parsed_url.scheme):
                    inval_reason = "Please specify a schema for example http://"
                    validurl = False
                    break

                # The main uri will be in netlocation otherwise it will be in path
                uri = parsed_url.netloc

            else:
                uri = parsed_url.path

            # If the uri is ip, check if its a valid ip, if not, its not a valid url
            if Validator._is_matchable_ip(uri) and not Validator._is_valid_ip(uri):
                inval_reason = "IP address is invalid"
                validurl = False
                break

            # Check if uri is a valid domain name
            elif not Validator._is_valid_dn(uri):
                inval_reason = "Domain name is invalid"
                validurl = False
                break

            else:
                break

        if not validurl:

            Validator.print_err(inval_reason + ", try again...\n")

        return validurl


class AtomicRegistryConfigManager:
    """Class contains the parameters used for customizing the atomic registry"""

    def __init__(self, drycreate=False):

        self._oc_master_config = "/etc/origin/master/master-config.yaml"
        self._oc_test_config = "temp.yaml"

        if not drycreate:
            with open(self._oc_master_config) as ymlfile:
                self._config = yaml.load(ymlfile)

        return

    @staticmethod
    def _print_configchange(changemsg):
        """Prepends a config change message with appropriate labels and prints it to stdout"""

        themsg = "\n \033[1;32m[CONFIGCHANGE]\033[0m " + changemsg
        print themsg

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
        if names is not None:
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
        self._print_configchange("Appending entry for named cert " + certfile + " and " + keyfile + "...")
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

        self._print_configchange(
            "Deleting entry for named cert " +
            certfile +
            " and " +
            keyfile +
            "..."
        )

        self.set_named_certs(newconfig)

        return

    # ** Section ends

    # * Default serving cert

    def get_default_cert(self):
        """I : Gets the default cert"""
        return [self._config["assetConfig"]["servingInfo"]["certFile"],
                self._config["assetConfig"]["servingInfo"]["keyFile"]]

    def set_default_cert(self, certfile, keyfile):
        """Sets the default certs"""

        self._print_configchange(
            "Altering default serving cert to " +
            certfile +
            " and " +
            keyfile +
            " ..."
        )

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

    @staticmethod
    def get_mappingmethods():
        """P : Gets a list of possible claim methods"""
        return ["claim", "lookup", "generate", "add"]

    def _validate_mappingmethod(self, mappingmethod):
        """Validates mapping method."""

        isvalid = False

        validmappingmethods = self.get_mappingmethods()

        for item in validmappingmethods:
            if mappingmethod == item:
                isvalid = True

        return isvalid

    def add_identityprovider_htpasswd(self, name, thehtpasswdfile, apiversion="v1", challenge=True, login=True,
                                      mappingmethod="claim"):
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
                        "file": thehtpasswdfile
                    }
            }
        ]

        self._print_configchange(
            "Adding htpasswd identity provider " +
            name +
            " referring database file " +
            thehtpasswdfile +
            " ..."
        )

        self.set_identity_providers(toadd)

        return

    def add_identityprovider_basicauth_remote(self, name, url, cafile=None, certfile=None, keyfile=None,
                                              apiversion="v1", challenge=True, login=True, mappingmethod="claim"):
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

        self._print_configchange(
            "Adding basic auth remote provider " +
            name +
            " at " +
            url +
            " ..."
        )
        self.set_identity_providers(toadd)

        return

    def add_identityprovider_requestheader(self, name, challengeurl, loginurl, clientca=None, apiversion="v1",
                                           challenge=True, login=True, mappingmethod="claim"):
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

        self._print_configchange("Adding request header auth provider " +
                                 name +
                                 " with challenge url : " +
                                 challengeurl +
                                 " and loginurl : " +
                                 loginurl +
                                 "..."
                                 )

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

        self._print_configchange(
            "Removing entry for auth provider " +
            name +
            " ..."
        )

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
        # self._container_image = "mohammedzee1000/centos-atomic-registry-quickstart"
        #  Actual FIXME: Set this up before shipping
        self._dn_or_ip = "localhost"
        self._path_files = "/etc/origin/master/"
        self._default_user = None

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

        call(cmd)

        return

    def _copy_file(self, src):
        """Copies necessary file to the atomic registry directory."""

        print " ** Copying over necessary file..."
        copy2(src, self._path_files)

        return os.path.basename(src)

    def customize_interactive(self):
        """Does customization of atomic registry interactively"""

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

                                inp = raw_input(" * Domain names to associate with this pair (comma separated list :"
                                                " Leave empty if nothing) : ")

                                if len(inp) < 0:
                                    ncnames = None

                                else:

                                    ncnames = inp.split(',')

                                self._config_manager.add_named_cert(self._copy_file(nccert), self._copy_file(nckey),
                                                                    ncnames)

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
                    print "README : http://docs.projectatomic.io/registry/latest/install_config/" \
                          "configuring_authentication.html\n"
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

                        nm = ""
                        while len(nm) < 4:
                            nm = raw_input(" * Name of the provider (atleast 4 characters) : ")

                        url = raw_input(" * URL ( https://www.example.com/remote-idp ) : ")

                        if Validator.is_valid_url(url):

                            cafile = raw_input(" * CA File (Leave empty if none) : ")

                            if len(cafile) == 0:

                                cafile = None

                            if cafile is None or (cafile is not None and Validator.is_valid_file(cafile)):

                                nckey = raw_input(" * Key File (Leave empty is none) : ")

                                if len(nckey) == 0:

                                    print " * Assuming cert file is empty as well"
                                    self._config_manager.add_identityprovider_basicauth_remote(nm, url, cafile, None,
                                                                                               None)

                                elif Validator.is_valid_file(nckey):

                                    cafile_tmp = None
                                    nccert = raw_input("* Cert File (Compulsory) : ")

                                    if len(nccert) == 0:

                                        Validator.print_err("You need to provide a cert file with a key file,"
                                                            " try again")

                                    elif Validator.is_valid_file(nccert):

                                        if cafile is not None:

                                            cafile_tmp = self._copy_file(cafile)

                                    self._config_manager.add_identityprovider_basicauth_remote(nm, url, cafile_tmp,
                                                                                               nccert, nckey)

                    elif ch2 == "4":

                        # Name, challengurl, loginurl, clientca
                        nm = ""
                        cafile_tmp = None
                        while len(nm) < 4:

                            nm = raw_input(" * Name of the provider (atleast 4 characters) : ")

                        challengeurl = raw_input(" * Challenge URL (https://www.example.com/challenging-proxy/oauth/"
                                                 "authorize?${query}) : ")

                        if Validator.is_valid_url(challengeurl, schemarequired=True):

                            loginurl = raw_input(" * Login URL (https://www.example.com/login-proxy/oauth/"
                                                 "authorize?${query}) : ")

                            if Validator.is_valid_url(loginurl):

                                cafile = raw_input(" * Client CA File (Leave empty if none) : ")

                                if len(cafile) == 0:

                                    cafile = None

                                if cafile is None or (cafile is not None and Validator.is_valid_file(cafile)):

                                    if cafile is not None:
                                        cafile_tmp = self._copy_file(cafile)

                                    self._config_manager.add_identityprovider_requestheader(nm, challengeurl, loginurl,
                                                                                            cafile_tmp)

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

    def _add_default_account(self):
        """Adds a default account if the cred file is present"""

        if os.path.exists("/root/cred"):
            users = {}
            default_htpasswd = self._path_files + "/" + "default.htpasswd"

            with open("/root/cred") as credfile:

                lineno = 0
                uname = ""
                for line in credfile:
                    lineno += 1
                    if lineno % 2 != 0:
                        uname = line.partition("=")[2]
                        uname = uname.rstrip()
                        users[uname] = None
                        self._default_user = uname
                    else:
                        passwd = line.partition("=")[2]
                        passwd = passwd.rstrip()
                        users[uname] = passwd

            users["pulluser"] = "pulluser@123"

            with open(default_htpasswd, "w") as htpasswdfile:

                for user in users.keys():
                    thepass = users[user]
                    cmd = ["openssl", "passwd", "-apr1", thepass]
                    p = Popen(cmd, stdout=PIPE)
                    out, err = p.communicate()
                    htpasswdfile.write(user + ":" + out)

            self._config_manager.delete_identity_provider("anypassword")
            self._config_manager.add_identityprovider_htpasswd("system_default_auth",
                                                               os.path.basename(default_htpasswd))

        return

    @staticmethod
    def _create_scripts():
        """Creates some scripts to be used after the install"""

        scriptspath = "/root"
        ocmscript = scriptspath + "/" + "ocm"

        ocmdata = "#!/bin/bash\n# Generated by Atomic Registry Setup Script\n"
        ocmdata += "ORIGIN_CONTAINER=`sudo docker ps | grep \"/usr/bin/openshift s\" | cut -d \" \" -f1`\n"
        ocmdata += "CMD=$@\n"
        ocmdata += "sudo docker exec -i ${ORIGIN_CONTAINER} ${CMD}"

        with open(ocmscript, "w") as ocmfile:
            ocmfile.write(ocmdata)

        os.chmod(ocmscript, 4755)

        return

    def customize(self):
        """Applying configuration changes to the atomic registry - based on user input"""

        self._config_manager = AtomicRegistryConfigManager()

        # FIXME : Finish this methed

        # Customize stuff based on user input
        if self._inp_mode == InpMode.interactive:
            self.customize_interactive()

        # Add default account if /root/cred present
        self._add_default_account()

        # Create some scripts to ease users pain of managing origin container.
        self._create_scripts()

        self._config_manager.finalize_config()

        return

    def run_containers(self):
        """Runs the containers that have been installed"""

        cmd = ["sudo",
               "atomic",
               "run",
               self._container_image,
               self._dn_or_ip]

        call(cmd)

        return

    def _default_user_grantadminrights(self):
        """Grants default user, admin rights"""

        if self._default_user is not None:
            print "Grant admin rights to user " + self._default_user + "\n"
            cmd = ["sudo", "/root/ocm", "oadm", "policy", "add-cluster-role-to-user", "cluster-admin",
                   self._default_user]
            call(cmd)

        return

    def postinstall(self):
        """Runs post install actions"""

        self._default_user_grantadminrights()

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

        return


def prereq():

    usr = os.getenv("USER")
    sudo_usr = os.getenv("SUDO_USER")

    if usr != "root" and sudo_usr is None:
        Validator.print_err("Please run the script as root or a sudo user.\n")
        sys.exit(1)

    print "\033[1m"
    print "* \033[35mIMPORTANT:The script runs with certain assumptions. Please make sure following prereq are met" \
          " before proceeding ..."
    print "\033[0m\033[1m"
    print " - If you want to use a default username or password, please make sure the same are present in /root/cred."
    print "   The first username is this file will automatically be granted full admin rights over the registry"
    print " - If you plan to use your own serving certificates, please make sure the same are loaded into this" \
          " machine and that"
    print "   you have access to them. You need to provide the path of the certificate and it will be copied over."
    print " - The cert files, key files, authfiles (such as htpasswd) file are valid. The only validation that the" \
          " script"
    print "   does against files is that they are actually files and and nothing more."
    print " - Please ensure ports 443, 8443 and 5000 are open and can be accessed."
    print " - Please ensure storage needed for containers, if any is mounted at /var/lib/origin. You can create the" \
          " folders, if required, with mkdir -p /var/lib/origin"
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
    setup.customize()

    # Step 4 : Run the containers :
    print "\n * STEP 4 : Running the registry : \n"
    setup.run_containers()

    # Wait for short duration for containers to come up:
    print
    for i in range(0, 180, 20):
        print "Waiting for containers to come up (" + str(180-i) + " secs remaining)"
        sleep(20)

    # Step 5: Post install
    print "\n"
    print "\n * STEP 5 : Doing some post install ops : \n"
    setup.postinstall()

    print "\nA very good documentation is available at http://www.projectatomic.io/registry/" \
          " Please do got through the same."

    print

    return


if __name__ == '__main__':
    main()

    # TODO : Check if all types for files are copied over and that only their names are being added in the config file
