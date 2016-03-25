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


# Globals

## The untouchables
F_REGCONF="/etc/docker-registry.yml";
F_SSLCONF="/etc/httpd/conf.d/ssl.conf";
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
#wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm &> /dev/null;
#yum localinstall epel-release-latest-7.noarch.rpm -y &> /dev/null;
#rm -rf epel-release-latest-7.noarch.rpm &> /dev/null;
printf " [$DONE] ";
echo;


# Install nessasary packages
printf " * Installing nessasary packages\t";
yum install docker docker-registry httpd mod_ssl firewalld git letsencrypt -y &> /dev/null;
printf " [$DONE] ";
echo;

# Generating nessasary certificates

##############################################################################################

echo "###########################################Basic Setup Complete requires some reconfiguration";
echo "Edit $F_REGCONF, set local \n storage_path = /path/to/loads/of/storage";
echo "Generate SSL Cert : openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ca.key -out ca.crt";
echo "In the questionnaire, make sure you set the common name to the fqdn that users will use to get to service";
echo "Copy the files to appropriate locations in /etc/pki/tls/certs/ca.crt and /etc/pki/tls/private/ca.key"
echo "Also paste the ca.crt somewhere publically available such as http server";
echo "Edit $F_SSLCONF to include following information before </VirtualHost>";
echo;
echo "<VirtualHost *:443>";
echo "SSLInsecureRenegotiation=false";
echo "ServerName=fqdn users will use to get to your service";
echo -e "ProxyRequests off\nProxyPreserveHost on\nProxyPass / http://127.0.0.1:5000/\nProxyPassReverse / http://127.0.0.1:5000/";
echo -e "<Location />\nOrder deny,allow\nAllow from all\nAuthName 'Registry Authentication'\nAuthType basic\n";
echo -e ""
echo -e "<Limit PUT>\nRequire valid-user\n</Limit>\n";
