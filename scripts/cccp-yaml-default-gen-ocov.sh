#!/bin/bash

###########################################################################################################
#													  #
#	Script to travese the directories and generate the default cccp.yaml where it is missing	  #
#													  #
#				Author : Mohammed Zeeshan Ahmed	(mohammed.zee1000@gmail.com)		  #
#													  #
###########################################################################################################

function gencccpyaml() {
	
	mode=$1;
	project=$2;

	case $mode in
		SUBP)		
			subproject=$3;
			PTH="./$project/$subproject/cccp.yaml"; # Determine path of the cccp.yaml file
			JOBID="oco-$project-$subproject" 
		;;
		DIRECT)
			PTH="./$project/cccp.yaml";
			JOBID="oco-$project";
		;;
	esac

    #	echo "$PTH $JOBID"; #TEST

	# Check if yaml file already exists, if so skip it

	if [ -f $PTH ]; then
		echo "*** $PTH already exists.....SKIPPED";
		return;
	fi

	# Generate the cccp.yaml file
echo "*** Generating default cccp.yaml";
cat <<EOF >> $PTH
job-id: $JOBID
test-skip: true
EOF


}

echo "Getting started....";echo;

# Check every project directory in the Centos-Dockerfiles
for project in `ls .`; do
	# echo $project; # TEST
	if [ -d $project  ]; then
			
		echo "Found project : $project, getting in..."
		ls ./$project | grep -i Dockerfile &> /dev/null; # Check if Dockerfile ispresent in the project dir

		# if there is no match process subprojects
		if [ $? -gt 0 ]; then

			echo "* Project contains subprojects, switching to subproject mode...";

			for subproject in `ls ./$project`; do

				echo "** Found $subproject in project, getting in...";
				gencccpyaml SUBP $project $subproject;

			done
		else
			echo "* Project does not contain subproject directories instead having Dockerfile, switching to direct mode...";
			gencccpyaml DIRECT $project;
		fi
	fi
	echo;
done
