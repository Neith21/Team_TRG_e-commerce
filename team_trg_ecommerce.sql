-- ¡¡¡ IMPORTANTE, PRIMERO CREAR LA BD Y LUEGO HACER LAS MIGRACIONES !!! -
CREATE DATABASE IF NOT EXISTS team_trg_ecommerce;
USE team_trg_ecommerce;

-- ¡¡¡ LUEGO DE HACER LAS MIGRACIONES PROCEDER A INSERTAR SÓLO SI YA SE CREÓ UN SUPERUSUARIO !!! --
INSERT INTO category (name, description, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
('Electrónica', 'Dispositivos y accesorios tecnológicos.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Hogar y Jardín', 'Artículos para la decoración y mantenimiento del hogar.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Ropa y Accesorios', 'Vestimenta, calzado y complementos de moda.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Deportes y Aire Libre', 'Equipamiento para actividades físicas y recreativas.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Libros y Papelería', 'Material de lectura, escritura y oficina.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO subcategory (category_id, name, description, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
(1, 'Teléfonos Móviles', 'Smartphones y teléfonos básicos.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 'Laptops y Computadoras', 'Equipos portátiles y de escritorio.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 'Muebles de Interior', 'Sofás, mesas, sillas y estanterías.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 'Camisetas y Tops', 'Prendas superiores para hombre y mujer.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 'Zapatos Deportivos', 'Calzado especializado para correr y entrenar.', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO unit (name, type, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
('Pieza', 'Cantidad', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Kilogramo', 'Peso', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Litro', 'Volumen', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Caja de 12', 'Cantidad', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Metro', 'Longitud', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO product (uuid, code, sku, name, size, description, presentation, category_id, subcategory_id, purchase_unit_id, sale_unit_id, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
('11e73c3073e411f0916d212d4004b297', 'ELE-TEL-00001', 'SKU-IPHONE15', 'Teléfono Móvil Pro', '6.1 pulgadas', 'El último modelo con cámara avanzada.', 'Caja sellada', 1, 1, 1, 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('b2c3d4e5f6a78901234567890abcdef1', 'ELE-LAP-00002', 'SKU-MACBOOKM3', 'Laptop Air M3', '13 pulgadas', 'Ultrabook ligera y potente para profesionales.', 'Caja con accesorios', 1, 2, 1, 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('c3d4e5f6a7b8901234567890abcdef12', 'HOG-MUE-00003', 'SKU-SOFA-GRIS', 'Sofá de 3 Plazas', '2m x 0.9m', 'Sofá de tela color gris oscuro.', 'Embalado', 2, 3, 1, 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('d4e5f6a7b8c901234567890abcdef123', 'ROP-CAM-00004', 'SKU-TSHIRT-L', 'Camiseta Básica de Algodón', 'Talla L', 'Camiseta de algodón suave color blanco.', 'Bolsa individual', 3, 4, 1, 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('e5f6a7b8c9d01234567890abcdef1234', 'ROP-ZAP-00005', 'SKU-NIKE-RUN-42', 'Zapatos para Correr', 'Talla 42', 'Zapatos con amortiguación para largas distancias.', 'Caja de zapatos', 3, 5, 1, 1, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO provider (name, country, address, phone, email, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
('TecnoGlobal S.A. de C.V.', 'Estados Unidos', '123 Tech Avenue, Silicon Valley, CA 94043', '+16505550101', 'ventas@tecnoglobal.com', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('OfiSuministros Express', 'El Salvador', 'Calle El Progreso, #52, San Salvador', '+50322223333', 'contacto@ofisuministros.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Textiles del Pacífico', 'China', '88 East Nanjing Rd, Shanghai', '+862140050080', 'export@pacifictextiles.cn', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('Logística Rápida Internacional', 'Panamá', 'Avenida Balboa, Torre Global, Piso 20, Ciudad de Panamá', '+5073004050', 'operaciones@logirapida.com.pa', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
('AgroExportadores SV', 'El Salvador', 'Km 68, Carretera a Santa Ana, Finca La Esperanza', '+50324445555', 'info@agroexportsv.com', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO provider_contact (provider_id, first_name, last_name, phone, email, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
(1, 'John', 'Smith', '+16505550102', 'j.smith@tecnoglobal.com', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 'Maria', 'Garcia', '+16505550103', 'm.garcia@tecnoglobal.com', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 'Carlos', 'Hernández', '+50377778888', 'carlos.h@ofisuministros.com.sv', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 'Li', 'Wei', '+862140050081', 'li.wei@pacifictextiles.cn', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, 'Isabella', 'Rojas', '+50760070080', 'isabella.rojas@logirapida.com.pa', TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO quotation (provider_id, date, code, is_approved, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
(1, '2025-08-01 10:00:00', 'COT-20250801-00001', TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, '2025-08-02 11:30:00', 'COT-20250802-00002', FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, '2025-08-05 09:15:00', 'COT-20250805-00003', TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, '2025-08-06 14:00:00', 'COT-20250806-00004', FALSE, FALSE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, '2025-08-08 16:45:00', 'COT-20250808-00005', TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, '2025-08-10 09:00:00', 'COT-20250810-00006', TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, '2025-08-11 14:20:00', 'COT-20250811-00007', FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, '2025-08-12 11:00:00', 'COT-20250812-00008', TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, '2025-08-12 15:00:00', 'COT-20250812-00009', FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, '2025-08-13 08:30:00', 'COT-20250813-00010', TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO quotation_detail (quotation_id, product_id, unit_id, required_quantity, price, approved_quantity, is_approved, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
(1, 1, 1, 10, 799.99, 10, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 2, 1, 5, 1299.00, 5, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 4, 1, 50, 12.50, 50, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 5, 1, 20, 89.95, 20, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 3, 1, 2, 450.00, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 1, 1, 15, 810.00, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 2, 1, 8, 1350.50, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 4, 4, 100, 11.99, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 5, 1, 30, 85.00, 25, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 4, 1, 200, 10.00, 200, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 1, 1, 5, 790.00, 5, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 3, 1, 4, 440.00, 0, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, 2, 1, 20, 1400.00, NULL, FALSE, FALSE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, 3, 1, 10, 480.75, NULL, FALSE, FALSE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, 5, 1, 50, 95.00, NULL, FALSE, FALSE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(4, 1, 1, 25, 850.00, NULL, FALSE, FALSE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, 1, 1, 2, 785.50, 2, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, 2, 1, 2, 1280.00, 2, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, 3, 1, 1, 430.00, 1, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, 4, 1, 10, 12.00, 10, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(6, 3, 1, 10, 435.00, 10, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(6, 4, 1, 150, 11.50, 150, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(7, 1, 1, 30, 820.00, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(7, 2, 1, 15, 1380.00, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(8, 1, 1, 20, 780.00, 20, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(8, 2, 1, 10, 1275.00, 10, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(8, 5, 1, 40, 88.00, 35, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(9, 3, 1, 5, 460.00, NULL, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(10, 4, 4, 50, 12.00, 50, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(10, 5, 1, 100, 89.00, 100, TRUE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO buy_order (provider_id, quotation_id, date, code, arrival_date, is_approved, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
(1, 1, '2025-08-10', 'BUY-20250810-00001', '2025-08-20 17:00:00', FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 3, '2025-08-10', 'BUY-20250810-00002', '2025-08-22 17:00:00', FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(5, 5, '2025-08-11', 'BUY-20250811-00003', '2025-08-25 17:00:00', FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);

INSERT INTO buy_order_detail (buy_order_id, product_id, unit_id, price, quantity, is_received, active, created_by_id, created_at, modified_by_id, updated_at) VALUES
(1, 1, 1, 799.99, 10, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 2, 1, 1299.00, 5, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 4, 1, 12.50, 50, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(1, 5, 1, 89.95, 20, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 5, 1, 85.00, 25, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 4, 1, 10.00, 200, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(2, 1, 1, 790.00, 5, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 1, 1, 785.50, 2, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 2, 1, 1280.00, 2, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 3, 1, 430.00, 1, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP),
(3, 4, 1, 12.00, 10, FALSE, TRUE, 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP);
