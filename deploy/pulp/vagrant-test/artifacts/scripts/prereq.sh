#!/bin/bash
# Presteps : 

printf " * Setting up prerequisites\t  ";
yum install nfs-utils -y;
cp -av /home/vagrant/sync/data/certs/*.crt "/etc/pki/ca-trust/source/anchors/" &> /dev/null;
update-ca-trust &> /dev/null;
yum install nfs-utils -y &> /dev/null;
systemctl enable rpcbind &> /dev/null;
systemctl enable nfs-server &> /dev/null;
systemctl enable nfs-lock &> /dev/null
systemctl enable nfs-idmap &> /dev/null;
systemctl start rpcbind &> /dev/null;
systemctl start nfs-server &> /dev/null;
systemctl start nfs-lock &> /dev/null;
systemctl start nfs-idmap &> /dev/null;
mkdir -p /var/lib/pulp;
echo "192.168.33.50:/var/nfsshares/var-lib-pulp    /var/lib/pulp       nfs    _netdev,defaults 0 0" >> /etc/fstab;
mount -a;
printf " [$DONE] ";
echo;

