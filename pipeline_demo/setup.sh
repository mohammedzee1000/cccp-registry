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
cat >${hosts_file} <<EOF
[all:children]
jenkins_master
jenkins_slaves
openshift
scanner_worker

[jenkins_master]
${JENKINS_MASTER}

[jenkins_slaves]
${JENKINS_SLAVE}

[openshift]
${OPENSHIFT}

[scanner_worker]
${SCANNER}

[all:vars]
db_host=${JENKINS_MASTER}
cccp_index_repo=https://github.com/mohammedzee1000/test_index.git
beanstalk_server=${OPENSHIFT}
copy_ssl_certs=True
oc_slave=${JENKINS_SLAVE}
jenkins_public_key_file=/home/moahmed/cccp-jenkins1.pub
jenkins_private_key_file=/home/moahmed/cccp-jenkins1
public_registry=${JENKINS_SLAVE}
test=True
intranet_registry=${JENKINS_SLAVE}:5000
setup_nfs=True
test_nfs_share=${SCANNER}:/nfsshare
deployment=test
EOF
