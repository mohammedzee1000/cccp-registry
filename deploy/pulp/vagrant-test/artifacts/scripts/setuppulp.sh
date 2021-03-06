#!/bin/bash

#################################################################################################################
# This script sets up pulp on systems acting as pulp server on devcloud	 for the			        #
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

PULP_VERIFYSSL="False";
PULPADMINPASS="admin@123"; #set the password before before running this script
PULPSERVER="server.pulpserver"
### Keep one active
REPO="rhel";
#REPO="fedora"; 
F_PULPREPO="/etc/yum.repos.d/pulp.repo";

## The untouchables
DONE="DONE"
PULPADMIN="admin";
F_INJECTFILE="/tmp/pulp_config_toinject";
F_PULPSERVER="/etc/pulp/server.conf";
#F_LOG="/var/log/"
#F_PULPADMIN="/etc/pulp/admin/admin.conf"
#F_CONSUMER="/etc/pulp/consumer/consumer.conf";

#Prep the confinjectfile (temporary file)
if [ -f $F_INJECTFILE ]; then
        rm -rf $F_INJECTFILE;
fi
cat <<EOF >> $F_INJECTFILE
server_name: $PULPSERVER
default_login: $PULPADMIN
default_password: $PULPADMINPASS
EOF

# Download and install nessasary repos
printf " * Setting up nessasary repositories\t  ";
yum install wget -y &> /dev/null;
#wget https://repos.fedorapeople.org/repos/pulp/pulp/`echo $REPO`-pulp.repo -O /etc/yum.repos.d/`echo $REPO`-pulp.repo &> /dev/null;
if [ -f $F_PULPREPO ]; then
        rm -rf $F_PULPREPO;
fi
cat <<EOF >> $F_PULPREPO
[pulp-repo]
name=Pulp-Crane Repo
baseurl=https://repos.fedorapeople.org/pulp/pulp/stable/2.8/7Server/x86_64/
gpgcheck=0
EOF
wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm &> /dev/null;
yum localinstall epel-release-latest-7.noarch.rpm -y &> /dev/null;
rm -rf epel-release-latest-7.noarch.rpm &> /dev/null;
printf " [$DONE] ";
echo;

# Setting up Backend
printf " * Setting up the backend stuff\t ";
yum install mongodb-server -y &> /dev/null;
systemctl enable mongod  &> /dev/null;
systemctl start mongod  &> /dev/null;
yum install -y qpid-cpp-server qpid-cpp-server-store &> /dev/null;
systemctl enable qpidd &> /dev/null;
systemctl start qpidd &> /dev/null;
printf " [$DONE] ";
echo;

# Setup pulp server
printf " * Setting up the pulp server\t "
yum groupinstall pulp-server-qpid -y &> /dev/null;
# Insert modifications into /etc/pulp/server.conf
sed -i "/\[server\]/r $F_INJECTFILE" $F_PULPSERVER &> /dev/null;
# Insert ssl insecure verify into ssl.conf
echo "SSLInsecureRenegotiation On" > $F_INJECTFILE;
sed -i "/#SSLCryptoDevice ubsec/r $F_INJECTFILE" /etc/httpd/conf.d/ssl.conf &> /dev/null;
cp -rf /artifacts/certs/server.pulpcluster.crt /etc/pki/pulp/ca.crt;
cp -rf /artifacts/certs/ca.key /etc/pki/pulp/ca.key;
sudo -u apache pulp-manage-db &> /dev/null;
printf " [$DONE] ";
echo;

# Start consumer services
printf " * Getting things started\t\t  ";
systemctl enable httpd &> /dev/null;
systemctl start httpd &> /dev/null;
systemctl enable pulp_workers &> /dev/null;
systemctl start pulp_workers &> /dev/null;
systemctl enable pulp_celerybeat &> /dev/null;
systemctl start pulp_celerybeat &> /dev/null;
systemctl enable pulp_resource_manager &> /dev/null;
systemctl start pulp_resource_manager &> /dev/null;
sudo -u apache pulp-manage-db &> /dev/null;
printf " [$DONE] ";
echo;echo;


echo "######################Setup completed#################";echo;
echo "######################TODO#################";echo;
echo;

