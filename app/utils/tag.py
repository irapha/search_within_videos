import caption
import vision
from algoliasearch import algoliasearch

client = algoliasearch.Client("Y9MCTNJ20T", "5c85dabf76ed1ba90c86b74f3470d965")

def tag_and_upload(url):
    frames = vision.get_labels_from_url(url)
    timestamps = list(sorted(frames.keys()))
    captions = caption.get_timestamped_captions(url, timestamps)
tag_and_upload('https://www.youtube.com/watch?v=pZOF9q5fzfs')