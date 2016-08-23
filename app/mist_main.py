from _app import return_app
from endpoints_v1 import api_auth
from index import index_routes

app = return_app()

app.register_blueprint(index_routes)
app.register_blueprint(api_auth)

