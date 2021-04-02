import argparse
import datetime
import json
import os.path
import re
import time

import moviepy.audio.fx.all as afx
import moviepy.editor as mpy
import moviepy.video.fx.all as vfx
import pandas as pd
from moviepy.editor import ipython_display

TIME_FORMAT = "%H:%M:%S"


def clipIt(vod, momentTime, sample_window, VOD_ID=None, suspenseSound=None):
    """
    returns vfx clip with fade
    """

    dt_sample_window = datetime.timedelta(0, sample_window)

    startTime = (momentTime - dt_sample_window).strftime(TIME_FORMAT)

    endTime = (momentTime + dt_sample_window).strftime(TIME_FORMAT)
    print(
        f"Found most engaged moment at: {startTime} to {endTime}",
    )

    clip = vod.subclip(startTime, endTime)

    # Add watermark
    if VOD_ID:
        txt_clip = mpy.TextClip(
            f"twitch.tv/videos/{VOD_ID}", fontsize=14, color="white"
        )
        txt_clip = txt_clip.set_pos("bottom").set_duration(sample_window)
        clip = mpy.CompositeVideoClip([clip, txt_clip])

    # Add fade in and fade out
    FADE_DURATION = 3
    clip = vfx.fadeout(clip, FADE_DURATION)
    clip = vfx.fadein(clip, FADE_DURATION)

    if suspenseSound:
        # fade in some audio sound
        audioclip = mpy.AudioFileClip(suspenseSound).set_duration(sample_window)

        audioclip = afx.audio_fadeout(audioclip, FADE_DURATION)
        audioclip = afx.audio_fadein(audioclip, round(FADE_DURATION * 2))

        clipAudio = mpy.CompositeAudioClip([clip.audio, audioclip])
        clip.audio = clipAudio

    return clip


def gatherChat(chat_path, start_time, end_time):
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

            data[cnt] = {"timestamp": timestamp, "user": user, "message": message}

            if cnt % 100000 == 1:
                print(
                    f"Anaysed messages: {cnt}",
                )

    df_chat = pd.DataFrame.from_dict(data, "index")
    # print("Sample messages")
    # print(df_chat.tail())
    # Time format series
    df_chat["timestamp"] = pd.to_datetime(
        df_chat["timestamp"].str.strip(), format=TIME_FORMAT
    )
    df_chat = df_chat[
        df_chat["timestamp"] > pd.to_datetime(start_time, format=TIME_FORMAT)
    ]
    df_chat = df_chat[
        df_chat["timestamp"] < pd.to_datetime(end_time, format=TIME_FORMAT)
    ]
    # print("Sample messages")
    # print(df_chat.head())
    return df_chat


def createIntroClip(title, screensize):

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
    SUSPENSE_FILE = args.suspense
    OUTPUT_PATH = args.output_path
    VOD_PATH = args.input_path

    # Download vod
    print("Formatting chat data")
    chat_path = f"{VOD_PATH}/{str(VOD_ID)}/chat.log"
    df_chat = gatherChat(chat_path, START_TIME_FILTER, END_TIME_FILTER)

    # sample bin window to group by
    df_sample_chat = (
        df_chat.set_index("timestamp")
        .resample(str(SAMPLE_WINDOW) + "s")["message"]
        .agg(["sum", "count"])
    )

    clips = []

    # Get the vod
    vod_file = f"{VOD_PATH}/{str(VOD_ID)}/vod.mkv"
    vod = mpy.VideoFileClip(vod_file)

    introClip = createIntroClip(INTRO_TITLE, vod.size)

    clips.append(introClip)

    EDIT_WINDOW = 10
    # Gather pogs emotes
    emotes_interest = [s.strip() for s in args.emotes.split(",")]

    # time of interest
    for emote in emotes_interest:
        df_sample_chat[emote + "_count"] = (
            df_sample_chat["sum"]
            .astype(str)
            .apply(lambda msg: len(re.findall(emote, msg)))
        )

        print(f"Gathering pog moment: {emote}")
        # Gather clips
        pogMomentTime = (
            df_sample_chat.sort_values([emote + "_count"]).iloc[[-1]].index.tolist()[0]
        )

        clip = clipIt(vod, pogMomentTime, EDIT_WINDOW, VOD_ID, SUSPENSE_FILE)
        # pogClip.write_videofile(f"{OUTPUT_PATH}/{str(VOD_ID)}/{emote}.mp4")
        clips.append(clip)

    # deletin vod to free up mem
    del vod
    # TODO: check if times overlap to much and if so choose the next top

    print("Editing vod clips")
    OUTPUT_PATH_VOD = f"{OUTPUT_PATH}/{str(VOD_ID)}"
    if not os.path.exists(OUTPUT_PATH_VOD):
        os.makedirs(OUTPUT_PATH_VOD)

    concatClip = mpy.concatenate_videoclips(clips)
    EXPORT_FILE_PATH = f"{OUTPUT_PATH_VOD}/previouslyClip.mp4"
    concatClip.write_videofile(EXPORT_FILE_PATH)
    print("Previously on clip saved to: ", EXPORT_FILE_PATH)
    del concatClip

    # exporting each clip
    print("Exporting clips")
    for clip, emote in zip(clips, emotes_interest):
        clip.write_videofile(f"{OUTPUT_PATH_VOD}/{emote}.mp4")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vodID", help="vodID downloaded for both .log and .mkv", type=int
    )
    parser.add_argument(
        "--start",
        default="00:00:00",
        help="start time to clip chat + vod. Time format %H:%M:%S",
        type=str,
    )
    parser.add_argument(
        "--end", help="end time to chat. Time format %H:%M:%S", type=str
    )
    parser.add_argument(
        "--input-path", help="Path to input files", default="./out", type=str
    )
    parser.add_argument(
        "--output-path", help="Path to output files", default="./clips", type=str
    )
    parser.add_argument(
        "--sample_window",
        nargs="?",
        const=1,
        default=15,
        help="Size of sample window to capture per moment. In seconds",
        type=int,
    )
    parser.add_argument(
        "--title",
        nargs="?",
        const=1,
        default="Previously...",
        help="A title to summarize the moments",
        type=str,
    )
    parser.add_argument(
        "--emotes",
        default="PogU,KEKW,WICKED,D:",
        help="Comma sperated top emotes to clip together. The order of the emotes determine the order they will be edited together",
        type=str,
    )
    parser.add_argument(
        "--suspense",
        default=None,
        help="Mix with a sound file with a suspense between clips. Provide a path to soundfile as an arg",
        type=str,
    )
    args = parser.parse_args()

    main(args)
