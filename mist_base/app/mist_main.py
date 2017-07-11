from _app import return_app
from endpoints_v2 import api_endpoints
from index import index_routes

app = return_app()

app.register_blueprint(index_routes)
app.register_blueprint(api_endpoints)
