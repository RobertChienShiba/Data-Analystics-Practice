from pprint import pprint
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId


client = MongoClient()
db = client.pchome
coll = db.products

##MONGODB EXAMPLE

table=db.example
table.insert_many([
 	{ "_id" : 1, "name" : "xPhone", "price" : 799, "releaseDate" : 'ISODate("2011-05-14T00:00:00Z")', "spec" : { "ram" : 4, "screen" : 6.5, "cpu" : 2.66 }, "color" : [ "white", "black" ], "storage" : [ 64, 128, 256 ] },
 	{ "_id" : 2, "name" : "xTablet", "price" : 899, "releaseDate" : 'ISODate("2011-09-01T00:00:00Z")', "spec" : { "ram" : 16, "screen" : 9.5, "cpu" : 3.66 }, "color" : [ "white", "black", "purple" ], "storage" : [ 128, 256, 512 ] },
 	{ "_id" : 3, "name" : "SmartTablet", "price" : 899, "releaseDate" :  'ISODate("2015-01-14T00:00:00Z")', "spec" : { "ram" : 12, "screen" : 9.7, "cpu" : 3.66 }, "color" : [ "blue" ], "storage" : [ 16, 64, 128 ] },
 	{ "_id" : 4, "name" : "SmartPad", "price" : 699, "releaseDate" :  'ISODate("2020-05-14T00:00:00Z")', "spec" : { "ram" : 8, "screen" : 9.7, "cpu" : 1.66 }, "color" : [ "white", "orange", "gold", "gray" ], "storage" : [ 128, 256, 1024 ] },
 	{ "_id" : 5, "name" : "SmartPhone", "price" : 599, "releaseDate" : 'ISODate("2022-09-14T00:00:00Z")', "spec" : { "ram" : 4, "screen" : 9.7, "cpu" : 1.66 }, "color" : [ "white", "orange", "gold", "gray" ], "storage" : [ 128, 256 ] },
 	{ "_id" : 6, "name" : "xWidget", "spec" : { "ram" : 64, "screen" : 9.7, "cpu" : 3.66 }, "color" : [ "black" ], "storage" : [ 1024 ] }
])
table.insert_one({ "_id" : 7, "name" : "xReader","price": 'null', "spec" : { "ram" : 64, "screen" : 6.7, "cpu" : 3.66 }, "color" : [ "black", "white" ], "storage" : [ 128 ] })
table.insert_many(([
 	{  "name" : "xPhone", "price" : 799, "releaseDate" : 'ISODate("2011-05-14T00:00:00Z")', "spec" : { "ram" : 4, "screen" : 6.5, "cpu" : 2.66 }, "color" : [ "white", "black" ], "storage" : [ 64, 128, 256 ] },
 	{"name" : "xTablet", "price" : 899, "releaseDate" : 'ISODate("2011-09-01T00:00:00Z")', "spec" : { "ram" : 16, "screen" : 9.5, "cpu" : 3.66 }, "color" : [ "white", "black", "purple" ], "storage" : [ 128, 256, 512 ] },
 	{  "name" : "SmartTablet", "price" : 899, "releaseDate" : 'ISODate("2015-01-14T00:00:00Z")', "spec" : { "ram" : 12, "screen" : 9.7, "cpu" : 3.66 }, "color" : [ "blue" ], "storage" : [ 16, 64, 128 ] },
 	{ "name" : "SmartPad", "price" : 699, "releaseDate" : 'ISODate("2020-05-14T00:00:00Z")', "spec" : { "ram" : 8, "screen" : 9.7, "cpu" : 1.66 }, "color" : [ "white", "orange", "gold", "gray" ], "storage" : [ 128, 256, 1024 ] },
 	{"name" : "SmartPhone", "price" : 599, "releaseDate" : 'ISODate("2022-09-14T00:00:00Z")', "spec" : { "ram" : 4, "screen" : 9.7, "cpu" : 1.66 }, "color" : [ "white", "orange", "gold", "gray" ], "storage" : [ 128, 256 ] }
]))
table.insert_one({  "name" : "xPhone", "price" : 799, "releaseDate" : datetime.strptime("2011-05-14 00:00:00", '%Y-%m-%d %H:%M:%S'), "spec" : { "ram" : 4, "screen" : 6.5, "cpu" : 2.66 }, "color" : [ "white", "black" ], "storage" : [ 64, 128, 256 ] })
table.update_one({'releaseDate':{'$type':['date']}},{'$set':{'releaseDate':datetime.strptime("2011-09-01 00:00:00",'%Y-%m-%d %H:%M:%S')}})
table.insert_one({  "name" : "SmartPhone", "price" : [599,699,799,999],"releaseDate": datetime.strptime("2011-05-14 00:00:00", '%Y-%m-%d %H:%M:%S'), "spec" : { "ram" : 4, "screen" : 5.7, "cpu" : 1.66 },"color":["white","orange","gold","gray"],"storage":[128,256]})
table.update_one({"_id":ObjectId('611a9ef95dd672085faa3087')}, {'$max': { 'price': 799}})
table.update_many({}, {'$unset': {'releaseDate': "",'spec.ram': "",'storage.0':""}})
table.update_many({ '_id': 6 },{ '$set': {'price': 999} },upsert=True)
table.delete_one({'_id':ObjectId('611a9ef95dd672085faa3087')})
table.delete_many({'spec.cpu':3.66})


