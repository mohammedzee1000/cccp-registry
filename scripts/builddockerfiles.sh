#!/bin/bash

######################################################################################################
#  Checks directory tree for dockerfiles and builds them while logging the success or failure of 
#  builds of the said dockerfiles and reports them through the loggile.
#	Author : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com)
######################################################################################################


# Globals

DIRROOT=$1;
PROJECT=$2;
ORDERFILE=$4;
CLEANUPAFTER=$3;
LOGFILE="$HOME/dockerfilebuildtest.log";
CLEANUPFILE="$HOME/builtimagelist";
INSPECTDIR="$HOME/dockerfilebuildinspects";

# Displays usage information for the command.
function usage() {
	echo "USAGE : $0 [DIRROOT] [PROJECTNAME] [CLEANUPAFTER] [ORDERFILE]";
	echo;
	echo "*   DIRROOT - The folder which containes dockerfiles, remember only one Dockerfile per directory/subdirectory.";
	echo "*   PROJECTNAME - Name you wish to assign to the project.";
	echo "*   CLEANUPAFTER - If true, then cleanup of built images will happen after everything is built";
	echo "*   ORDERFILE - List of relative paths(relative to DIRROOT of dockerfiles to be built in order ";
	echo "**  Orderfile contains list of directories (path relative to DIRROOT) containing dockerfiles to be built in a specified order.";
	echo "**  Orderfile Each entry can also optionally have image name specified. format PATH[:IMAGENAME]";
	echo;
}

# Handles certain error conditions
function err() {
	# mode - The type of the error.
	mode=$1;
	errcode=1;

	case $mode in
		INVAL_USAGE)

			usage;

		;;
	esac

	exit $errcode
}

# Called only when user wants cleanup to happen, after the entire build process.
function cleanupafter() {

	echo "Cleaning up built images...";

	local ITEM;

	for ITEM in `cat $CLEANUPFILE`; do

		docker rmi $ITEM &> /dev/null;

	done

}

# Function actually builds the image, while logging the build.
function build_image() {
	# buildid - The ID of the image to build
	buildid=$1;

	# Setup the inspectdir
	INSPECTDIR_B="$INSPECTDIR/$buildid";
	mkdir -p "$INSPECTDIR_B";

	docker build -t $buildid . >> $LOGFILE 2>&1;

	# If build failed, then state is failed.
        if [ $? -gt 0 ]; then

       		state="failure";
		
	# Else it is success.
        else

        	state="success";

		# If success and cleanupafter is set, skip cleaning up the image
		if [ $CLEANUPAFTER == "true" ]; then

			echo "Skipping cleanup for now..";
			echo $buildid >> $CLEANUPFILE;

		# Else clean up image immediately.
		else
							
			echo "Cleaning up $buildid";
                        docker rmi $buildid &> /dev/null;
			
		fi
						
	fi

	docker inspect $buildid > "$INSPECTDIR_B/$buildid.inspect" 2>&1;
	echo "Inspect available in $INSPECTDIR_B";
	printf "\nInspect available at $INSPECTDIR_B\n" >> $LOGFILE;
}

