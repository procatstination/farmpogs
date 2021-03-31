# Farm Pogs

This will take a [twitch](https://www.twitch.tv) vod and create a short video 'previously' based on chatters top moments according to the [emotes](https://betterttv.com/) chatters send.

You can pass a series of emotes to search the vod and they will clip these together.

# Example Usage

First install the pip requirements prefeably in a virualenv

`$ pip install -r requirements.txt`

Next execute the gatherContent.sh script below and pass the VODID of twitch stream found within the url: `https://www.twitch.tv/videos/963962409`

`$ bash gatherContent.sh -v 963962409 -q source`

This is the longest part of the process as its downloading the a quality vod and all the chat logs.

alternatively if avalaible move the vod file into `'./out/963962409/vod.mkv'` and the chat log into `'./out/963962409/chat.log'`.

Finally run the analysis script below to extract all those pog momments!
You must provide the start and end time to cover.

`$ python analysis.py --vodID 963962409 --start "02:30:00" --end "10:50:28" --emotes PogU,KEKW,WICKED,D:`

The clips will be outputed to a `'./clips'` folder for other editing needs.

The core edit is `'./clips/963962409/previouslyClip.mp4'`