for idx,db in enumerate(table.find({'releaseDate':{'$type':'string'}},{'releaseDate':1,'_id':False})):
    if idx % 3 == 0:
        table.update_one(db,{'$set':{'releaseDate':datetime.strptime("2011-01-14 00:00:00",'%Y-%m-%d %H:%M:%S')}})
    elif idx % 3 == 1:
        table.update_one(db,{'$set':{'releaseDate':datetime.strptime("2011-05-14 00:00:00",'%Y-%m-%d %H:%M:%S')}}) 
    else:
        table.update_one(db,{'$set':{'releaseDate':datetime.strptime("2011-09-14 00:00:00",'%Y-%m-%d %H:%M:%S')}})


pprint(list(table.find({'releaseDate':{'$type':['date']}},{'releaseDate':1})))
pprint(list(table.find({"_id":ObjectId('611a9ef95dd672085faa3087')})))
pprint(list(table.find()))
pprint(list(table.find({},{'name': 1,'price': 1},skip=2,limit=3).sort([('price', -1),('name',1)])))
pprint(list(table.find({'price': {'$exists': True,'$gt': 699}}, {'name': 1,'price': 1})))
pprint(list(table.find(  { 'name':{'$not': {'$regex':'^Smart.+'}}}, {'name': 1})))
pprint(list(table.find({
    'storage': {
        '$gte': 64,
        '$lte': 128
    }
}, {
    'name': 1,
    'storage': 1
})))

##PCHOME

print(coll.count())
pprint.pprint(list(coll.find({'price': 13999},{'_id':0,'name':1,'price':1})))
pprint.pprint(coll.find())

# name containing asus
name_condition = {'name': {'$regex': '.*三星.*', '$options': 'i'}}
data = coll.find(name_condition)
for d in data :
    print(d)

price_condition = {'price': {'$gt': 10000}}
# data = coll.find(price_condition)

# and operator example
data = coll.find({'$and': [name_condition, price_condition]})
for d in data:
    print(d['name'], d['price'])


coll.update_one({'name': 'ASUS XG32VQR(低藍光+不閃屏)'}, {'$set': {'price': 8000}}, upsert=True )

#upsert example (insert if not exist)
coll.update_one({'name': 'Allen'}, {'$set': {'name': 'Allen'}}, upsert=True)

#delete example
coll.delete_one({'name': 'Allen'})
