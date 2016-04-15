#!/bin/bash

#################################################################################################
#	Script generates default entries into cccp-index/index.yml for the CentOs-Dockerfiles.	#
#												#
#	Author : Mohammed Zeeshan Ahmed (mohammed.zee1000@gmail.com)				#
#################################################################################################

# Globals : 

centosdfpath=$1;
git_url=$2;
git_branch=$3;
notify_email=$4;

function err(){
	mode=$1;
	exitc=1;
	errmsg="";

	case $mode in
		INDEX_INCORRECT)
			errmsg="The path specified as the index file is not a file or does not exist.";
			exitc=2;
		;;
		INVAL_DFPATH)
			errmsg="The location specified for centos dockerfiles path is invalid.";
			exitc=3;
		;;	
	esac	

	echo -e "ERROR : $errmsg";
	exit $exitc;
}

function indexentry(){
	# Usage: indexentry mode id appid jobid gitpath
	mode=$1;
	theid=$2;
	app_id=$3;
	job_id=$4;
	git_path=$5;
	echo "$git_path"; #TEST

	indexpath="./index.yml"; # The path of the index.yml file. Please set this before running this script.
	tmpfile="/tmp/gentemp";

	case $mode in
		CHK_INDEXPATH)   # Mode checks if indexpath value points to a file.
			if [ -f $indexpath ]; then
				# If index path exists then its fine.
				return;		
							
			fi
			# Ask user to set the value.
			err INDEX_INCORRECT;
		;;
		GEN_ENTRY)
			#entry="- id\t\t: $theid\n";
		
			if [ -f $tmpfile ]; then
				rm -rf $tmpfile
			fi
				
			echo -en "app-id      : $app_id" > $tmpfile;
	
			content=$(cat $tmpfile);
			echo -en "$content\njob-id      : $job_id" > $tmpfile;

			content=$(cat $tmpfile);
			echo -en "$content\ngit-url     : $git_url" > $tmpfile;

			content=$(cat $tmpfile);
			echo -en "$content\ngit-path    : $git_path" > $tmpfile;

			content=$(cat $tmpfile);
			echo -en "$content\ngit-branch  : $git_branch" > $tmpfile;

			content=$(cat $tmpfile);
			echo -en "$content\nnotify-email: $notify_email" > $tmpfile;

			sed -e 's/^/  /' -i $tmpfile;
			content=$(cat $tmpfile);
			echo -en "- id          : $theid\n$content" > $tmpfile;
			sed -e 's/^/  /' -i $tmpfile;
			#cat $tmpfile; #TEST;
			cat $tmpfile >> $indexpath;
			echo >> $indexpath;
			echo >> $indexpath;
		;;
	esac
	
}

function genindexentry(){

        mode=$1;
        project=$2;


        case $mode in
                SUBP)
                        subproject=$3;
			echo "** generating indx entry for $project $subproject...";
                        JOBID="oco-$project-$subproject" # JOBID = FirstChar(osversion)LastChar(osversion)-PROJECTNAME
			git_path="images/$project/$subproject/";
		
                ;;
                DIRECT)
			echo "** generating indx entry for $project ...";
                        JOBID="oco-$project";
			git_path="images/$project/"
                ;;
        esac
	#echo "$git_path"; #TEST
	indexentry GEN_ENTRY "default" "openshiftorigin" $JOBID "$git_path";
}

function usage(){
	echo "USAGE $0 <CENTOSDOCKERFILEPATH> <GITURL> <GITBRANCH> <NOTIFYEMAIL>";
	exit 5000;
}

# MAIN BEGINS


# Check if parameters were passed.
if [ $# -lt 4  ]; then
	usage;
fi

proceed="z";
while true; do
        echo;
        echo "Please ensure that the indexpath value has been set in the script";
        printf "Proceed with generation (y/n) : ";
        read proceed;
        #echo $proceed; #TEST
        echo
        if [ "$proceed" = "y" ]; then
                break;
        elif [ "$proceed" = "n" ]; then
                exit 0;
        fi
done

indexentry CHK_INDEXPATH;

# Check if path is a valid directory
if [ ! -d $centosdfpath ]; then

	err INVAL_DFPATH; # Inform user of invalid path

fi

# Check every project directory in the Centos-Dockerfiles
for project in `ls $centosdfpath/images`; do
         #echo $project; # TEST
        if [ -d "$centosdfpath/images/$project"  ]; then

                echo "Found project : $project, getting in..."
                ls $centosdfpath/images/$project | grep -i Dockerfile &> /dev/null; # Check if Dockerfile is present in the project dir

                # if there is no match process subprojects
                if [ $? -gt 0 ]; then

                        echo "* Project contains subprojects, switching to subpoject mode...";

                        for subproject in `ls $centosdfpath/images/$project`; do

                                genindexentry SUBP $project $subproject;

                        done
                else
                        echo "* Project does not contain subproject directories, switching to direct mode...";
                        genindexentry DIRECT $project;
                fi
        fi
        echo;
done

