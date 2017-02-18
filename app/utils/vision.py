import re
import requests
import time

from PIL import Image
from google.cloud import vision
from io import BytesIO


def get_page_source(url):
    r = requests.get(url)
    return str(r.content)

def get_mosaics(page_content):
    match = (re.search('\"storyboard_spec\":\"([^\"]*)\"', page_content)
            .group(1).replace('\\\\', ''))
    sighs = re.findall('\$M#([^\|$]+)(?:\||$)', match)
    base_url = match[:match.find('|')] + '?sigh=$S'

    l_value = len(sighs)
    sigh = sighs[-1]
    m_value = 0

    base_url = base_url.replace('$L', str(l_value)).replace('$S', sigh)

    # get all mosaics
    imgs = {}
    img_keys = []
    while True:
        mosaic_url = base_url.replace('$N', 'M{}'.format(m_value))
        img_keys.append('L{}_M{}_{}'.format(l_value, m_value, sigh))

        r = requests.get(mosaic_url, stream=True)
        if r.status_code != 200:
            print('failed on img_key={}, so we\'re done'.format(img_keys[-1]))
            img_keys.pop()
            break

        r.raw.decode_content = True
        imgs[img_keys[-1]] = Image.open(r.raw)

        time.sleep(0.5) # do not set off youtube's firewall
        m_value += 1
    
    return img_keys, imgs, l_value

def get_vid_length(page_content):
    return int(re.search(
        '\"length\_seconds\":\"([0-9]*)\"',
        page_content).group(1))

def get_frame_interval(vid_length):
    if 15 <= vid_length < 120: return 1
    elif 120 <= vid_length < 300: return 2
    elif 300 <= vid_length < 900: return 5
    else: return 10

def get_frame_dims(mosaic_w, mosaic_h, num_full_rows, num_last_row, shape):
    if num_full_rows == 0:
        frame_width = mosaic_w // num_last_row
    else:
        frame_width = mosaic_w // shape

    if num_full_rows >= shape:
        frame_height = mosaic_h // shape
    else:
        frame_height = mosaic_h // num_full_rows

    return frame_width, frame_height

def get_timestamped_frames(img_keys, imgs, level, vid_length):
    level_to_mosaic_shape = {1: 10, 2: 5, 3: 9, 4: 3}
    shape = level_to_mosaic_shape[level] # each mosaic has shape x shape frames
    frame_interval = get_frame_interval(vid_length)
    num_frames = (vid_length / frame_interval) + 2 # 1st & last frame always in

    num_full_rows = int(num_frames // shape)
    num_last_row = round((num_frames / shape - num_full_rows) * shape)

    frame_width, frame_height = get_frame_dims(
            imgs[img_keys[0]].size[0], imgs[img_keys[0]].size[1],
            num_full_rows, num_last_row, shape)

    timestamp = 0
    frames = {}

    for row_idx in range(num_full_rows):
        for col_idx in range(shape):
            # determine what img we're looking at
            global_frame_idx = row_idx * shape + col_idx
            img_idx = (global_frame_idx // (shape * shape))
            curr_img = imgs[img_keys[img_idx]]
            curr_img_row = round(((row_idx / shape) % 1) * shape)

            # crop and add to list with incrementing timestamp
            x = col_idx * frame_width
            y = curr_img_row * frame_height
            frames[timestamp] = curr_img.crop((x, y, x+frame_width, y+frame_height))
            timestamp += frame_interval

    return frames

def get_labels(frames):
    client = vision.Client('treehacks-159123')
    new_frames = {}
    i = 0
    for timestamp, curr_img in frames.items():
        img_bytes = BytesIO()
        curr_img.save(img_bytes, format='png')

        img = client.image(content=img_bytes.getvalue())
        labels = img.detect_labels()
        time.sleep(0.05) # don't set off the firewallll
        new_frames[timestamp] = (curr_img, [l.description for l in labels])
        print ('{}/{}'.format(str(i), len(frames)), end='\r')
        i += 1
    return new_frames

def get_labels_from_url(url):
    page_content = get_page_source(url)
    frames = get_timestamped_frames(
            *get_mosaics(page_content),
            get_vid_length(page_content))
    return get_labels(frames)

