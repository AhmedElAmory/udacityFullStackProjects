import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


## ROUTES

@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()

    return jsonify({'success': True, 'drinks': [drink.short()
                   for drink in drinks]})


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks = Drink.query.all()

    return jsonify({'success': True, 'drinks': [drink.long()
                   for drink in drinks]})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    body = request.get_json()

    if 'title' and 'recipe' not in body:
        abort(422)

    drink = Drink(title=body['title'], recipe=json.dumps(body['recipe'
                  ]))

    drink.insert()

    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):

    body = request.get_json()

    drink = Drink.query.filter_by(id=id).first()

    if drink is None:
        abort(404)

    if 'title' in body:
        drink.title = body['title']

    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    drink.update()

    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({'success': True, 'delete': drink.id})


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({'success': False, 'error': 422,
            'message': 'unprocessable'}), 422)


@app.errorhandler(404)
def unprocessable(error):
    return (jsonify({'success': False, 'error': 404,
            'message': 'Page not Found'}), 404)


@app.errorhandler(AuthError)
def unprocessable(error):
    return (jsonify({'success': False, 'error': error.status_code,
            'message': error.error['description']}), error.status_code)
