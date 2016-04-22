#!/usr/bin/python
# Author Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com)
# Run this after atomic install projectatomic/atomic-registry-quickstart or mohammedzee1000/centos-atomic-registry
# Before executing a run and ensuring the htpasswd file exists at /etc/origin/master/

import yaml
import sys
import os

# * Initialize nessasary parameters

fname = "/etc/origin/master/master-config.yaml" # Name of the origin master config file
#fname = "test.yaml" #TEST

htpassfile = "/etc/origin/master/users.htpasswd" # The password file where the users password will be saved.
#htpassfile = "./thepass" #TEST

# * Check if the htpasswd file exists where it is supposed to be.
if not os.path.exists(htpassfile):
    print "Please ensure that the htpass file is copied to " + htpassfile + " and then rerun"
    exit(1);

# * Open the origin config file for modification
with open(fname) as ymlfile:
    ymlcontent = yaml.load(ymlfile)

# * Modify appropriate yaml entires
ymlcontent["oauthConfig"]["identityProviders"][0]["name"]="htpasswd_auth"
ymlcontent["oauthConfig"]["identityProviders"][0]["provider"]["kind"]="HTPasswdPasswordIdentityProvider"
ymlcontent["oauthConfig"]["identityProviders"][0]["provider"]["file"]=htpassfile

# * Dump the changes back to config file
with open(fname, "w") as targetyml:
    yaml.dump(ymlcontent, targetyml)
