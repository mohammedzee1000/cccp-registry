#!/bin/bash

function cont() {
	echo -e "\n###################################\n"
	read -n 1 -s -p "Press any key to continue";
	echo;
}

# Pre-steps :
#  Add r.c.o as registry.
#  Install atomic and oc command lines.

set -ex;

echo "Atomic Registry DEMO";
cont;

echo "Pre-Steps : "
yum -y install docker atomic;
cat /etc/sysconfig/docker | grep registry.centos.org
if [ $? -ne 0 ]; then
	echo "ADD_REGISTRY='--add-registry registry.centos.org'" >> /etc/sysconfig/docker
fi
systemctl enable --now docker;

cont;
echo "1. Installing atomic registry....";
atomic install projectatomic/atomic-registry-install;

cont;
echo "2. Starting atomic registry, please wait for 5 mins....";
systemctl enable --now atomic-registry-master.service;
while :
do
	docker ps;
	read -n1 -r -p "Press space to move forward, any other key to check status..." key
	if [ "${key}" = '' ]; then
		break;
	fi
done

cont;
echo "3. Pulling an image for demo purposes...";
docker pull busybox;

cont;
echo "4. Retagging and pushing....";
docker tag -t busybox localhost:5000/simple/box;
oc login localhost:8443 -u test -p test;
oc new-project simple;
oc policy add-role-to-group registry-viewer system:authenticated system:unauthenticated;
TOKEN=`oc whoami -t`;
docker login -p ${TOKEN} -u unused -e test@test.com localhost:5000;
docker push localhost:5000/simple/box;

cont;
echo "5. Deleting local copy...";
docker rmi localhost:5000/simple/box

cont;
echo "6. Ensuring docker is logged out (anonymous pull & no push)...";
docker logout localhost:5000

cont;
echo "7. Pulling image from atomic registry (anonymous pull)...";

cont;
echo "8. Atempting anonymous push to atomic registry...";

cont;
