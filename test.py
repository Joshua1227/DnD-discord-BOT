import pymongo
from pymongo import MongoClient
import json
cluster = MongoClient("mongodb+srv://Bad_Wolf:TZ8nRcNL0SskMvyb@dnd.y1p4h.gcp.mongodb.net/DnD?retryWrites=true&w=majority")
db = cluster["DnD"]
collection = db["Characters"]

results = collection.find_one({"_id":0})

#for result in results:
#result = results[0]
print(results["Saving Throws"]["Intelligence"])
