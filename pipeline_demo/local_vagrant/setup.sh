#!/bin/bash

set -eux;

hosts_file="./hosts.demo"

VAGRANT_USER="root";
VAGRANT_IP="";

setup_node(){
	ACTION=${1};
	NODE=${2};
	pushd ${NODE};
	vagrant destroy;
	if [ $ACTION == "create" ]; then
		vagrant up;
		VAGRANT_IP="`vagrant ssh-config | grep HostName | cut -d ' ' -f4`";
		sshpass -proot ssh-copy-id -o StrictHostKeyChecking=no ${VAGRANT_USER}@${VAGRANT_IP};
	fi
	popd;
}

ACTION=${1:-"create"}

# Setup the nodes and gather their ips
CURRENT_NODE="jenkins_master";
setup_node ${ACTION} ${CURRENT_NODE};
JENKINS_MASTER=${VAGRANT_IP};

CURRENT_NODE="jenkins_slave";
setup_node ${ACTION} ${CURRENT_NODE};
JENKINS_SLAVE=${VAGRANT_IP};

CURRENT_NODE="openshift";
setup_node ${ACTION} ${CURRENT_NODE};
OPENSHIFT=${VAGRANT_IP};

CURRENT_NODE="scanner";
setup_node ${ACTION} ${CURRENT_NODE};
SCANNER=${VAGRANT_IP};
# Generate pipeline inventory file
sh ./gen_inventory.sh ${hosts_file} ${JENKINS_MASTER} ${JENKINS_SLAVE} ${OPENSHIFT} ${SCANNER}
