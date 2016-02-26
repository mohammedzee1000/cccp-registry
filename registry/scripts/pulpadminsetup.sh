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

# GLOBALS

## End user can mod these
PULPSERVER="dev-32-79.lon1.centos.org";
PULP_VERIFYSSL="False";
### Keep one active
REPO="rhel";
#REPO="fedora"; 

## The untouchables
DONE="\x1b[32mDONE\x1b[0m"
PULPADMIN="admin";
PULPADMINPASS="cccp@devcloud";
F_INJECTFILE="/tmp/pulpadmin_config_toinject"; 
F_PULPADMIN="/etc/pulp/admin/admin.conf"
F_CONSUMER="/etc/pulp/consumer/consumer.conf";

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

#Prep the confinjectfile (temporary file)
if [ -f $F_INJECTFILE ]; then
	rm -rf $F_INJECTFILE;
fi
cat <<EOF >> $F_INJECTFILE
host: $PULPSERVER
verify_ssl: $PULP_VERIFYSSL
EOF

# Download and install nessasary repos
printf " * Setting up nessasary repositories\t  ";
yum install wget -y &> /dev/null;
wget https://repos.fedorapeople.org/repos/pulp/pulp/`echo $REPO`-pulp.repo -O /etc/yum.repos.d/`echo $REPO`-pulp.repo &> /dev/null;
wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm &> /dev/null;
yum localinstall epel-release-latest-7.noarch.rpm -y &> /dev/null;
printf " [$DONE] ";
echo;

# Install pulp admin client
printf " * Installing pulp-admin client\t\t  ";
yum groupinstall pulp-admin -y &> /dev/null;
#Inject config changes into /etc/pulp/admin/admin.conf
sed -i "/[server]/r $F_INJECTFILE" $F_PULPADMIN &> /dev/null;
printf " [$DONE] ";
echo;

# Setup consumer and agent
printf " * Installing pulp consumer and agent\t  ";
yum groupinstall pulp-consumer-qpid -y &> /dev/null;
#Inject config changes into /etc/pulp/consumer/consumer.conf
sed -i "/[server]/r $F_INJECTFILE" $F_CONSUMER &> /dev/null;
printf " [$DONE] ";
echo;

# Start consumer services
printf " * Getting things started\t\t  ";
systemctl enable goferd &> /dev/null;
systemctl start goferd &> /dev/null;
systemctl enable docker &> /dev/null;
systemctl start docker &> /dev/null;
printf " [$DONE] ";
echo;

# Setup docker components for pulp-admin
printf " * Installing pulp-admin docker components";
yum install pulp-docker-admin-extensions -y &> /dev/null;
printf " [$DONE] ";
echo;echo;
echo "######################Setup completed#################";echo;

# Get the user started
echo "######################Get started#####################";echo;
echo "Login : pulp-admin login -u $PULPADMIN -p $PULPADMINPASS";
echo "List available repos : pulp-admin repo list";
echo "Create a new repo : pulp-admin docker repo create --repo-id=theid"
echo "Upload docker image to repo : pulp-admin docker repo uploads upload --repo-id=existingrepo theimage.tar";
echo "More info available at https://pulp-docker.readthedocs.org/en/latest/user-guide/recipes.html"
echo;echo;

 
