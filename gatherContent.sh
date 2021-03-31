#!/bin/

OPTIND=1     
while getopts "v:q:s:e:" flag
do
    case "${flag}" in
        v) vodID=${OPTARG} ;;
        q) quality=${OPTARG} ;;
    esac
done

mkdir ./out/$vodID
mkdir ./clips/$vodID

cd ./out/$vodID
echo 'Downloading chat log'
tcd --video $vodID --format irc --output ./ --first=1 

#Rename chat file
#mv *.log chat.log

echo 'Downloading vod'
twitch-dl download $vodID --quality $quality
# get title and rename

#Rename vod file
mv *.mkv vod.mkv
