import app.utils.caption
from app.utils import vision
from algoliasearch import algoliasearch

client = algoliasearch.Client("Y9MCTNJ20T", "5c85dabf76ed1ba90c86b74f3470d965")

def tag_and_upload(url):
    print("getting frames")
    frames = vision.get_labels_from_url(url)
    timestamps = list(sorted(frames.keys()))
    captions = caption.get_timestamped_captions(url, timestamps)
    out = []
    print (captions)
    print (frames)
    for time in timestamps:
        print (time)
        data = {}
        if time in frames:
            data['labels'] = frames[time][1]
        if time in captions:
            data['text'] = captions[time]
        data['time'] = time * 1000
        data['url'] = url 
        out.append(data)
    index = client.init_index("frames")
    index.add_objects(out)