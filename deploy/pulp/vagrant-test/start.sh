#!/bin/bash

if [ -f itemlist ]; then
	rm -rf itemlist;
fi

touch itemlist;

for item in nfsserver pulpserver cdnserver craneserver; do
	actualname="$item$RANDOM";
	echo $actualname >> itemlist;
	mkdir virtual-machines/$actualname;
	cp vagrantfiles/Vagrantfile.$item ./virtual-machines/$actualname/Vagrantfile;
	pushd ./virtual-machines/$actualname &> /dev/null;
	vagrant up $item;
	popd &> /dev/null;
done
