
from unittest.mock import MagicMock, patch

import pytest

from app.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@patch("app.app.get_db_connection")
def test_health_success(mock_get_connection, client):
    mock_connection = MagicMock()
    mock_get_connection.return_value.__enter__.return_value = mock_connection

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "healthy",
        "database": "connected",
    }
    mock_connection.execute.assert_called_once_with("SELECT 1")


@patch("app.app.get_db_connection")
def test_products_success(mock_get_connection, client):
    mock_connection = MagicMock()
    mock_connection.execute.return_value.fetchall.return_value = [
        ("FF-HC-001", "Laundry Detergent", "Home Care", "bottle"),
        ("FF-HC-002", "Surface Cleaner", "Home Care", "bottle"),
        ("FF-PC-001", "Liquid Hand Soap", "Personal Care", "bottle"),
    ]
    mock_get_connection.return_value.__enter__.return_value = mock_connection

    response = client.get("/products")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["products"]) == 3
    assert data["products"][0]["sku"] == "FF-HC-001"
    assert data["products"][0]["name"] == "Laundry Detergent"


@patch("app.app.get_db_connection")
def test_inventory_success(mock_get_connection, client):
    mock_connection = MagicMock()
    mock_connection.execute.return_value.fetchall.return_value = [
        ("FF-HC-001", "Laundry Detergent", "WH-LAG-01",
         "Lagos Distribution Warehouse", 250),
        ("FF-HC-002", "Surface Cleaner", "WH-LAG-01",
         "Lagos Distribution Warehouse", 120),
        ("FF-PC-001", "Liquid Hand Soap", "WH-LAG-01",
         "Lagos Distribution Warehouse", 180),
    ]
    mock_get_connection.return_value.__enter__.return_value = mock_connection

    response = client.get("/inventory")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["inventory"]) == 3
    assert data["inventory"][0]["sku"] == "FF-HC-001"
    assert data["inventory"][0]["quantity"] == 250.0
