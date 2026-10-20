
import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, jsonify, request

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

@app.route("/batches", methods=["POST"])
def create_batch():
    """Create a new production batch."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "A JSON request body is required"}), 400

    batch_number = data.get("batch_number")
    product_sku = data.get("product_sku")
    planned_quantity = data.get("planned_quantity")

    if not batch_number or not isinstance(batch_number, str):
        return jsonify({"error": "A valid batch_number is required"}), 400

    if not product_sku or not isinstance(product_sku, str):
        return jsonify({"error": "A valid product_sku is required"}), 400

    if isinstance(planned_quantity, bool):
        return jsonify({"error": "planned_quantity must be a positive number"}), 400

    try:
        planned_quantity = float(planned_quantity)
        if planned_quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "planned_quantity must be a positive number"}), 400

    try:
        with get_db_connection() as connection:
            product = connection.execute(
                "SELECT id FROM products WHERE sku = %s",
                (product_sku.strip(),),
            ).fetchone()

            if product is None:
                return jsonify({"error": "Product not found"}), 404

            batch = connection.execute(
                """
                INSERT INTO production_batches
                    (batch_number, product_id, planned_quantity, status)
                VALUES (%s, %s, %s, 'planned')
                RETURNING id, batch_number, planned_quantity, status
                """,
                (batch_number.strip(), product[0], planned_quantity),
            ).fetchone()

        return jsonify({
            "message": "Production batch created successfully",
            "batch": {
                "id": batch[0],
                "batch_number": batch[1],
                "planned_quantity": float(batch[2]),
                "status": batch[3],
            },
        }), 201

    except psycopg.IntegrityError:
        return jsonify({
            "error": "A batch with this batch_number already exists"
        }), 409

    except psycopg.Error:
        app.logger.exception("Failed to create production batch")
        return jsonify({"error": "Unable to create production batch"}), 503

@app.route("/batches", methods=["GET"])
def get_batches():
    """Return all production batches."""
    try:
        with get_db_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    pb.id,
                    pb.batch_number,
                    p.sku,
                    p.name AS product_name,
                    pb.planned_quantity,
                    pb.actual_quantity,
                    pb.status,
                    pb.created_at
                FROM production_batches pb
                JOIN products p ON p.id = pb.product_id
                ORDER BY pb.created_at DESC, pb.id DESC
                """
            ).fetchall()

        batches = [
            {
                "id": row[0],
                "batch_number": row[1],
                "product_sku": row[2],
                "product_name": row[3],
                "planned_quantity": float(row[4]),
                "actual_quantity": (
                    float(row[5]) if row[5] is not None else None
                ),
                "status": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
            }
            for row in rows
        ]

        return jsonify({"batches": batches}), 200

    except psycopg.Error:
        app.logger.exception("Failed to retrieve production batches")
        return jsonify({"error": "Unable to retrieve production batches"}), 503

@app.route("/batches/<batch_number>", methods=["PATCH"])
def update_batch_status(batch_number):
    """Update production progress for a batch."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON request body is required"}), 400

    new_status = data.get("status")
    actual_quantity = data.get("actual_quantity")

    if new_status not in {"in_progress", "completed", "cancelled"}:
        return jsonify({"error": "Invalid target status"}), 400

    if new_status == "completed":
        if isinstance(actual_quantity, bool) or not isinstance(
            actual_quantity, int
        ) or actual_quantity < 0:
            return jsonify({
                "error": "A non-negative integer actual_quantity is required"
            }), 400

    try:
        with get_db_connection() as connection:
            batch = connection.execute(
                """
                SELECT id, status
                FROM production_batches
                WHERE batch_number = %s
                FOR UPDATE
                """,
                (batch_number,),
            ).fetchone()

            if batch is None:
                return jsonify({"error": "Production batch not found"}), 404

            current_status = batch[1]

            allowed_transitions = {
                "planned": {"in_progress", "cancelled"},
                "in_progress": {"completed", "cancelled"},
                "completed": set(),
                "cancelled": set(),
            }

            if new_status not in allowed_transitions.get(current_status, set()):
                return jsonify({
                    "error": (
                        f"Cannot change status from "
                        f"{current_status} to {new_status}"
                    )
                }), 409

            if new_status == "in_progress":
                updated_batch = connection.execute(
                    """
                    UPDATE production_batches
                    SET status = %s, started_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, batch_number, status, actual_quantity,
                              started_at, completed_at
                    """,
                    (new_status, batch[0]),
                ).fetchone()

            elif new_status == "completed":
                updated_batch = connection.execute(
                    """
                    UPDATE production_batches
                    SET status = %s,
                        actual_quantity = %s,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, batch_number, status, actual_quantity,
                              started_at, completed_at
                    """,
                    (new_status, actual_quantity, batch[0]),
                ).fetchone()

            else:
                updated_batch = connection.execute(
                    """
                    UPDATE production_batches
                    SET status = %s
                    WHERE id = %s
                    RETURNING id, batch_number, status, actual_quantity,
                              started_at, completed_at
                    """,
                    (new_status, batch[0]),
                ).fetchone()

        return jsonify({
            "message": "Production batch updated successfully",
            "batch": {
                "id": updated_batch[0],
                "batch_number": updated_batch[1],
                "status": updated_batch[2],
                "actual_quantity": updated_batch[3],
                "started_at": (
                    updated_batch[4].isoformat()
                    if updated_batch[4] else None
                ),
                "completed_at": (
                    updated_batch[5].isoformat()
                    if updated_batch[5] else None
                ),
            },
        }), 200

    except psycopg.Error:
        app.logger.exception("Failed to update production batch")
        return jsonify({"error": "Unable to update production batch"}), 503
@app.route("/reports/production", methods=["GET"])
def production_report():
    """Return aggregate production performance metrics."""
    try:
        with get_db_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_batches,
                    COUNT(*) FILTER (
                        WHERE status = 'completed'
                    ) AS completed_batches,
                    COALESCE(SUM(planned_quantity), 0)
                        AS total_planned_quantity,
                    COALESCE(
                        SUM(planned_quantity)
                        FILTER (WHERE status = 'completed'),
                        0
                    ) AS completed_planned_quantity,
                    COALESCE(
                        SUM(actual_quantity)
                        FILTER (WHERE status = 'completed'),
                        0
                    ) AS total_actual_quantity
                FROM production_batches
                """
            ).fetchone()

        total_batches = row[0]
        completed_batches = row[1]
        planned_quantity = float(row[2])
        completed_planned_quantity = float(row[3])
        actual_quantity = float(row[4])

        production_yield = (
            round(
                actual_quantity / completed_planned_quantity * 100, 2
            )
            if completed_planned_quantity > 0
            else 0.0
        )

        quantity_variance = actual_quantity - completed_planned_quantity

        return jsonify({
            "report": {
                "total_batches": total_batches,
                "completed_batches": completed_batches,
                "planned_quantity": planned_quantity,
                "actual_quantity": actual_quantity,
                "production_yield_percent": production_yield,
                "quantity_variance": quantity_variance,
            }
        }), 200

    except psycopg.Error:
        app.logger.exception("Failed to generate production report")
        return jsonify({
            "error": "Unable to generate production report"
        }), 503

print(app.url_map)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
