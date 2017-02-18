import re
import requests
import time

from PIL import Image
from io import BytesIO


def get_mosaics(url):
    r = requests.get(url)
    match = re.search('\"storyboard_spec\":\"([^\"]*)\"', str(r.content)).group(1).replace('\\\\', '')
    sighs = re.findall('\$M#([^\|$]+)(?:\||$)', match)
    base_url = match[:match.find('|')] + '?sigh=$S'

    l_value = len(sighs)
    sigh = sighs[-1]
    m_value = 0

    base_url = base_url.replace('$L', str(l_value)).replace('$S', sigh)

    imgs = {}
    img_keys = []

    # get all mosaics
    while True:
        mosaic_url = base_url.replace('$N', 'M{}'.format(m_value))
        img_keys.append('mosaics/L{}_M{}_{}'.format(l_value, m_value, sigh))

        r = requests.get(mosaic_url, stream=True)
        if r.status_code != 200:
            print('failed on img_key={}'.format(img_keys[-1]))
            break

        r.raw.decode_content = True
        imgs[img_keys[-1]] = Image.open(r.raw)

        time.sleep(0.5) # do not set off youtube's firewall
        m_value += 1

    return img_keys, imgs, l_value


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=OvXHbJzWMqI'
    level_to_shape = {1: (40, 30), 2: (80, 60), 3: (160, 120), 4: (320, 240)}

    img_keys, imgs, level = get_mosaics(url)
    print('\n'.join(img_keys))

    shape = level_to_shape[level]
