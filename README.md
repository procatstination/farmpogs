# Farm pogos

This will take a vod and create a 'previously' on type moment.

Right now it chooses a set of 4 emotes and find when this is used the most.

It then edits these clips together to provide a summary of a vod to give a nice fun overview of best momements.

# Example

First install the pip requirements prefeably in a virualenv

`$ pip install -r requirements.txt`

Next execute the gatherContent.sh script below and pass the VODID of twitch stream found within the url: `https://www.twitch.tv/videos/963962409`

`$ bash gatherContent.sh 963962409`

This is the longest part of the process as its downloading the a quality vod and all the chat logs.

alternatively if avalaible move the vod file into `'./out/963962409/vod.mkv'` and the chat log into `'./out/963962409/vod.log'`.

Finally run the analysis script below to extract all those pog momments!
You must provide the start and end time to cover.

`$ python analysis.py --vodID 963962409 --start "02:30:25" --end "10:55:28"`

The clips will be outputed to a `'./clips'` folder.

The core edit is `'./clips/previosulyClip.mp4'`
