from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from app.config import API_PREFIX, API_VERSION

__version__ = "/v1"
__bp__ = "/users"

url_prefix = API_PREFIX + API_VERSION + __bp__

# Define any security requirements or tags if needed
tag = Tag(name='User', description="User management API")

api = APIBlueprint(__bp__, __name__, url_prefix=url_prefix, abp_tags=[tag])


@api.post('/register')
def register():
    # Implement the registration logic here
    return jsonify({"msg": "registration success"})


@api.post('/login')
def login():
    # Implement the login logic here
    return jsonify({"msg": "login success"})
