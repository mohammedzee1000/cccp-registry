#!/bin/bash

#################################################################################################################
# This script sets up pulpadmin on systems acting as pulp-admin clients for pulpadmin setup on devcloud for     #
# Centos Container Pipeline.											#
# 														#
#	MAINTAINER : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com						#
#################################################################################################################


# Check sudo access
SUDO=''
if (( $EUID != 0 )); then
        #rerun self as root
	sudo bash $0;
	exit 0;
fi

#GLOBALS - END USER ONLY NEEDS TO MOD THESE
PULPSERVER="172.29.32.79";
PULP_VERIFYSSL="false";
REPO="rhel"; # other option is fedora

# Warn user to do his updates
proceed="z";

while true; do
	echo;
	echo "Please ensure your system is upto date and rebooted if needed";
	echo "You may run 'yum update -y' to do so.";
	printf "Proceed with setup (y/n) : ";
	read proceed;
	#echo $proceed; #TEST
	echo
	if [ "$proceed" = "y" ]; then 
		break;
	elif [ "$proceed" = "n" ]; then
		exit 0;
	fi
done

#echo "test"; #TEST

# Download and install nessasary repos
printf "Setting up nessasary repositories\t";
yum install wget -y &> /dev/null;
wget https://repos.fedorapeople.org/repos/pulp/pulp/`echo $REPO`-pulp.repo -O /etc/yum.repos.d/`echo $REPO`-pulp.repo &> /dev/null;
sudo yum install http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm &> /dev/null;
printf "[DONE]";
echo;

#Install pulp admin client
printf "";


