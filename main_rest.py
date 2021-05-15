from flask import Flask, request, jsonify, abort
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import json
import copy

with open("holder_f.json") as f:
    HOLDER = json.load(f)

DB_URI = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
    user=HOLDER["user"],
    password=HOLDER["password"],
    host=HOLDER["host"],
    port=HOLDER["port"],
    db=HOLDER["db"])

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    price = db.Column(db.Float, unique=False)
    country = db.Column(db.String(80), unique=False)
    provider = db.Column(db.String(80), unique=False)

    def __init__(self, name, price, country, provider):
        self.name=name
        self.price = price
        self.country = country
        self.provider = provider


class ItemSchema(ma.Schema):
    class Meta:
        fields = ("name", "price", "country", "provider")


item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


@app.route("/item", methods=["POST"])
def add_item():
    data = ItemSchema().load(request.json)
    new_item = Item(**data)

    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item)


@app.route("/item", methods=["GET"])
def get_item():
    all_items = Item.query.all()
    result = items_schema.dump(all_items)
    return jsonify(({"items":result}))


@app.route("/item/<id>", methods=["GET"])
def item_detail(id):

    item = Item.query.get(id)

    if not Item:
        abort(404)

    return item_schema.jsonify(item)



@app.route("/item/<id>", methods=["PUT"])
def item_update(id):
    item = Item.query.get(id)

    if item is None:
        abort(404)

    data = ItemSchema().load(request.json)

    for i in data:
        setattr(item, i, request.json[i])

    db.session.commit()
    return item_schema.jsonify(item)


@app.route("/item/<id>", methods=["DELETE"])
def item_delete(id):
    item = Item.query.get(id)

    if item is None:
        abort(404)

    db.session.delete(item)
    db.session.commit()

    return item_schema.jsonify(item)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")