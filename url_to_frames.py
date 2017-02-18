import re
import requests


def url_to_frames(url):
    """given a url, get a list of timestamped frames"""
    r = requests.get(url)
    match = re.search('\"storyboard_spec\":\"([^\"]*)\"', str(r.content)).group(1)
    match = match.replace('\\\\', '')
    base_url = match[:match.find('|')]

    # in order of preference: L3, L2, L4, L1
    print(match)
    # print(re.search('\$M#', match).pos) # do not work. but we want all positions where this happens
    print(base_url) # replace $L with the l-number, $N with 'M0', 'M1', etc, and add '?sigh=' + the matched thing from above


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=OvXHbJzWMqI'
    url_to_frames(url)
