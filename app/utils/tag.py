from app.utils import caption
from app.utils import vision
from algoliasearch import algoliasearch

client = algoliasearch.Client("Y9MCTNJ20T", "5c85dabf76ed1ba90c86b74f3470d965")

def merge(url, captions, frames, timestamps, progress_cb, so_far, task_weight):
    out = []
    total = len(timestamps)
    for i, time in enumerate(timestamps):
        data = {}
        if time in frames:
            data['labels'] = frames[time][1]
        if time in captions:
            data['text'] = captions[time]
        data['time'] = time * 1000
        data['url'] = url
        out.append(data)
        progress_cb(so_far + (task_weight * (i / total)), 100)
    return out

def tag_and_upload(url, progress_cb):
    # 70 percent
    frames = vision.get_labels_from_url(url, progress_cb, 0, 70)

    # 20 percent
    timestamps = list(sorted(frames.keys()))
    captions = caption.get_timestamped_captions(url, timestamps, progress_cb, 70, 20)

    # 10 percent
    # TODO: save images in db and store id in res too.
    res = merge(url, captions, frames, timestamps, progress_cb, 90, 10)

    index = client.init_index("frames")
    index.add_objects(res)
    progress_cb(100, 100)
