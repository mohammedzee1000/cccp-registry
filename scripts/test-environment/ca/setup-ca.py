#!/bin/python

# imports
import ConfigParser
import os
from enum import Enum
from subprocess import call

# CA SPECIFTC - USER MODIFIES THESE

# Base variables
# CA_LOC = "/root" # ACTUAL
CA_LOC = "." # TEST

# Consts - UNTOUCHABLES
# * ROOT CA CERTS
CA_CERT = "ca.cert.pem"
CA_KEY = "ca.key.pem"
CA_CRL = "ca.crl.pem"

# * INTERMEDIATE CA CERTS
INT_CERT = "intermediate.cert.pem"
INT_KEY = "intermediate.key.pem"
INT_CRL = "intermediate.crl.pem"

# * DIRECTORY AND FILES TO BE CREATED
CA_DIR_CERTS = "certs"
CA_DIR_CRL = "crl"
CA_DIR_NEWCERTS = "newcerts"
CA_DIR_PRIVATE = "private"
CA_DIR_CSR = "csr"
CA_FILE_INDEX = "index.txt"
CA_FILE_SERIAL = "serial"
CA_FILE_CRLNUMBER = "crlnumber"
CA_FILE_CNF = "openssl.cnf"

# Derived
CA_DIR = CA_LOC + "/ca"
INT_DIR = CA_DIR + "/intermediate"

class CAMODE(Enum):
    """This enumeration defines the mode of operation of come of the functions that operate stuff common to root CA or intermediate CA."""
    root = 1
    intermediate = 2

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
    """Touches a file and then writes some text into it, could be an enpty string"""
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

    # Write the config changes to config file
    with open(cnffile, 'wb') as configfile:
        config.write(configfile)

    return

#os.rmdir(CA_DIR)

# Set up root CA.
initcadirs(CAMODE.root)
initcaconfig(CAMODE.root)

# Set up intermediate CA
initcadirs(CAMODE.intermediate)
initcaconfig(CAMODE.intermediate)
