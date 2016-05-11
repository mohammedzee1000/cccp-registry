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
PULPADMINPASS="###"; #set the password before before running this script
PULPSERVER="registry.pco.centos.in"
### Keep one active
REPO="rhel";
#REPO="fedora"; 
F_PULPREPO="/etc/yum.repos.d/pulp.repo";

## The untouchables
DONE="\x1b[32mDONE\x1b[0m"
PULPADMIN="admin";
F_INJECTFILE="/tmp/pulp_config_toinject";
F_PULPSERVER="/etc/pulp/server.conf";
F_CRANECONFIG="/etc/crane.conf";
#F_LOG="/var/log/"
#F_PULPADMIN="/etc/pulp/admin/admin.conf"
#F_CONSUMER="/etc/pulp/consumer/consumer.conf";

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
#wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm &> /dev/null;
#yum localinstall epel-release-latest-7.noarch.rpm -y &> /dev/null;
#rm -rf epel-release-latest-7.noarch.rpm &> /dev/null;
yum install epel-release -y;
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
sudo -u apache pulp-manage-db &> /dev/null;
printf " [$DONE] ";
echo;

# Setup crane
printf " * Setting up the crane\t "
yum install python-crane -y &> /dev/null;
cp /usr/share/crane/apache.conf /etc/httpd/conf.d/crane.conf
#Prep the confinjectfile (temporary file) this time to inject crane config
if [ -f $F_CRANECONFIG ]; then
        rm -rf $F_CRANECONFIG;
fi

cat <<EOF >> $F_CRANECONFIG
[general]
debug: true
data_dir: /var/www/pub/docker/
endpoint: `hostname`:5000
EOF

printf " [$DONE] ";
echo;

# Start consumer services
printf " * Getting things started\t\t  ";
firewall-cmd --permanent --add-service http --add-service https >> /dev/null;
firewall-cmd --permanent --add-port 27017/tcp &> /dev/null;
firewall-cmd --permanent --add-port 27017/udp &> /dev/null;
firewall-cmd --reload;
setsebool -P httpd_use_nfs 1 $> /dev/null; 
setsebool -P httpd_can_network_connect 1 $> /dev/null;
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
echo "Edit /etc/httpd/conf.d/crane.conf as needed";
echo "Edit $F_CRANECONFIG as needed";
echo "Enable SSLInsecureRenegotiation on and SSLVerifyClient off"
echo "Make sure you make the hostname of the server known to be put into setup-pulp-client.sh";
echo;

