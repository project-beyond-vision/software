import requests
from datetime import datetime
import numpy as np

#test for 

url = 'http://127.0.0.1:5000/store'
now = datetime.now()

latlongs = ((1.294894, 103.773882, 50), (1.294507, 103.774447, 25), (1.294001, 103.774021, 150), (1.294522, 103.772441, 25))

timenow = now.isoformat()
obj = []
for lat, long, n in latlongs:
    dsb = np.random.multivariate_normal((lat, long), [[0.00001, 0], [0, 0.00001]], n)
    for i in range(n):
        rand_acts = [int(np.random.randint(1, 4)) for _ in range(3)]
        lat, long = dsb[i]
        d = {"time":timenow, "lat":lat, "long": long, "pred1": rand_acts[0], "pred2": rand_acts[1], "pred3": rand_acts[2], "pred4": 4}
        obj.append(d)


for o in obj:
    x = requests.post(url, json=o)
print(x)