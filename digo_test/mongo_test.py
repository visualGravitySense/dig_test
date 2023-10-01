from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://helikeel:2aCEOKLIMczzb17U@digo-1.bgjk2no.mongodb.net/?retryWrites=true&w=majority")

db = cluster["QuizBot"]
collection = db["Test"]

# results = collection.find({"name": "Tim"})
# results = collection.find({})
# print(results)

collection.update_one({"name": "Tim"}, {"$set": {"name": "Alex"}})

for result in results:
    print(result)

delete_one, delete_many    

# post1 = {
#     "name": "Tim",
#     "age": 19
# }
#
# post2 = {
#     "name": "Bill",
#     "age": 31
# }

# collection.insert_one(post1)
# collection.insert_many([post1, post2])
