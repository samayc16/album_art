"""import stuff"""

import numpy as np
from PIL import Image
import cv2
import urllib.request
import musicbrainzngs
import os
import fast_colorthief
import billboard
from datetime import date
from dateutil.rrule import rrule, WEEKLY
musicbrainzngs.set_useragent("album_scraping", "1.0", "samayc16",)

QUANT = 16
OUTPUT_IMG_SIZE = 128

"""helper functions"""

quantize = np.vectorize(lambda x: 255 if x >= 248 
                        else QUANT * round(x / QUANT))

def process_img_url_128(img_url):
    urllib.request.urlretrieve(img_url, "img.jpg")
    img = cv2.imread('img.jpg')[:,:,::-1]
    img = cv2.resize(img, dsize = (OUTPUT_IMG_SIZE, OUTPUT_IMG_SIZE), interpolation = cv2.INTER_CUBIC)
    np.asarray('img')
    return img

def get_dominant_color():
    dominant = fast_colorthief.get_dominant_color("img.jpg", quality = 1)
    dominant = quantize(dominant)
    dominant = np.char.mod('%d', dominant)
    return '_'.join(dominant)

def get_album(artist, album):
    ## get img_url
    result = musicbrainzngs.search_releases(release = album, artist = artist, limit=1, primarytype = 'Album')
    album_id = result["release-list"][0]["id"]
    release_id = musicbrainzngs.get_release_by_id(album_id)['release']['id']
    img_url = 'https://coverartarchive.org/release/' + release_id + '/front'
    ## process img
    img = process_img_url_128(img_url)
    ## save album art to quantized color folder
    dominant = 'colors/' + get_dominant_color()
    img = Image.fromarray(img)
    if not os.path.exists(dominant): os.mkdir(dominant)
    img.save(dominant + "/" + release_id + ".jpg")

"""do stuff"""

## Billboard API
# initializing the start and end date
start_date = date(1985, 1, 1)
end_date = date.today()
date_range = rrule(WEEKLY, dtstart=start_date, until=end_date)
current, total = 1, date_range.count()
 
# iterating over the dates
for day in date_range:
    print("%.2f%% done, Currently on week %d of %d" % ((100 * current/total), current, total))
    chart = billboard.ChartData('billboard-200', date = day.strftime("%Y-%m-%d"))
    current += 1
    curr = 1
    for song in chart:
        print('Song %d of %d' % (curr, len(chart)))
        artist, title = song.artist, song.title
        curr += 1
        try : get_album(artist, title)
        except: pass 