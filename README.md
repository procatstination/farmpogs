# Farm Pogs

This will take a [twitch](https://www.twitch.tv) vod and create a short video 'previously' based on chatters top momemnts according to the [emotes](https://betterttv.com/) chatters send.

Right now it chooses a set of 4 fixed emotes and find when this is used the most then roughly joins those segments.

# Example Usage

First install the pip requirements prefeably in a virualenv

`$ pip install -r requirements.txt`

Next execute the gatherContent.sh script below and pass the VODID of twitch stream found within the url: `https://www.twitch.tv/videos/963962409`

`$ bash gatherContent.sh 963962409 160p 02:30:00 10:55:00`

This is the longest part of the process as its downloading the a quality vod and all the chat logs.

alternatively if avalaible move the vod file into `'./out/963962409/vod.mkv'` and the chat log into `'./out/963962409/chat.log'`.

Finally run the analysis script below to extract all those pog momments!
You must provide the start and end time to cover.

`$ python analysis.py --vodID 963962409 --end "10:50:28"`

The clips will be outputed to a `'./clips'` folder.

The core edit is `'./clips/previouslyClip.mp4'`
