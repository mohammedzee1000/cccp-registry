#!/bin/python

# imports
import ConfigParser
import os
from enum import Enum
import  sys
from subprocess import call
import re

# CA SPECIFTC - USER MODIFIES THESE

# Base variables
# CA_LOC = "/root" # ACTUAL
CA_LOC = "." # TEST

SUBJ_COUNTRY = "GB"
SUBJ_STATEORPROVINCE = "England"
SUBJ_LOCALITY = ""
SUBJ_ORGNAME = "CentOS Devcloud"
SUBJ_OU = "CCCP"
SUBJ_EMAIL = "test@cccp.org"

# Consts - UNTOUCHABLES
# * ROOT CA CERTS
CA_CERT = "ca.cert.pem"     # The name of the root CA pair cert
CA_KEY = "ca.key.pem"   # The name of the root CA pair key
CA_CRL = "ca.crl.pem"   # The name of the root CA pair crl

# * INTERMEDIATE CA CERTS
INT_CERT = "intermediate.cert.pem"  # The name of the intermediate CA pair cert
INT_KEY = "intermediate.key.pem"    # The name of intermediate CA pair key
INT_CRL = "intermediate.crl.pem"    # The name of the intermediate CA pair crl

# * DIRECTORY AND FILES TO BE CREATED
CA_DIR_CERTS = "certs"  # The name of the dir containing the certs
CA_DIR_CRL = "crl"  # The name of the dir containing the certificate Revocation List
CA_DIR_NEWCERTS = "newcerts"    # The name of the directory containing new certificates
CA_DIR_PRIVATE = "private"  # The name of the directory containing the private keys
CA_DIR_CSR = "csr"  # The name of the
CA_FILE_INDEX = "index.txt"     # The flat file containing the database of the certs
CA_FILE_SERIAL = "serial"   # The flat file containing the current serial no of the certs
CA_FILE_CRLNUMBER = "crlnumber"     # The flat file containing the CRL number of the certs
CA_FILE_CNF = "openssl.cnf"     # The name of the config file

# Derived
CA_DIR = CA_LOC + "/ca"     # The path of the root CA.
INT_DIR = CA_DIR + "/intermediate"      # The path of the intermediate CA.

class CAMODE(Enum):
    """This enumeration defines the mode of operation of come of the functions that operate stuff common to root CA or intermediate CA."""
    root = 1
    intermediate = 2

class INPMODE(Enum):
    """This enumeration defines the mode of the input of the various settings."""
    inscript = 1
    cmdargs = 2
    interactive = 3

def createdir(path, mode=None):
    """Checks if a specified path exists, if not, creates it."""
    if os.path.exists(path):
        print "DIRCREATE : Path " + path + " already exists, skipping"
        if mode != None:
            os.chmod(path, mode)
    else:
        if mode != None:
            os.mkdir(path, mode)
        else:
            os.mkdir(path)
    return

def touchfile(filename,text):
    """Touches a file and then writes some text into it, could be an empty string"""
    target = open(filename, "w")
    target.write(text)
    target.close()
    return

def initcadirs(camode):
    """Does some initialization for the CA such as creating directories, creating some database files and so on."""
    thedir = ""

    if camode == CAMODE.root:
        thedir = CA_DIR
    elif camode == CAMODE.intermediate:
        thedir = INT_DIR
    else:
        raise Exception("Invalid mode of function call specified")

    createdir(thedir)

    # Common files and directories for all CAs
    createdir(thedir + "/" + CA_DIR_CERTS)
    createdir(thedir + "/" + CA_DIR_CRL)
    createdir(thedir + "/" + CA_DIR_NEWCERTS)
    createdir(thedir + "/" + CA_DIR_PRIVATE, 700)
    touchfile(thedir + "/" + CA_FILE_INDEX, "")
    touchfile(thedir + "/" + CA_FILE_SERIAL, "1000\n")

    # Only for intermediate CAs
    if camode == CAMODE.intermediate:
        touchfile(thedir + "/" + CA_FILE_CRLNUMBER, "1000\n")
        createdir(thedir + "/" + CA_DIR_CSR)

    return

