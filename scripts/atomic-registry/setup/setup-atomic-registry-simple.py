#!/bin/python

import yaml
import os
import sys
from subprocess import call, Popen, PIPE
import re
from time import sleep
import pprint
from urlparse import urlparse

pp = pprint.PrettyPrinter(indent=4)


def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(str, quoted_presenter)


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


class AtomicRegistrySetupSimple:

    def __init__(self):

        self._oc_master_config = "/etc/origin/master/master-config.yaml"
        self._oc_test_config = "temp.yaml"

        self._config = None

        # self._containerImage = "projectatomic/atomic-registry-quickstart"  # The name of the container image
        # self._containerImage = "mohammedzee1000/centos-atomic-registry-quickstart"
        self._containerImage = "registry.centos.org/atomic-registry/c7-atomic-registry-quickstart"
        #  Actual FIXME: Set this up before shipping
        self._dNOrIP = "localhost"
        self._filesPath = "/etc/origin/master/"
        self._defaultUser = None

        return

    def initconfig(self):

        with open(self._oc_master_config) as ymlfile:
            self._config = yaml.load(ymlfile)

        return

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

    def delete_identity_provider(self, name):
        """P: Deletes an identity provider based on name"""

        currconfig = self.get_identity_providers()
        newconfig = []

        for item in currconfig:
            if item["name"] != name:
                newconfig.append(item)

        self.set_identity_providers(newconfig, append=False)

        return

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

        self.set_identity_providers(toadd)

        return

    # Finalize Function
    def finalize_config(self):
        """Writes the config back to config file, making it permanent"""

        with open(self._oc_master_config, "w") as ymlfile:
            ymlfile.write(yaml.dump(self._config, default_flow_style=False))

        return

    def install_containers(self):
        """Installs the atomic registry containers"""

        cmd = ["sudo",
               "atomic",
               "install",
               self._containerImage,
               self._dNOrIP]

        call(cmd)

        return

    def _add_default_account(self):
        """Adds a default account if the cred file is present"""

        default_htpasswd = self._filesPath + "/" + "default.htpasswd"
        users = {}

        if os.path.exists("/root/cred"):

            with open("/root/cred") as credfile:

                lineno = 0
                uname = ""
                for line in credfile:
                    lineno += 1
                    if lineno % 2 != 0:
                        uname = line.partition("=")[2]
                        uname = uname.rstrip()
                        users[uname] = None
                        self._defaultUser = uname
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

        self.delete_identity_provider("anypassword")
        self.add_identityprovider_htpasswd("system_default_auth", os.path.basename(default_htpasswd))

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

    def run_containers(self):
        """Runs the containers that have been installed"""

        cmd = ["sudo",
               "atomic",
               "run",
               self._containerImage,
               self._dNOrIP]

        call(cmd)

        return

    def _default_user_grantadminrights(self):
        """Grants default user, admin rights"""

        if self._defaultUser is not None:
            print "Grant admin rights to user " + self._defaultUser + "\n"
            cmd = ["sudo", "/root/ocm", "oadm", "policy", "add-cluster-role-to-user", "cluster-admin",
                   self._defaultUser]
            call(cmd)

        return

    def postinstall(self):
        """Runs post install actions"""

        self._default_user_grantadminrights()

        return

    def preinstall(self):
        """Gets the domain name or ip to be used to setup the atomic registry.."""

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
                self._dNOrIP = defval
                break

            elif Validator.is_valid_url(inp, schemarequired=False):
                self._dNOrIP = inp
                break

        return

    def customize(self):

        self._add_default_account()
        self._create_scripts()
        self.finalize_config()

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


def mainf():

    prereq()

    print "\n Lets get started : \n"

    setup = AtomicRegistrySetupSimple()

    # Step 1 : Get the dn or ip
    print "\n * STEP 1 : Getting basic information needed to install atomic registry\n"
    setup.preinstall()
    print

    # Step 2 : Install the containers :
    print "\n * STEP 2 : Installing the registry : \n"
    setup.install_containers()
    setup.initconfig()

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


if __name__ == '__main__':
    mainf()