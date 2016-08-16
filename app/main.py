from _app import return_app
from index import index_routes
from auth import api_auth

app = return_app()

app.register_blueprint(index_routes)
app.register_blueprint(api_auth)

