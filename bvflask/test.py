import requests
from datetime import datetime

#test for 

url = 'http://127.0.0.1:5000/store'
now = datetime.now()
obj ={"time":now.isoformat(), "lat":1.42, "long": 1.36, "pred1": 1, "pred2": 2, "pred3": 3, "pred4": 4}

x = requests.post(url, json=obj)
print(x)