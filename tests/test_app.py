from app import app


def test_home_page():
    response = app.test_client().get("/")
    assert response.status_code == 200


def test_health_endpoint():
    response = app.test_client().get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["application"] == "DevOps Dashboard"
