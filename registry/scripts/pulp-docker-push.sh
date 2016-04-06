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
                        echo "usage : $0 REGISTRYVERSION[1|2] PULP_LOGIN PULP_PASSWORD LOCAL_DOCKER_PULLED_IMAGE_NAME INTERNAL_REPOID IMAGE_PUBLISHED_ID "
                ;;
        esac

        exit $err_code;
}

# Check parameters
if [ "$#" -lt 6 ]; then
        err_handle NO_PARAMS;
fi

# Globals
REG_VER=$1;
PULP_UID=$2;
PULP_PASS=$3;
ORIGIMG=$4;   # The image as present in your machine
REPOID_INTERNAL=$5; # Internal repo name
PUBLISHEDID=$6; # The published repo name.
CDNURL="https://dev-32-49.lon1.centos.org/pulp/docker/v$REG_VER/$REPOID_INTERNAL";

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
pulp-admin docker repo create --repo-id=$REPOID_INTERNAL --redirect-url=$CDNURL;

# Upload image layers to created repo
 pulp-admin docker repo uploads upload --repo-id=$REPOID_INTERNAL -f $TARBALL;

# Publish the data for crane to consume
pulp-admin docker repo update --repo-id=$REPOID_INTERNAL --repo-registry-id=$PUBLISHEDID;
pulp-admin docker repo publish run --repo-id=$REPOID_INTERNAL;

echo;
echo "TASK COMPLETED";

