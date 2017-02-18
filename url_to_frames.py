import re
import requests
import time

from PIL import Image
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

def get_timestamped_frames(img_keys, imgs, level, vid_length):
    level_to_mosaic_shape = {1: 10, 2: 5, 3: 9, 4: 3}
    shape = level_to_mosaic_shape[level] # each mosaic has shape x shape frames
    frame_interval = get_frame_interval(vid_length)
    num_frames = (vid_length / frame_interval) + 2 # 1st & last frame always in

    num_full_rows = num_frames // shape
    num_last_row = round((num_frames / shape - num_full_rows) * shape)

    for row_idx in range(num_full_rows):
        for frame_idx in range(shape):
            # determine what img we're looking at
            # determine the height of a frame
            # crop and add to list



if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=OvXHbJzWMqI'
    page_content = get_page_source(url)

    vid_length = get_vid_length(page_content)
    frames = get_timestamped_frames(*get_mosaics(page_content), vid_length)

