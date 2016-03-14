#!/bin/bash

#################################################################################################################
# This script sets up docker registry for								        #
# Centos Container Pipeline.                                                                                    #
#                                                                                                               #
#            AUTHOR : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com                                        #
#################################################################################################################


# Check sudo access
SUDO=''
if (( $EUID != 0 )); then
        #rerun self as root
        sudo bash $0;
        exit 0;
fi


## The untouchables
DONE="\x1b[32mDONE\x1b[0m";

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


# Download and install nessasary repos
printf " * Setting up nessasary repositories\t  ";
yum install wget -y &> /dev/null;
wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm &> /dev/null;
yum localinstall epel-release-latest-7.noarch.rpm -y &> /dev/null;
rm -rf epel-release-latest-7.noarch.rpm &> /dev/null;
printf " [$DONE] ";
echo;


# Install nessasary packages
printf " * Installing nessasary packages\t";
yum install docker docker-registry httpd mod_ssl -y &> /dev/null;
printf " [$DONE] ";
echo;


