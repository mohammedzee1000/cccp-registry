#!/bin/bash

# Script traces orphaned layers and reports their space usage, listing them into a temp dir for deletion

set -eu
shopt -s nullglob

readonly base_dir=/mnt/dockerstore
readonly output_dir=$(mktemp -d -t trace-images-XXXX)
readonly jq=/tmp/jq

readonly repository_dir=$base_dir/repositories
readonly image_dir=$base_dir/images

readonly all_images=$output_dir/all
readonly used_images=$output_dir/used
readonly unused_images=$output_dir/unused

function cleanup() {
    echo rm -r $output_dir
}
trap cleanup EXIT ERR INT

function image_history() {
    local readonly image_hash=$1
    $jq '.[]' $image_dir/$image_hash/ancestry | tr -d  '"'
}

for library in $repository_dir/*; do
    echo "Library $(basename $library)" >&2

    for repo in $library/*; do
        echo " Repo $(basename $repo)" >&2

        for tag in $repo/tag_*; do
            echo "  Tag $(basename $tag)" >&2

            tagged_image=$(cat $tag)
            image_history $tagged_image
        done
    done
done | sort | uniq > $used_images

ls $image_dir > $all_images

grep -v -F -f $used_images $all_images > $unused_images

readonly all_image_count=$(wc -l $all_images | awk '{print $1}')
readonly used_image_count=$(wc -l $used_images | awk '{print $1}')
readonly unused_image_count=$(wc -l $unused_images | awk '{print $1}')
readonly unused_image_size=$(cd $image_dir; du -hc $(cat $unused_images) | tail -n1 | cut -f1)

echo "${all_image_count} images, ${used_image_count} used, ${unused_image_count} unused"
echo "Unused images consume ${unused_image_size}"
