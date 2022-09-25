from .model import User  # noqa

BASE_ROUTE = "user"

def register_routes(api, app, root=""):
    from .controller import api as user_api

    api.add_namespace(user_api, path=f"/{root}/{BASE_ROUTE}")
