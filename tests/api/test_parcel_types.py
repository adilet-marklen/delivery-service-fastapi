from delivery_service.main import create_app


def test_parcel_types_route_registered() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/api/v1/parcel-types/" in paths
