#!/usr/bin/env bash

# This script assumes you already have agent forwarding based ssh configured to access the CentOS Devcloud
# And that you have the jenkins keyfiles generated
# https://developer.github.com/v3/guides/using-ssh-agent-forwarding/ should give you the information you need.

# This script will setup the nodes and provide you with the inventory file. You will need to manually run the
# ansible playbook after that

# Initialize Variables

## SSH_VARS:
DEVCLOUD_USER=${DEVCLOUD_USER:-"mzee1000"};
DEVCLOUD_JUMP_NODE=${DEVCLOUD_JUMP_NODE:-"jump.lon1.centos.org"};
SSH_URL="${DEVCLOUD_USER}@${DEVCLOUD_JUMP_NODE}";
SSH_CMD="ssh -A ${SSH_URL}";

# NODE_NAMES_IPS
JM="";
JS="";
OS="";
SC="";
ND_JM_NAME=${ND_JM_NAME:-"pipeline_jenkins_master"};
ND_JS_NAME=${ND_JS_NAME:-"pipeline_jenkins_slave"};
ND_OS_NAME=${ND_OS_NAME:-"pipeline_openshift"};
ND_SC_NAME=${ND_SC_NAME:-"pipeline_scanner"};

## CMDS
OPENSTACK_CMD="${SSH_CMD} openstack server";
OPENSTACK_CREATE="${OPENSTACK_CMD} create";
OPENSTACK_SHOW="${OPENSTACK_CMD} show";
OPENSTACK_DELETE="${OPENSTACK_CMD} delete";
OPENSTACK_NETWORKS="${OPENSTACK_CMD} network list -f value";

## FUNCTION_DATA_PIPE
DATA_PIPE="";

## NEEDED VARS
INVENTORY_FILE="./hosts.demo";
OPENSTACK_FLAVOUR="medium";

# OPENSTACK FUNCTIONS

openstack_node_exists() {
    NODE_NAME=${1};
    NODE_CMD="${OPENSTACK_SHOW} ${NODE_NAME} &> /dev/null";
    ${NODE_CMD};
    if [ $? -eq 0 ]; then
        DATA_PIPE=1;
    else
        DATA_PIPE=0;
    fi
}

openstack_node_id() {
    NODE_NAME=${1};
    NODE_CMD="${OPENSTACK_SHOW} ${NODE_NAME} | grep id | awk '{print \$4}' | head -1";
    DATA_PIPE="$(${NODE_CMD})"
}

openstack_node_ip() {
    NODE_NAME=${1};
    NODE_CMD="${OPENSTACK_SHOW} ${NODE_NAME} | grep addresses | awk '{print \$4}' | cut -d '=' -f2";
    DATA_PIPE="$(${NODE_CMD})";
}

openstack_node_delete() {
    NODE_NAME=${1};

    openstack_node_exists ${NODE_NAME}
    if [ ${DATA_PIPE} -eq 1 ]; then
        openstack_node_id ${NODE_NAME};
        NODE_CMD="${OPENSTACK_DELETE} ${DATA_PIPE}";
        ${NODE_CMD};
    fi
}

openstack_node_create() {
    NODE_NAME=${1};
    NODE_CMD="${OPENSTACK_CREATE} --image 'centos_7' --flavor medium --key-name ${DEVCLOUD_USER}_key
     --nic net-id=\$(openstack network list -f value |awk '{print \$1}') ${NODE_NAME} &> /dev/null";
    ${NODE_CMD};
}


# Core functions
SETUP_NODES() {
    openstack_node_delete ${ND_JM_NAME};
    openstack_node_delete ${ND_JS_NAME};
    openstack_node_delete ${ND_OS_NAME};
    openstack_node_delete ${ND_SC_NAME};

    openstack_node_create ${ND_JM_NAME};
    openstack_node_create ${ND_JS_NAME};
    openstack_node_create ${ND_OS_NAME};
    openstack_node_create ${ND_SC_NAME};
}

GEN_INVENTORY() {
    openstack_node_ip ${ND_JM_NAME};
    JM=${DATA_PIPE};

    openstack_node_ip ${ND_JS_NAME}
    JS=${DATA_PIPE};

    openstack_node_ip ${ND_OS_NAME}
    OS=${DATA_PIPE};

    openstack_node_ip ${ND_SC_NAME}
    SC=${DATA_PIPE};

    sh ./gen_inventory.sh ${INVENTORY_FILE} ${JM} ${JS} ${OS} ${SC}
}

# Core Choice functions

SETUP() {

    SETUP_NODES;
    GEN_INVENTORY;
    echo "Great, the nodes are ready along with a sample inventory file. The next steps, however,";
    echo "will require manual intervention. Please start an ssh tunnel and then run the playbook" ;
    echo "with provided inventory file";

    echo "1.  sshuttle -v -r ${DEVCLOUD_USER}@${DEVCLOUD_JUMP_NODE} -e 'ssh -A' 172.29.0.0/16";
    echo "2a  Make sure you get you ssh keys accepted into the nodes, rememebr password is centos by default on all nodes";
    echo "2b.  ssh centos@${JM}";
    echo "2c.  ssh centos@${JS}";
    echo "2d.  ssh centos@${OS}";
    echo "2e.  ssh centos@${SC}";
    echo "3a. CD to directory wuth pipeline code";
    echo "3b. ansible-playbook provisions/main.yml -bu centos -i /path/to/generated/inventory"

}

DEL_NODES() {

    openstack_node_delete ${ND_JM_NAME};
    openstack_node_delete ${ND_JS_NAME};
    openstack_node_delete ${ND_OS_NAME};
    openstack_node_delete ${ND_SC_NAME};

}

# MAIN BEGINS

ACT=${1:-"SETUP"};

case ${ACT} in
    setup)
        SETUP;
    ;;
    delete)
        DEL_NODES;
    ;;
    *)
    echo "Invalid choice";
    ;;
esac
