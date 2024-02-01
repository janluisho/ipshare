import cv2
import qrcode
import urllib
import numpy as np
from PIL import Image
from io import BytesIO
from flask import Blueprint, send_file

from app import limiter

qr_views = Blueprint('qr_views', __name__, template_folder='templates')


# @qr_views.route('/', defaults={'addr': 'ipshare.de'})
@qr_views.route('/<path:addr>')  # need to add path here or the route is not matched correctly resulting in 404
@limiter.limit("1337/day;420/hour;42/minute")
def qr_code(addr):
    address = urllib.parse.unquote_plus(addr)
    img = qrcode.make(address)
    img = np.array(img, dtype=np.uint8)

    img = cv2.resize(img, (1000, 1000), interpolation=cv2.INTER_NEAREST)  # default interpolation gives bad results
    img = img[115:-115, 115:-115]  # cut border. Values depend on dsize and what's encoded (48).

    # Dilate (make the white area smaller)
    kernel = np.ones((7, 7), dtype=np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel)  # MORPH_ERODE

    # Blur (round of the edges)
    img = cv2.GaussianBlur(img, (21, 21), sigmaX=7)

    # Send the image as PNG
    img = Image.fromarray((1-img) * 255)
    fp = BytesIO()  # using BytesIO removes the storage problem. But misses Cashing.
    img.save(fp, format="png")
    fp.seek(0)  # read form the top of the file
    return send_file(fp, mimetype='image/png')


# if __name__ == '__main__':
#     import requests
#     address = urllib.parse.quote_plus("http://127.0.0.1")
#     r = requests.get(f'http://127.0.0.1:5000/qr/{address}')
#     print(r.status_code)
