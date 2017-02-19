from __future__ import unicode_literals
import youtube_dl
import requests
import os
from pyvtt import WebVTTFile

def findMatches(captions):
    index = client.init_index("captions")
    arr = []
    for caption in captions:
        arr.append({'start':caption.start.ordinal, 'end': caption.end.ordinal, 'text': caption.text, 'video': url})
    index.add_objects(arr)

def merge(captions, timestamps):
    out = {}
    diff = (timestamps[1] - timestamps[0])
    
    for caption in captions:
        caption_timestamp = caption.start.ordinal / 1000
        if diff * int(caption_timestamp / diff) not in out:
            out[diff * int(caption_timestamp / diff)] = caption.text
        else: 
            out[diff * int(caption_timestamp / diff)] += ' ' + caption.text
    return out

def getCaptions(url):
    ydl = youtube_dl.YoutubeDL({'writesubtitles': True})
    with ydl:
        res = ydl.extract_info(url, download=False)
        if res['requested_subtitles']['en']:
            print ('Grabbing vtt file from ' + res['requested_subtitles']['en']['url'])
            response = requests.get(res['requested_subtitles']['en']['url'], stream=True)
            with open('temp.vtt', 'wb') as handle:
                for block in response.iter_content(1024):
                    handle.write(block)
            arr = WebVTTFile.open('temp.vtt')
            os.remove('temp.vtt')
            return arr
        else:
            print ('Youtube Video does not have any english captions')

def get_timestamped_captions(url, timestamps):
    captions = getCaptions(url)
    return merge(captions, timestamps)