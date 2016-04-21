#!/bin/bash

for item in nfsserver pulpserver cdnserver craneserver; do
	actualdir=$(cat itemlist | grep $item);
	pushd ./virtual-machines/$actualdir &> /dev/null;
	vagrant destroy $item;
	popd &> /dev/null;
	rm -rf ./virtual-machines/$actualdir;
done
