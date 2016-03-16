#!/bin/bash

#################################################################################################################
# This script sets enables single command push for pulp based docker repositories, through pulp-admin for the   #
# Centos Container Pipeline. It assumes that the pulp-admin has been properly setup.                            #
#                                                                                                               #
#            AUTHOR : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com                                        #
#################################################################################################################

function err_handle() {
	err=$1;
	err_code=1;

	case $err in
		PLP_LOGIN_FAIL)
			echo;
			echo "Pulp credentials are invalid, exiting.";
			err_code=2;
		;;
		NO_PARAMS)
			echo;
			echo "usage : $0 PULP_LOGIN PULP_PASSWORD LOCAL_DOCKER_PULLED_IMAGE_NAME INTERNAL_REPOID IMAGE_PUBLISHED_ID "
		;;
	esac

	exit $err_code;
}

# Check parameters
if [ "$#" -lt 5 ]; then
	err_handle NO_PARAMS;
fi

# Globals
PULP_UID=$1;
PULP_PASS=$2;
ORIGIMG=$3;   # The image as present in your machine
REPOID_INTERNAL=$4; # Internal repo name
PUBLISHEDID=$5; # The published repo name.

TARBALL="theimage.tar";
REPOEXISTS=0;


# Action Begins


# Attempt to login into pulp-admin
pulp-admin login -u $PULP_UID -p $PULP_PASS;
if [ $? -gt 0 ]; then
	err_handle PLP_LOGIN_FAIL;
fi

# Create the tarball
if [ -f $TARBALL ]; then
	rm -rf $TARBALL;
fi
docker save $ORIGIMG > $TARBALL; 

# Check for existance of the repo
pulp-admin docker repo list | grep $REPOID_INTERNAL &> /dev/null;
REPOEXISTS=$?;

# If it exists, remove it.
if [ $REPOEXISTS -gt 0 ]; then
	pulp-admin docker repo delete --repo-id=$REPOID_INTERNAL;
fi

# Create the fresh repo
pulp-admin docker repo create --repo-id=$REPOID_INTERNAL;

# Upload image layers to created repo
 pulp-admin docker repo uploads upload --repo-id=$REPOID_INTERNAL -f $TARBALL;

# Publish the data for crane to consume
pulp-admin docker repo update --repo-id=$REPOID_INTERNAL --repo-registry-id=$PUBLISHEDID;
pulp-admin docker repo publish run --repo-id=$REPOID_INTERNAL;

echo;
echo "TASK COMPLETED";

