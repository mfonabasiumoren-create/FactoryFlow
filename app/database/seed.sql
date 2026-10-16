-- FactoryFlow sample FMCG products
INSERT INTO products (sku, name, category, unit_of_measure)
VALUES
    ('FF-HC-001', 'Laundry Detergent', 'Home Care', 'bottle'),
    ('FF-PC-001', 'Liquid Hand Soap', 'Personal Care', 'bottle'),
    ('FF-HC-002', 'Surface Cleaner', 'Home Care', 'bottle')
ON CONFLICT (sku) DO NOTHING;

-- Sample raw materials
INSERT INTO raw_materials (
    sku, name, unit_of_measure, quantity_on_hand, reorder_level
)
VALUES
    ('RM-001', 'Detergent Base', 'kg', 500.000, 100.000),
    ('RM-002', 'Plastic Bottles', 'unit', 2000.000, 500.000),
    ('RM-003', 'Fragrance Concentrate', 'litre', 80.000, 20.000),
    ('RM-004', 'Liquid Soap Base', 'kg', 300.000, 75.000)
ON CONFLICT (sku) DO NOTHING;

-- Sample distribution warehouse
INSERT INTO warehouses (code, name, location)
VALUES
    ('WH-LAG-01', 'Lagos Distribution Warehouse', 'Lagos, Nigeria')
ON CONFLICT (code) DO NOTHING;

-- Initial finished-goods inventory
INSERT INTO inventory (product_id, warehouse_id, quantity)
SELECT p.id, w.id, stock.quantity
FROM (
    VALUES
        ('FF-HC-001', 250),
        ('FF-PC-001', 180),
        ('FF-HC-002', 120)
) AS stock(sku, quantity)
JOIN products p ON p.sku = stock.sku
CROSS JOIN warehouses w
WHERE w.code = 'WH-LAG-01'
ON CONFLICT (product_id, warehouse_id) DO NOTHING;