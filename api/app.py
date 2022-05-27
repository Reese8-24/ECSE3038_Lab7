from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
from flask_pymongo import PyMongo
from json import loads
from dotenv import load_dotenv
from marshmallow import Schema, ValidationError, fields
from bson.json_util import dumps


load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = os.getenv("MONGO_CONNECTION_STRING")
mongo = PyMongo(app)

class TankSchema(Schema):
    location = fields.String(required=True)
    long = fields.Float(required=True)
    lat= fields.Float(required=True)
    percentage_full = fields.Integer(required=True)
    
@app.route("/data", methods=["POST"])
def add_new_data():
    request_dict = request.json 
    try: 
        new_tank = TankSchema().load(request_dict)
    except ValidationError as err:
        return(err.messages, 400)
    
    tank_document = mongo.db.tanks.insert_one(new_tank)
    tank_id = tank_document.inserted_id

    tank = mongo.db.tanks.find_one({"_id": tank_id})

    tank_json = loads(dumps(tank))

    return jsonify(tank_json)
        
@app.route("/data", methods=["GET"])
def get_data():
    tanks = mongo.db.tanks.find()
    tanks_list = loads(dumps(tanks))

    return jsonify(tanks_list)

@app.route("/data/<ObjectId:id>", methods=["PATCH"])
def update_tank(id):
    request_dict = request.json 

    try: 
        TankSchema(partial=True).load(request_dict)
    except ValidationError as err:
        return(err.messages, 400)

    mongo.db.tanks.update_one({"_id": id}, {"$set": request.json})

    tank = mongo.db.tanks.find_one(id)

    tank_json = loads(dumps(tank))
    
    return jsonify(tank_json)

@app.route("/data/<ObjectId:id>", methods=["DELETE"])
def delete_tank(id):      
    tank = mongo.db.tanks.delete_one({"_id": id})

    if tank.deleted_count == 1:
        return { "success": True }
    return { "success": False }, 404
# ==============================================================================================
class Level(Schema):
	tank_id = fields.String(required=True)
	water_level=fields.Integer(required=True)

@app.route("/tank",methods=["POST"])
def stat():
    ledstat = False
    request_dict = request.json 
    try: 
        new_tank = Level().load(request_dict)
    except ValidationError as err:
        return(err.messages, 400)
    
    tank_document = mongo.db.levels.insert_one(new_tank)
    tank_id = tank_document.inserted_id
    tank = mongo.db.levels.find_one({"_id": tank_id})
    tank_json = loads(dumps(tank))
    if tank_json["water_level"] in range(80,101):
        ledstat=True
    responeobj={
	"led": ledstat,
	"msg": "data saved successfully",
	"date": str(datetime.now()),
    }
    return jsonify(responeobj)

if __name__ == '__main__':
    app.run(debug=True, host="192.168.0.8", port="3000")
