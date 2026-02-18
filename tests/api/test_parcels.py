from delivery_service.main import create_app


def test_parcels_routes_registered() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/api/v1/parcels/" in paths
    assert "/api/v1/parcels/{parcel_id}" in paths