def initcaconfig(camode):
    """This function initializes the openssl.cnf files needed for certificate generation."""
    thedir = ""
    privkey = ""
    cert = ""
    crl = ""
    cadefpolicy="policy_"

    if camode == CAMODE.root:
        thedir = CA_DIR
        privkey = CA_KEY
        cert = CA_CERT
        crl = CA_CRL
        cadefpolicy = cadefpolicy + "strict"
    elif camode == CAMODE.intermediate:
        thedir = INT_DIR
        privkey = INT_KEY
        cert = INT_CERT
        crl = INT_CRL
        cadefpolicy = cadefpolicy + "loose"
    else:
        raise Exception("Invalid mode of function call specified")

    cnffile = thedir + "/" + CA_FILE_CNF

    config = ConfigParser.RawConfigParser()

    # Section ca
    currsec = "ca"
    config.add_section(currsec)
    config.set(currsec, "default_ca", "CA_default")

    # Section CA_Default
    currsec = "CA_default"
    config.add_section(currsec)
    config.set(currsec, "dir", thedir)
    config.set(currsec, "certs", "$dir/" + CA_DIR_CERTS)
    config.set(currsec, "crl_dir", "$dir/" + CA_DIR_CRL)
    config.set(currsec, "newcerts_dir", "$dir/" + CA_DIR_NEWCERTS)
    config.set(currsec, "database", "$dir/" + CA_FILE_INDEX)
    config.set(currsec, "serial", "$dir/" + CA_FILE_SERIAL)
    config.set(currsec, "RANDFILE", "$dir/" + CA_DIR_PRIVATE + "/" + ".rand")
    config.set(currsec, "private_key", "$dir/" + CA_DIR_PRIVATE + "/" + privkey)
    config.set(currsec, "certificate", "$dir/" + CA_DIR_CERTS + "/" + cert)
    config.set(currsec, "crlnumber", "$dir/" + CA_FILE_CRLNUMBER)
    config.set(currsec, "crl", "$dir/" + crl)
    config.set(currsec, "crl_extensions", "crl_ext")
    config.set(currsec, "default_crl_days", "30")
    config.set(currsec, "default_md", "sha256")
    config.set(currsec, "name_opt", "ca_default")
    config.set(currsec, "cert_opt", "ca_default")
    config.set(currsec, "default_days", "375")
    config.set(currsec, "preserve", "no")
    config.set(currsec, "policy", cadefpolicy)

    # Section policy_strict
    currsec = "policy_strict"
    config.add_section(currsec)
    config.set(currsec, "countryName", "match")
    config.set(currsec, "stateOrProvinceName", "match")
    config.set(currsec, "organizationName", "match")
    config.set(currsec, "organizationalUnitName", "optional")
    config.set(currsec, "commonName", "supplied")
    config.set(currsec, "emailAddress", "optional")

    # Section policy_loose
    currsec = "policy_loose"
    config.add_section(currsec)
    config.set(currsec, "countryName", "optional")
    config.set(currsec, "stateOrProvinceName", "optional")
    config.set(currsec, "organizationName", "optional")
    config.set(currsec, "organizationalUnitName", "optional")
    config.set(currsec, "commonName", "supplied")
    config.set(currsec, "emailAddress", "optional")

    # Section req
    currsec = "req"
    config.add_section(currsec)
    config.set(currsec, "default_bits", "2048")
    config.set(currsec, "distinguished_name", "req_distinguished_name")
    config.set(currsec, "string_mask", "utf8only")
    config.set(currsec, "default_md", "sha256")
    config.set(currsec, "x509_extensions", "v3_ca")

    # Section req_distinguished_name
    currsec = "req_distinguished_name"
    config.add_section(currsec)
    config.set(currsec, "countryName", "Country Name (2 letter code)")
    config.set(currsec, "stateOrProvinceName", "State or Province Name")
    config.set(currsec, "localityName", "Locality Name")
    config.set(currsec, "0.organizationName", "Organization Name")
    config.set(currsec, "organizationalUnitName", "organizational Unit Name")
    config.set(currsec, "emailAddress", "Email Address")

    # Section req_distinguished_name defaults
    config.set(currsec, "countryName_default", SUBJ_COUNTRY)
    config.set(currsec, "stateOrProvinceName_default", SUBJ_STATEORPROVINCE)
    config.set(currsec, "localityName_default", SUBJ_LOCALITY)
    config.set(currsec, "0.organizationName_default", SUBJ_ORGNAME)
    config.set(currsec, "organizationalUnitName_default", SUBJ_OU)
    config.set(currsec, "emailAddress_default", SUBJ_EMAIL)

    # Section v3_ca
    currsec = "v3_ca"
    config.add_section(currsec)
    config.set(currsec, "subjectKeyIdentifier", "hash")
    config.set(currsec, "authorityKeyIdentifier", "keyid:always,issuer")
    config.set(currsec, "basicConstraints", "critical, CA:true")
    config.set(currsec, "keyUsage", "critical, digitalSignature, cRLSign, keyCertSign")

    # Section v3_intermediate_ca
    currsec = "v3_intermediate_ca"
    config.add_section(currsec)
    config.set(currsec, "subjectKeyIdentifier", "hash")
    config.set(currsec, "authorityKeyIdentifier", "keyid:always,issuer")
    config.set(currsec, "basicConstraints", "critical, CA:true, pathlen:0")
    config.set(currsec, "keyUsage", "critical, digitalSignature, cRLSign, keyCertSign")

    # Section usr_cert
    currsec = "usr_cert"
    config.add_section(currsec)
    config.set(currsec, "basicConstraints", "CA:false")
    config.set(currsec, "nsCertType", "client, email")
    config.set(currsec, "nsComment", "\"OpenSSL Generated Client Certificate\"")
    config.set(currsec, "subjectKeyIdentifier", "hash")
    config.set(currsec, "authorityKeyIdentifier", "keyid:always,issuer")
    config.set(currsec, "keyUsage", "critical, nonRepudiation, digitalSignature, keyEncipherment")
    config.set(currsec, "extendedKeyUsage", "clientAuth, emailProtection")

    # Section server_cert
    currsec = "server_cert"
    config.add_section(currsec)
    config.set(currsec, "basicConstraints", "CA:false")
    config.set(currsec, "nsCertType", "server")
    config.set(currsec, "nsComment", "\"OpenSSL Generated Server Certificate\"")
    config.set(currsec, "subjectKeyIdentifier", "hash")
    config.set(currsec, "authorityKeyIdentifier", "keyid,issuer:always")
    config.set(currsec, "keyUsage", "critical, digitalSignature, keyEncipherment")
    config.set(currsec, "extendedKeyUsage", "serverAuth")

    # Section crl_ext
    currsec = "crl_ext"
    config.add_section(currsec)
    config.set(currsec, "authorityKeyIdentifier", "keyid:always")

    # Section oscp
    currsec = "oscp"
    config.add_section(currsec)
    config.set(currsec, "basicConstraints", "CA:false")
    config.set(currsec, "subjectKeyIdentifier", "hash")
    config.set(currsec, "authorityKeyIdentifier", "keyid,issuer")
    config.set(currsec, "keyUsage", "critical, digitalSignature")
    config.set(currsec, "extendedKeyUsage", "OCSPSigning")

    # Write the config changes to config file
    with open(cnffile, 'wb') as configfile:
        config.write(configfile)

    return

