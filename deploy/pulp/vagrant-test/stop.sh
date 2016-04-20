#!/bin/bash

for item in nfsserver pulpserver cdnserver craneserver; do
	pushd ./$item &> /dev/null;
	vagrant destroy $item;
	rm -rf .vagrant;
	popd &> /dev/null;
done
