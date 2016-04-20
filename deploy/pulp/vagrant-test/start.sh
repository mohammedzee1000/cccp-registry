#!/bin/bash

for item in nfsserver pulpserver cdnserver craneserver; do
	pushd ./$item &> /dev/null;
	vagrant up $item;
	popd &> /dev/null;
done