def getinp_helper_country():

    return

def getinp_interactive():
    """This function does the input in case of interactive mode."""
    global CA_LOC, SUBJ_COUNTRY, SUBJ_EMAIL, SUBJ_STATEORPROVINCE, SUBJ_LOCALITY, SUBJ_ORGNAME, SUBJ_OU

    print "Hi, lets get started : "

    # Get location of the CA.
    inp = raw_input("* Where do you want me to put all my work [Def : " + CA_LOC + "] : ")
    if len(inp) == 0:
        inp = CA_LOC
    if os.path.exists(inp):
        print "** Found it"
        if os.path.isdir(inp):
            #print "testing" # test
            CA_LOC = inp
            #print CA_LOC #test
        else:
            print "**E " + inp + " needs to be a directory :("
            sys.exit(3)

    else:
        try:
            os.mkdir(inp)
        except OSError:
            print "** Damn sorry, cannot create that :("
            sys.exit(3)

    # Get the default country for the CA.
    ptn = re.compile("^[A-Z]{2}$")
    while True:
        inp = raw_input("What is the CA's Country Code (2 Capital Letters) [" + SUBJ_COUNTRY + "] : ")

        if len(inp) == 0:
            break

        if ptn.match(inp) != None:
            SUBJ_COUNTRY = inp
            break

    # Get the default state or province
    inp = raw_input("What is the CA's state or province [" + SUBJ_STATEORPROVINCE + "] : ")

    if len(inp) > 0:
        SUBJ_STATEORPROVINCE = inp

    # Get the default Locality
    inp = raw_input("What is the CA's Locality [" + SUBJ_LOCALITY + "] : ")

    if len(inp) > 0:
        SUBJ_LOCALITY = inp

    # Get the default Org Name
    inp = raw_input("What is the CA's Organization Name [" + SUBJ_ORGNAME + "] : ")

    if len(inp) > 0:
        SUBJ_ORGNAME = inp

    # Get the default OU
    inp = raw_input("Whats the CA's OU : [" + SUBJ_OU + "] : ")

    if len(inp) > 0:
        SUBJ_OU = inp

    # Get the default email

    return

