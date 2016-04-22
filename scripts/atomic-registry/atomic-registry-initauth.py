#!/usr/bin/python
# Author Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com)
# Run this after atomic install projectatomic/atomic-registry-quickstart or mohammedzee1000/centos-atomic-registry
# Before executing a run

import yaml
import sys
import os

# * Initialize nessasary parameters

fname = "/etc/origin/master/master-config.yaml" # Name of the origin master config file
#fname = "test.yaml" #TEST

passwd = sys.argv[1] # The password as supplied by the user.

htpassfile = "/etc/origin/master/users.htpasswd" # The password file where the users password will be saved.
#htpassfile = "./thepass" #TEST

# Check if the path for htpasswd file is absolute, if not make it so
if not os.path.isabs(htpassfile):
    htpassfile = os.path.abspath(htpassfile)

# Open the origin config file for modification
with open(fname) as ymlfile:
    ymlcontent = yaml.load(ymlfile)

# Modify appropriate yaml entires
ymlcontent["oauthConfig"]["identityProviders"][0]["name"]="htpasswd_auth"
ymlcontent["oauthConfig"]["identityProviders"][0]["provider"]["kind"]="HTPasswdPasswordIdentityProvider"
ymlcontent["oauthConfig"]["identityProviders"][0]["provider"]["file"]=htpassfile

# Generate the commande echo "passwd" | htpasswd -ci htpassfile admin 
htpasscmd = ("/usr/bin/echo " +
             passwd + 
             " | "
             "/usr/bin/htpasswd -ci " +
             htpassfile + 
             " admin") 

# Execute the command
from subprocess import call
call(htpasscmd, shell=True)

# Dump the changes back to config file
with open(fname, "w") as targetyml:
    yaml.dump(ymlcontent, targetyml)
