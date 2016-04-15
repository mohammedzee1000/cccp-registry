#!/bin/bash

######################################################################################################
#  Checks directory tree for dockerfiles and builds them while logging the success or failure of 
#  builds of the said dockerfiles and reports them through the loggile.
#	Author : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com)
######################################################################################################

# Globals

DIRROOT=$1;
PROJECT=$2;
ORDERFILE=$3;
LOGFILE="$HOME/builddockerfile";

function usage() {
	echo "USAGE : $0 [DIRROOT] [PROJECTNAME] [BASEDIR] [ORDERFILE]";
	echo;
	echo "*   Directory Root - The folder which containes dockerfiles, remember only one Dockerfile per directory/subdirectory.";
	echo "*   PROJECTNAME - Name you wish to assign to the project.";
	echo "    ORDERFILE - Pattern ";
	echo;
}

function err() {
	mode=$1;
	errcode=1;

	case $mode in
		INVAL_USAGE)

			usage;

		;;
	esac

	exit $errcode
}

function build() {
	level=$1;
	local ITEM;
	if [ -f $ORDERFILE]; then

		for ITEM in `cat $ORDERFILE`; do
			if [ -d "$ITEM" -a ! -L "$ITEM" ]; then
				ls ./$ITEM | grep -i Dockerfile &> /dev/null;
				if [ $? -eq 0 ]; then
					echo;echo;
					echo "* Found dockerfile at $PWD/ITEM...";
					buildid_t="$PROJECT/$ITEM";
					buildid=`echo $buildid_t | tr '[:upper:]' '[:lower:]'`;
					printf "** Building as $buildid...\n";
					docker build -t $buildid . >> $LOGFILE 2>&1;
               		                if [ $? -eq 0 ]; then
                	               		 state="success";
                        	                 docker rmi $buildid &> /dev/null;
                        	        else
                                	         state="failure";
                               		fi
					printf "$state\n\n";
					printf "$state\n\n" >> $LOGFILE;

				fi
				echo;echo;

			fi
		done

	else

		for ITEM in `ls`; do
			#echo $ITEM; #test
			if [ -d "./$ITEM" -a ! -L "./$ITEM" ]; then
				#echo "$ITEM is directory" #test
				#ls -l $ITEM; #test
				pushd ./$ITEM &> /dev/null;
				build $level;

				ls | grep -i Dockerfile &> /dev/null;
			
				if [ $? -eq 0 ]; then

					echo;echo;
					echo "* Found Dockerfile at $PWD";
					buildid_t="$PROJECT/$ITEM";
					buildid=`echo $buildid_t | tr '[:upper:]' '[:lower:]'`;
					printf "** Building as $buildid, this could take a while ...";
					printf "\n\n\nBuild $PWD dockerfile\n" >> $LOGFILE; 
					docker build -t $buildid . >> $LOGFILE 2>&1;
					if [ $? -eq 0 ]; then
						state="success";
						docker rmi $buildid &> /dev/null;
					else
						state="failure";
					fi
					echo;echo;
					printf "$state\n\n" >> $LOGFILE;
					printf "$state\n\n";
				fi	
				popd &> /dev/null;
			fi
		done

	fi	
}

if [ $# -lt 2 ]; then
	err INVAL_USAGE;
fi


echo "Log file not provided, defaulting to $LOGFILE";


if [ -f $LOGFILE ]; then
	rm -rf $LOGFILE;
fi

touch $LOGFILE;
pushd $DIRROOT &> /dev/null;
build 1;
popd &> /dev/null;