def getinp(inpmode):
    """This function takes the input mode and sets the parameters needed for the CA."""
    # FIXME : Finish this function

    if inpmode == INPMODE.cmdargs:
        print "test"
    elif inpmode == INPMODE.interactive:
        getinp_interactive()
    elif inpmode == INPMODE.inscript:
        print "test"
    else:
        raise Exception("Invalid mode of function call.")

    print "* Alight let me finish the job for you. :)"

    return

def usage():
    print "\nUsage : " + sys.argv[0] + " [--in-script | -s | --interactive | -i | --args | -a] [PARAMS]"
    print "         " + "PARAMS (if --args or -a specified) - [caroot] [city] [location]"
    print "\n"
    sys.exit(2)
    return

# Main section begins :

def main():
    """This is the main function of this script."""
    # Globals :
    global CA_LOC, CA_DIR, INT_DIR

    # Check input mode :
    if len(sys.argv) < 2:
        usage()

    MD = sys.argv[1]

    if MD == "--in-script" or MD == "-s":
        getinp(INPMODE.inscript)
    elif MD == "--interactive" or MD == "-i":
        getinp(INPMODE.interactive)
    elif MD == "--args" or MD == "-a":
        getinp(INPMODE.cmdargs)
    elif MD == "--help" or MD == "-h":
        usage()
    else:
        usage()

    #os.rmdir(CA_DIR)

    CA_LOC = os.path.abspath(CA_LOC)

    # Derived - Reassign
    CA_DIR = CA_LOC + "/ca"
    INT_DIR = CA_DIR + "/intermediate"

    # Set up root CA.
    initcadirs(CAMODE.root)
    initcaconfig(CAMODE.root)

    # Set up intermediate CA
    initcadirs(CAMODE.intermediate)
    initcaconfig(CAMODE.intermediate)

    print  "\nOperation Completed\n"
    return

if __name__ == '__main__':
    main()