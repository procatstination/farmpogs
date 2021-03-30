# Farm pogos

This will take a vod and create a 'previously' on type moment.

Right now it chooses a set of 4 emotes and find when this is used the most.

It then edits these clips together to provide a summary of a vod to give a nice fun engagement.

# Example

$ pip install -r requirements.txt
$ bash gathContent.sh 963962409
$ python analysis.py --vodID 963962409 --start "02:30:25" --end "10:55:28"