# Partially recursive function that does the actual building of images.
function build() {
        # level - Depth of tree as there is a DFT (Depth First Traversal) here.
	level=$1;
	local ITEM;
	local state;
	local INSPECTDIR_B;

	# Check if Orderfile has been specified.
	if [ -f $ORDERFILE ]; then

		# If so, time to start building dockerfiles in specified order.
		printf "\nFound $ORDERFILE, reading...\n\n";

		# Read through entry in orderfile, one line at a time.
		for ITEM in `cat $ORDERFILE`; do

			# Check if entry has a : indicating that an image name has been specified as well.
			echo $ITEM | grep ":" &> /dev/null;

			# If it exists, then split entry on :, first part is folder containing dockerfile and 
			# second part is the image id.
			if [ $? -eq 0 ]; then

				#echo "Contains splitter" #TEST
				FLDR=`echo $ITEM | cut -d ':' -f1`;
				PRJID=`echo $ITEM | cut -d ':' -f2`;
				#echo "$FLDR  ----  $PRJID"; #TEST

			# Else, entire entry is path of the folder containing dockerfile.
			else

				FLDR=$ITEM;
				PRJID="";

			fi

			# If the path specified is a directory and not a soft link.
			if [ -d "$FLDR" -a ! -L "$FLDR" ]; then

				# Check if directory contains Dockerfile.
				ls ./$FLDR | grep -i Dockerfile &> /dev/null;

				# If so, start building it.
				if [ $? -eq 0 ]; then

					echo;echo;
					echo "* Found dockerfile at orderfile location $PWD/$FLDR...";
				
					# If an image id has been specifed, use it as the image buildid.
					if [ ! -z $PRJID ]; then
		
						buildid_t="$PRJID";

					# Else construct one using project name/foldername.
					else

						buildid_t="$PROJECT/$FLDR";

					fi					

					# The image id must be all small characters.
					buildid=`echo $buildid_t | tr '[:upper:]' '[:lower:]'`;

					printf "** Building as $buildid...\n";
					printf "\n\nBuilding $PWD/$ITEM as $buildid\n\n" >> $LOGFILE;
		
					# Get into the directory and build the image
					pushd $PWD/$FLDR &> /dev/null;

					build_image $buildid;

					popd &> /dev/null;
					printf "Build was $state\n\n";
					printf "Build was $state\n\n" >> $LOGFILE;

				fi
				echo;echo;

			fi

		done
	
	# If no orderfile is specified do a DFT of the entire directory tree, starting with DIRROOT as root.
	else
		# Traverse through all child files in current parent.
		for ITEM in `ls`; do
			#echo $ITEM; #test
			#If child file is directory and not a soft link, get into it.
			if [ -d "./$ITEM" -a ! -L "./$ITEM" ]; then

				#echo "$ITEM is directory" #test
				#ls -l $ITEM; #test
				pushd ./$ITEM &> /dev/null;
				
				# DFT here.
				build $level;

				# Check if dockerfile exist in this directory.
				ls | grep -i Dockerfile &> /dev/null;
			
				# If it exists, build it.
				if [ $? -eq 0 ]; then

					echo;echo;
					echo "* Found Dockerfile at $PWD";
					# Build ID is combo of project/foldername.
					buildid_t="$PROJECT/$ITEM";
					# Buidid is all small always.
					buildid=`echo $buildid_t | tr '[:upper:]' '[:lower:]'`;
					printf "** Building as $buildid, this could take a while ...";
					printf "\n\n\nBuild $PWD dockerfile\n" >> $LOGFILE; 

					build_image $buildid;

					echo;echo;
					printf "$state\n\n" >> $LOGFILE;
					printf "$state\n\n";
				fi	
				popd &> /dev/null;
			fi
		done

	fi	
}

# Main Section begins

# Check minimum number of parameters are passed.
if [ $# -lt 2 ]; then

	err INVAL_USAGE;

fi

# Tell user where his logile is located.
echo "Log file at $LOGFILE";

# If log file does not exist, create it.
if [ ! -f $LOGFILE ]; then
	#rm -rf $LOGFILE;
	touch $LOGFILE;
fi

# If cleanupfile does not exist, create it.
if [ ! -f $CLEANUPFILE ]; then

	touch $CLEANUPFILE;

fi

# Check and create inspectdir which will contain the inspect logs.
if [ -d $INSPECTDIR ]; then

	rm -rf $INSPECTDIR;

fi

mkdir -p $INSPECTDIR &> /dev/null;

# Record the docker version used to do the build.
printf "Docker Builder version : `docker version`\n\n######################################## BEGIN #############################" > $LOGFILE;

echo "clafter=$CLEANUPAFTER"

# Depending if cleanupafter is set or not 
if [ $CLEANUPAFTER == "true" ]; then

	printf "\n\n Images will be cleaned up after the build process.\n\n" >> $LOGFILE;

else

	printf "\n\n Images will be cleaned up immediately when build succeeds.\n\n" >> $LOGFILE;

fi

# Initalise the nessasary files and start build.
printf "" > $CLEANUPFILE;
pushd $DIRROOT &> /dev/null;
build 1;
popd &> /dev/null;
printf "\n########################### END ######################\n\n" >> $LOGFILE;


