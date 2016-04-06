#!/bin/bash

######################################################################################################
#												     #
#    This script is a single command wrapper to sync content from external registry into pulp 	     #
#    registry.											     #
#												     #
#		Author : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com)			     #
#												     #
######################################################################################################

# Usage :
#  CMD PATTERN : cmd pulp_uid pulp_pass  extern_reg_reponame repoid_pulp_internal repoid_pulp_publish

# Imp : make  --verify-feed-ssl false to true in production as pulp server must trust the internal registry.

# Globals : 

## Params
pulp_uid=$1;
pulp_pass=$2;
extern_reg_reponame=$3;
repoid_pulp_internal=$4;
repoid_pulp_publish=$5;

## Base 
extern_reg_url="https://dev-32-56.lon1.centos.org:5000";
CDN_Server="https://dev-32-49.lon1.centos.org";
CDN_Repo_Version="2";
LOG="/var/log/pulp_docker_sync_log";

## Derived
redirecturl="$CDN_Server/v$CDN_Repo_Version/$repoid_pulp_internal";

function usage() {
	echo "USAGE : $0 pulp_uid pulp_pass extern_reg_reponame repoid_pulp_internal repoid_pulp_publish";
}

function err() {
	mode=$1;
	exitc=1;
	msg="";

	case $mode in
		PARAMS_ERROR)
			usage;
		;;
		PULP_LOGIN_FAIL)
			msg="Unable to login to the pulp registry.";
		;;
	esac

	echo -e $msg;
	exit $exitc;
}

# Check if logfile exists, if not create it.
if [ ! -f $LOG ]; then
	touch $LOG;
else
	rm -rf $LOG;
	touch $LOG;
fi

# Check if parameters were passed correctly.
if [ $# -lt 5 ]; then
	err PARAMS_ERROR;
fi

# Attempt to login into pulp.
pulp-admin login -u $pulp_uid -p $pulp_pass >> $LOG;

# Check if login was successfull
if [ $? -gt 0 ]; then
	err PULP_LOGIN_FAIL;
fi

# Check if the repo already exists
pulp-admin docker repo list | grep $repoid_pulp_internal >> $LOG;

# if repo already exists, delete it
if [ $? -eq 0 ]; then
	pulp-admin docker repo delete --repo-id=$repoid_pulp_internal >> $LOG;
fi

# Create the repo
pulp-admin docker repo create --repo-id=$repoid_pulp_internal --repo-registry-id=$repoid_pulp_publish --feed=$extern_reg_url --verify-feed-ssl false --upstream-name=$extern_reg_reponame  --redirect-url=$redirecturl;

# Run the sync on the repository.
pulp-admin docker repo sync run --repo-id=$repoid_pulp_internal;

# Publish the repository.
pulp-admin docker repo publish run --repo-id=$repoid_pulp_internal;

echo;
echo "TASK COMPLETE";
echo;
