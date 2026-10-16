
import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    """Open a connection to the FactoryFlow PostgreSQL database."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5433"),
        dbname=os.getenv("DB_NAME", "factoryflow"),
        user=os.getenv("DB_USER", "factoryflow_user"),
        password=os.getenv("POSTGRES_PASSWORD"),
        connect_timeout=5,
    )


@app.route("/health", methods=["GET"])
def health():
    """Report whether the API and database are available."""
    try:
        with get_db_connection() as connection:
            connection.execute("SELECT 1")

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except psycopg.Error:
        app.logger.exception("Database health check failed")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503

@app.route("/products", methods=["GET"])
def get_products():
    """Return all products from the database."""
    try:
        with get_db_connection() as connection:
            rows = connection.execute(
                """
                SELECT sku, name, category, unit_of_measure
                FROM products
                ORDER BY sku
                """
            ).fetchall()

        products = [
            {
                "sku": row[0],
                "name": row[1],
                "category": row[2],
                "unit_of_measure": row[3],
            }
            for row in rows
        ]

        return jsonify({"products": products}), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve products")
        return jsonify({"error": "Unable to retrieve products"}), 503


@app.route("/inventory", methods=["GET"])
def get_inventory():
    """Return finished-goods inventory by warehouse."""
    try:
        with get_db_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    p.sku,
                    p.name AS product_name,
                    w.code AS warehouse_code,
                    w.name AS warehouse_name,
                    i.quantity
                FROM inventory i
                JOIN products p ON p.id = i.product_id
                JOIN warehouses w ON w.id = i.warehouse_id
                ORDER BY p.sku, w.code
                """
            ).fetchall()

        inventory_items = [
            {
                "sku": row[0],
                "product_name": row[1],
                "warehouse_code": row[2],
                "warehouse_name": row[3],
                "quantity": float(row[4]),
            }
            for row in rows
        ]

        return jsonify({"inventory": inventory_items}), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve inventory")
        return jsonify({"error": "Unable to retrieve inventory"}), 503



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
