import base64
import hashlib
import urllib.request

url = "https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"
with urllib.request.urlopen(url) as response:
    data = response.read()

digest = hashlib.sha384(data).digest()
print("sha384-" + base64.b64encode(digest).decode("ascii"))
