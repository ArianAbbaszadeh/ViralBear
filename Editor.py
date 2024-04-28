import random
import os
import ffmpeg
import json
from moviepy.editor import VideoFileClip, vfx, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.VideoClip import *
from faster_whisper import WhisperModel

def make_video_format1(main_path, bkg_path = "SubwaySurfers001.mp4", bkg_cutoff=0.45, main_ypan = 0.15, output = "ready/testoutput.mp4"):

    # create clips from file paths
    main_clip = VideoFileClip(main_path)
    bkg_clip = VideoFileClip(bkg_path)

    # select a random portion of the background clip equal to the length of the main clip
    start = random.randint(0, int(bkg_clip.duration - 1) - int(main_clip.duration))
    bkg_clip = bkg_clip.subclip(start, start + main_clip.duration)

    # resize the portion of the clip above to match bkg_cutoff
    percent = main_clip.h*bkg_cutoff/bkg_clip.h
    bkg_clip = vfx.resize(bkg_clip, percent)

    #Composite clips together and pan main clip by main_ypan parameter
    final = CompositeVideoClip([main_clip.set_position((0, -main_ypan), relative=True),
                                bkg_clip.set_position("bottom")]).set_audio(main_clip.audio)


    #output file to output parameter destination
    final.write_videofile(output, 
                     codec='libx264', 
                     audio_codec='aac', 
                     temp_audiofile='temp-audio.m4a', 
                     remove_temp=True
                     )

def make_captions(filename):
    audio_filename = filename.replace(".mp4", '.mp3')

    input_stream = ffmpeg.input(filename)
    audio = input_stream.audio
    output = ffmpeg.output(audio, audio_filename)
    output = ffmpeg.overwrite_output(output)
    ffmpeg.run(output)

    model_size = "small"
    model = WhisperModel(model_size)
    segments, info = model.transcribe(audio_filename, word_timestamps = True, language="en")
    word_info = []
    for segment in segments:
        for word in segment.words:
            word_info.append({'word': word.word, 'start': word.start, 'end': word.end})
    print([word['word'] for word in word_info])

    with open(filename.replace(".mp4", ".json"), 'w') as f:
        json.dump(word_info, f)
    return word_info


if __name__ == '__main__':
    make_captions("7258741182447078698.mp4")


