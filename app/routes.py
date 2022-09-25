
def register_routes(api, app, root=""):
    from app.user import register_routes as attach_user

    # Add routes
    attach_user(api, app)