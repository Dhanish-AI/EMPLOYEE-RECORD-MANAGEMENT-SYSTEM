from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://n30475959:Nothing30475959@mycluster.vwwbm.mongodb.net/?retryWrites=true&w=majority&appName=mycluster"

client = MongoClient(CONNECTION_STRING)
collection = client["ERMS"]["empdata"]
for idx, doc in enumerate(collection.find().limit(5), start=1):
    print(f"Document {idx}: {doc}")
client.close()
