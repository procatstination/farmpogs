import json
import pandas as pd
import re
import time
import moviepy.editor as mpy
from moviepy.editor import ipython_display
import moviepy.video.fx.all as vfx
import datetime
import argparse
import os.path


VOD_ID = 963962409
VOD_PATH = "./out/"
START_TIME_FILTER = "00:00:00"
END_TIME_FILTER = "00:30:00"
TIME_FORMAT = "%H:%M:%S"
SAMPLE_WINDOW = 15  # in seconds
INTRO_TITLE = "Previously..."


def clipIt(vod, momentTime, sample_window):
    """
    returns vfx clip with fade
    """

    dt_sample_window = datetime.timedelta(0, sample_window)

    startTime = (momentTime - dt_sample_window).strftime(TIME_FORMAT)

    endTime = (momentTime + dt_sample_window).strftime(TIME_FORMAT)
    print(
        f"Found most engaged moment at: {startTime} to {endTime}",
    )

    # Clip it
    clip = vod.subclip(startTime, endTime)

    #%%
    # Add fade in and fade out
    FADE_DURATION = 3
    clip = vfx.fadeout(clip, FADE_DURATION)
    clip = vfx.fadein(clip, FADE_DURATION)
    return clip


def gatherChat(chat_path):
    df_chat = pd.DataFrame(columns=["timestamp", "user", "message"])
    # Overall meta message data
    total_msgs = sum(1 for line in open(chat_path))

    print(f"Total messages reviewing: {total_msgs}")

    data = {}
    with open(chat_path) as fp:
        for cnt, line in enumerate(fp):
            timestamp = re.search(r"\[(.*?)\]", line).group(1)
            user = re.search(r"\<(.*?)\>", line).group(1)
            message = re.search(r"\>(.*)", line).group(1)

            # df_chat = df_chat.append(
            #     {"timestamp": timestamp, "user": user, "message": message},
            #     ignore_index=True,
            # )
            data[cnt] = {"timestamp": timestamp, "user": user, "message": message}

            if cnt % 10000 == 1:
                print(
                    f"Anaysed messages: {cnt}",
                )

    df_chat = pd.DataFrame.from_dict(data, "index")

    # Time format series
    df_chat["timestamp"] = pd.to_datetime(
        df_chat["timestamp"].str.strip(), format=TIME_FORMAT
    )

    df_chat = df_chat[
        df_chat["timestamp"] > pd.to_datetime(START_TIME_FILTER, format=TIME_FORMAT)
    ]
    df_chat = df_chat[
        df_chat["timestamp"] < pd.to_datetime(END_TIME_FILTER, format=TIME_FORMAT)
    ]

    return df_chat


def createIntroClip(title):
    screensize = (720, 460)

    introClip = mpy.TextClip(
        title,
        color="white",
        font="Amiri-Bold",
        kerning=5,
        fontsize=20,
    )

    introClip = mpy.CompositeVideoClip(
        [introClip.set_duration(5).set_pos("center").set_fps(30)], size=screensize
    )
    return introClip


def main(args):
    VOD_ID = args.vodID
    START_TIME_FILTER = args.start
    END_TIME_FILTER = args.end
    SAMPLE_WINDOW = args.sample_window
    INTRO_TITLE = args.title

    # Download vod
    print("Formatting chat data")
    chat_path = VOD_PATH + str(VOD_ID) + ".log"
    df_chat = gatherChat(chat_path)
    # chat_path = VOD_PATH + str(VOD_ID) + "_chat.csv"
    # df_chat.to_csv(chat_path)

    # sample bins
    df_sample_chat = (
        df_chat.set_index("timestamp")
        .resample(str(SAMPLE_WINDOW) + "s")["message"]
        .agg(["sum", "count"])
    )

    # Farm PogO's
    emotes_interest = ["PogO", "KEKW", "WICKED", "D:"]

    # time of interest
    for emote in emotes_interest:
        df_sample_chat[emote + "_count"] = df_sample_chat["sum"].apply(
            lambda msg: len(re.findall(emote, msg))
        )

    print("Gathering pog moments")
    # Gather clips
    # Pog moment
    pogMomentTime = (
        df_sample_chat.sort_values(["PogO" + "_count"]).iloc[[-1]].index.tolist()[0]
    )

    # Funnist clip
    funnyMomentTime = (
        df_sample_chat.sort_values(["KEKW" + "_count"]).iloc[[-1]].index.tolist()[0]
    )

    # WICKED momemnt
    wickedMomentTime = (
        df_sample_chat.sort_values(["WICKED" + "_count"]).iloc[[-1]].index.tolist()[0]
    )

    # End with a shocker as hopefully this is a clifhanger
    # or a top 1 anime betrayals...
    shockMomentTime = (
        df_sample_chat.sort_values(["D:" + "_count"]).iloc[[-1]].index.tolist()[0]
    )

    # TODO: check if times overlap to much and if so choose the next top

    print("Editing vod clips")
    # Get the vod
    vod_file = "./out/" + str(VOD_ID) + ".mkv"
    vod = mpy.VideoFileClip(vod_file)

    # Generate a intro clip
    introClip = createIntroClip(INTRO_TITLE)

    EDIT_WINDOW = 10

    pogClip = clipIt(vod, pogMomentTime, EDIT_WINDOW)

    funnyClip = clipIt(vod, funnyMomentTime, EDIT_WINDOW)

    wickedClip = clipIt(vod, wickedMomentTime, EDIT_WINDOW)

    shockClip = clipIt(vod, shockMomentTime, EDIT_WINDOW)

    concatClip = mpy.concatenate_videoclips(
        [introClip, pogClip, funnyClip, wickedClip, shockClip]
    )
    EXPORT_FILE_PATH = "./previouslyClip.mp4"
    concatClip.write_videofile(EXPORT_FILE_PATH)
    print("Previously on clip saved to: ", EXPORT_FILE_PATH)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vodID", help="vodID downloaded for both .log and .mkv", type=int
    )
    parser.add_argument(
        "--start", help="start time to clip chat + vod. Time format %H:%M:%S", type=str
    )
    parser.add_argument(
        "--end", help="end time to chat. Time format %H:%M:%S", type=str
    )
    parser.add_argument(
        "--sample_window",
        nargs="?",
        const=1,
        default=15,
        help="Size of sample window per moment. In seconds",
        type=int,
    )
    parser.add_argument(
        "--title",
        nargs="?",
        const=1,
        default="Previously...",
        help="A title to summarize the momemnts",
        type=str,
    )

    args = parser.parse_args()

    main(args)