#!/bin/bash

function close_step() {
	echo -e "\n###################################\n"
}

function cont_step() {
	read -n 1 -s -p "Press any key to continue";
	echo;
}

# Pre-steps :
#  Add r.c.o as registry.
#  Install atomic and oc command lines.

set -x;

echo "Atomic Registry DEMO";
cont_step;

echo "Pre-Steps : "
cont_step;
yum -y install docker atomic centos-release-openshift-origin;
yum -y intall oc-clients;
cat /etc/sysconfig/docker | grep "registry.centos.org";
if [ $? -ne 0 ]; then
	echo "ADD_REGISTRY='--add-registry registry.centos.org'" >> /etc/sysconfig/docker
fi
systemctl enable --now docker;
close_step;

echo "1. Installing atomic registry....";
cont_step;
atomic install projectatomic/atomic-registry-install;
docker images;
close_step;

echo "2. Starting atomic registry, please wait for 5 mins....";
cont_step;
systemctl enable --now atomic-registry-master.service;
while :
do
	docker ps;
	read -n1 -r -p "Press c to move forward, any other key to check status..." key
	if [ "${key}" = 'c' ]; then
		break;
	fi
done
close_step;

echo "3. Pulling an image for demo purposes...";
cont_step;
docker pull busybox;
docker images | grep "busybox";
close_step

echo "4. Retagging and pushing....";
cont_step;
docker tag -t busybox localhost:5000/simple/box;
oc login localhost:8443 -u test -p test;
oc new-project simple;
oc policy add-role-to-group registry-viewer system:authenticated system:unauthenticated;
TOKEN="`oc whoami -t`";
docker login -p ${TOKEN} -u unused -e test@test.com localhost:5000;
docker push localhost:5000/simple/box;
close_step;

echo "5. Deleting local copy...";
cont_step;
docker rmi localhost:5000/simple/box;
docker images;
close_step;

echo "6. Ensuring docker is logged out (anonymous pull & no push)...";
cont_step;
docker logout localhost:5000
close_step;

echo "7. Pulling image from atomic registry (anonymous pull)...";
docker pull localhost:5000/simple/box
docker images | grep "simple/box"
cont_step;

echo "8. Atempting anonymous push to atomic registry...";
docker push localhost:5000/simple/box;
cont_step;
