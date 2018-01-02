#!/bin/bash

INVENTORY=$1;
JENKINS_MASTER=$2;
JENKINS_SLAVE=$3;
OPENSHIFT=$4;
SCANNER=$5;

cat >${INVENTORY} <<EOF
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

[sentry]
${JENKINS_MASTER}

[all:vars]
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
allowed_hosts = "['127.0.0.1', '${JENKINS_SLAVE}']"
db_host=${JENKINS_MASTER}
db_backup_nfs_path=/srv/db/cccp
db_local_volume=/srv/local-db-volume/cccp/
cccp_index_repo_branch=master

[jenkins_master:vars]
logrotate_maxsize=100M
logrotate_rotate=5
EOF

