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
DONE="\x1b[32mDONE\x1b[0m"
PULPADMIN="admin";
F_INJECTFILE="/tmp/pulp_config_toinject";
F_CRANECONFIG="/etc/crane.conf";
F_HTTP_CRANECONFIG="/etc/httpd/conf.d/crane.conf";

#Prep the confinjectfile (temporary file)
if [ -f $F_INJECTFILE ]; then
        rm -rf $F_INJECTFILE;
fi

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

# Crane Pre-steps

# Setup crane
printf " * Setting up the crane\t "
yum install python-crane -y &> /dev/null;
cp /usr/share/crane/apache.conf /etc/httpd/conf.d/crane.conf
#Prep the confinjectfile (temporary file) this time to inject crane config
if [ -f $F_CRANECONFIG ]; then
        rm -rf $F_CRANECONFIG;
fi

echo "SSLInsecureRenegotiation On" > $F_INJECTFILE;
sed -i "/#SSLCryptoDevice ubsec/r $F_INJECTFILE" /etc/httpd/conf.d/ssl.conf &> /dev/null;
cp -rf /home/vagrant/sync/data/certs/crane.pulpcluster.crt /etc/pki/crane/ca.crt;
cp -rf /home/vagrant/sync/data/certs/ca.key /etc/pki/crane/ca.key;

cat <<EOF >> $F_HTTP_CRANECONFIG
Listen 5000 https

 <VirtualHost *:5000>
     SSLEngine on
     SSLCertificateFile /etc/pki/crane/ca.crt
     SSLCertificateKeyFile /etc/pki/crane/ca.key
     WSGIScriptAlias / /usr/share/crane/crane.wsgi
     <Location /crane>
         Require all granted
     </Location>
     <Directory /usr/share/crane/>
         SSLVerifyClient off
         SSLVerifyDepth 2
         SSLOptions +StdEnvVars +ExportCertData +FakeBasicAuth
         Require all granted
     </Directory>
 </VirtualHost>
EOF

cat <<EOF >> $F_CRANECONFIG
[general]
debug: true
data_dir: /var/www/crane/docker
endpoint: `hostname`:5000
EOF

ln -s /var/www/crane /var/lib/pulp;

printf " [$DONE] ";
echo;

systemctl enable httpd;
systemctl start httpd;

echo "######################Setup completed#################";echo;
echo;

