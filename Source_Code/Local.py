import io
import cv2
import requests

# Special token you can test for in calling code
SERVER_DOWN_TOKEN = "<<SERVER_DOWN>>"

def send_image_to_qwen(opencv_img, url, prompt,
                       *, fmt=".png", timeout=30, session=None):
    """
    Send an already-loaded OpenCV image to a Qwen-VL Flask endpoint.

    Returns
    -------
    str
        • The model’s clean reply on success.  
        • The constant SERVER_DOWN_TOKEN if the request fails (timeout,
          connection error, non-JSON reply, etc.).  You can compare against
          this value outside the function to detect server problems.
    """
    # 1) Encode the OpenCV (BGR) image to bytes in memory
    ok, buf = cv2.imencode(fmt, opencv_img)
    if not ok:
        raise ValueError("Failed to encode image with OpenCV")

    img_bytes = buf.tobytes()
    files = {
        "image": (f"upload{fmt}",
                  io.BytesIO(img_bytes),
                  "image/png" if fmt == ".png" else "image/jpeg")
    }
    data  = {"prompt": prompt}

    sess = session or requests.Session()

    try:
        resp = sess.post(url, files=files, data=data, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()                 # may raise ValueError if not JSON
    except (requests.RequestException, ValueError):
        # Connection, timeout, HTTP error, or bad JSON → signal server problem
        return SERVER_DOWN_TOKEN

    raw = payload.get("description", "")
    if "\nassistant\n" in raw:
        return raw.split("\nassistant\n")[-1].strip()
    return raw.strip()

import cv2

img   = cv2.imread("WebCam/logo.png")              # already have the image
url   = "http://192.168.100.32:5000/predict"
prompt = "Describe the image"

reply = send_image_to_qwen(img, url, prompt)
print("Model reply:", reply)


# import time
# import io
# import requests

# URL          = "http://192.168.100.32:5000/predict"
# IMAGE_PATH   = "WebCam/logo.png"
# PROMPT_TEXT  = "Describe the image"
# N_REQUESTS   = 30

# # Read the image into memory once
# with open(IMAGE_PATH, "rb") as f:
#     img_bytes = f.read()

# session    = requests.Session()        # connection-reuse is faster
# durations  = []

# for i in range(N_REQUESTS):
#     files = {"image": ("logo.png", io.BytesIO(img_bytes), "image/png")}
#     data  = {"prompt": PROMPT_TEXT}

#     start = time.perf_counter()
#     resp  = session.post(URL, files=files, data=data, timeout=60)
#     resp.raise_for_status()            # raise if the server returns an error
#     durations.append(time.perf_counter() - start)

# total_time   = sum(durations)
# avg_latency  = total_time / N_REQUESTS
# fps          = N_REQUESTS / total_time

# print(f"Requests sent       : {N_REQUESTS}")
# print(f"Total elapsed time  : {total_time:.2f} s")
# print(f"Average per request : {avg_latency:.3f} s")
# print(f"Effective FPS       : {fps:.2f}")
