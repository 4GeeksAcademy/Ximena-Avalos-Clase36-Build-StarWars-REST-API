import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, favorite_planet, favorite_people

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
Migrate(app, db)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    people_list = [person.serialize() for person in people]
    return jsonify(people_list), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        raise APIException('Person not found', status_code=404)
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    planet_list = [planet.serialize() for planet in planets]
    return jsonify(planet_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1 
    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)
    
    favorite_planets = [planet.serialize() for planet in user.favorite_planets]
    favorite_people = [person.serialize() for person in user.favorite_people]
    favorites = {
        "planets": favorite_planets,
        "people": favorite_people
    }
    return jsonify(favorites), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1 
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if user is None or planet is None:
        raise APIException('User or Planet not found', status_code=404)
    
    user.favorite_planets.append(planet)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1 
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    if user is None or person is None:
        raise APIException('User or People not found', status_code=404)
    
    user.favorite_people.append(person)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if user is None or planet is None:
        raise APIException('User or Planet not found', status_code=404)
    
    user.favorite_planets.remove(planet)
    db.session.commit()
    return '', 204

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1 
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    if user is None or person is None:
        raise APIException('User or People not found', status_code=404)
    
    user.favorite_people.remove(person)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)