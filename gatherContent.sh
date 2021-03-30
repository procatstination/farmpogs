#!/bin/sh

# first arg vod id

while getopts v:q flag
do
    case "${flag}" in
        v) vodID=${OPTARG};
    esac
done
echo "vodID: $vodID";

mkdir ./out/$vodID
mkdir ./clips/$vodID

cd ./out/$vodID
echo 'Downloading chat log'
tcd --channel hasanabi --video $vodID --format irc --output ./ --first=1 

#Rename chat file
mv *.log $vodID.log


echo 'Downloading vod'
twitch-dl download $vodID --overwrite -q 720p60 #not using source to speed up download
# get title and rename

#Rename vod file
mv *.mkv $vodID.mkv
