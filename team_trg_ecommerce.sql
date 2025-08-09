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

