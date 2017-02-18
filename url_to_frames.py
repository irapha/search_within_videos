import re
import requests
import shutil
import time


def url_to_frames(url):
    """given a url, get a list of timestamped frames"""
    r = requests.get(url)
    match = re.search('\"storyboard_spec\":\"([^\"]*)\"', str(r.content)).group(1).replace('\\\\', '')
    sighs = re.findall('\$M#([^\|$]+)(?:\||$)', match)
    base_url = match[:match.find('|')] + '?sigh=$S'

    l_value = len(sighs)
    sigh = sighs[-1]
    m_value = 0

    base_url = base_url.replace('$L', str(l_value)).replace('$S', sigh)

    while True:
        mosaic_url = base_url.replace('$N', 'M{}'.format(m_value))

        r = requests.get(mosaic_url, stream=True)
        if r.status_code != 200:
            print('failed on m_value={}'.format(m_value))
            break

        with open('mosaics/L{}_M{}_{}'.format(l_value, m_value, sigh), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        time.sleep(0.5)

        m_value += 1

    # print(re.search('\$M#', match).pos) # do not work. but we want all positions where this happens
    print(base_url) # replace $L with the l-number, $N with 'M0', 'M1', etc, and add '?sigh=' + the matched thing from above


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=OvXHbJzWMqI'
    url_to_frames(url)
