"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)



@app.route('/people', methods=['GET'])
def get_all_people():
    """GET /people - Listar todos los personajes"""
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    """GET /people/<id> - Obtener un personaje específico"""
    person = People.query.get(people_id)
    
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    
    return jsonify(person.serialize()), 200



@app.route('/planets', methods=['GET'])
def get_all_planets():
    """GET /planets - Listar todos los planetas"""
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    """GET /planets/<id> - Obtener un planeta específico"""
    planet = Planet.query.get(planet_id)
    
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    return jsonify(planet.serialize()), 200



@app.route('/users', methods=['GET'])
def get_all_users():
    """GET /users - Listar todos los usuarios"""
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    """GET /users/favorites - Listar favoritos del usuario actual"""
    # usamos user_id=1 (hardcodeado)
    user_id = request.args.get('user_id', 1, type=int)
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([fav.serialize() for fav in favorites]), 200



@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    """POST /favorite/people/<id> - Añadir personaje a favoritos"""
    user_id = request.json.get('user_id', 1)
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    
    existing = Favorite.query.filter_by(
        user_id=user_id,
        favorite_type='people',
        favorite_id=people_id
    ).first()
    
    if existing:
        return jsonify({"error": "Already in favorites"}), 400
    
    favorite = Favorite(
        user_id=user_id,
        favorite_type='people',
        favorite_id=people_id
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify(favorite.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    """POST /favorite/planet/<id> - Añadir planeta a favoritos"""
    user_id = request.json.get('user_id', 1)
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    existing = Favorite.query.filter_by(
        user_id=user_id,
        favorite_type='planet',
        favorite_id=planet_id
    ).first()
    
    if existing:
        return jsonify({"error": "Already in favorites"}), 400
    
    favorite = Favorite(
        user_id=user_id,
        favorite_type='planet',
        favorite_id=planet_id
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify(favorite.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    """DELETE /favorite/people/<id> - Eliminar personaje de favoritos"""
    user_id = request.args.get('user_id', 1, type=int)
    
    favorite = Favorite.query.filter_by(
        user_id=user_id,
        favorite_type='people',
        favorite_id=people_id
    ).first()
    
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Favorite removed successfully"}), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    """DELETE /favorite/planet/<id> - Eliminar planeta de favoritos"""
    user_id = request.args.get('user_id', 1, type=int)
    
    favorite = Favorite.query.filter_by(
        user_id=user_id,
        favorite_type='planet',
        favorite_id=planet_id
    ).first()
    
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Favorite removed successfully"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)