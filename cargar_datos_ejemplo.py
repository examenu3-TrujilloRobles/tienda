# cargar_datos_ejemplo.py
# ===================================================================
# Script para cargar datos de prueba en la aplicación 'tienda'
# Ejecutar con: python cargar_datos_ejemplo.py
# ===================================================================

import os
import django
from decimal import Decimal

# ====== CONFIGURAR DJANGO ======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_tienda.settings')
django.setup()

# ====== IMPORTACIONES ======
from tienda.models import Categoria, Proveedor, Cliente, Producto
from django.contrib.auth.models import User

print("\n--- 🚀 INICIALIZANDO CARGA DE DATOS DE EJEMPLO ---\n")

# ==========================
# 1️⃣ Crear Categorías
# ==========================
print("📦 Creando Categorías...")
categorias = [
    ("Electrónica", "Dispositivos y accesorios digitales."),
    ("Ropa", "Artículos de vestir para todas las edades."),
    ("Hogar", "Artículos para decoración y cocina."),
]

for nombre, descripcion in categorias:
    cat, creado = Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": descripcion})
    if creado:
        print(f"✅ Categoría creada: {nombre}")
    else:
        print(f"ℹ️ Categoría existente: {nombre}")

# ==========================
# 2️⃣ Crear Proveedores
# ==========================
print("\n🏢 Creando Proveedores...")
proveedores = [
    {
        "nombre": "Juan Pérez",
        "empresa": "TechSupply Corp",
        "telefono": "662-123-4567",
        "email": "contacto@techsupply.com",
        "direccion": "Calle A #123, Hermosillo",
    },
    {
        "nombre": "Laura Gómez",
        "empresa": "Moda Express S.A.",
        "telefono": "662-987-6543",
        "email": "laura@modaxpress.com",
        "direccion": "Av. B #456, Guaymas",
    },
]

for data in proveedores:
    prov, creado = Proveedor.objects.get_or_create(nombre=data["nombre"], defaults=data)
    if creado:
        print(f"✅ Proveedor creado: {data['nombre']}")
    else:
        print(f"ℹ️ Proveedor existente: {data['nombre']}")

# ==========================
# 3️⃣ Crear Clientes
# ==========================
print("\n👤 Creando Clientes...")
clientes = [
    {
        "nombre": "Carlos",
        "apellido": "López",
        "email": "carlos.cliente@uth.edu.mx",
        "telefono": "662-555-1111",
        "direccion": "Residencial C, #789",
    },
    {
        "nombre": "María",
        "apellido": "García",
        "email": "maria.test@uth.edu.mx",
        "telefono": "662-555-2222",
        "direccion": "Colonia D, #101",
    },
]

for data in clientes:
    cli, creado = Cliente.objects.get_or_create(email=data["email"], defaults=data)
    if creado:
        print(f"✅ Cliente creado: {data['nombre']} {data['apellido']}")
    else:
        print(f"ℹ️ Cliente existente: {data['nombre']} {data['apellido']}")

# ==========================
# 4️⃣ Obtener usuario administrador (si existe)
# ==========================
try:
    creador = User.objects.get(username="admin1")
except User.DoesNotExist:
    try:
        creador = User.objects.get(username="admin")
    except User.DoesNotExist:
        creador = None

# ==========================
# 5️⃣ Crear Productos
# ==========================
print("\n🛒 Creando Productos...")
productos_data = [
    # Electrónica
    {
        "nombre": "Laptop UTH Pro",
        "descripcion": "Laptop de alto rendimiento para ingenieros.",
        "precio_venta": Decimal("15000.00"),
        "stock": 15,
        "categoria": Categoria.objects.get(nombre="Electrónica"),
        "proveedor": Proveedor.objects.get(nombre="Juan Pérez"),
    },
    {
        "nombre": "Mouse Óptico Inalámbrico",
        "descripcion": "Mouse ergonómico y preciso.",
        "precio_venta": Decimal("350.50"),
        "stock": 50,
        "categoria": Categoria.objects.get(nombre="Electrónica"),
        "proveedor": Proveedor.objects.get(nombre="Juan Pérez"),
    },
    # Ropa
    {
        "nombre": "Camisa Algodón UTH",
        "descripcion": "Camisa 100% algodón con logo de la universidad.",
        "precio_venta": Decimal("499.99"),
        "stock": 30,
        "categoria": Categoria.objects.get(nombre="Ropa"),
        "proveedor": Proveedor.objects.get(nombre="Laura Gómez"),
    },
    {
        "nombre": "Pantalón Jeans Casual",
        "descripcion": "Jeans de mezclilla corte recto.",
        "precio_venta": Decimal("850.00"),
        "stock": 20,
        "categoria": Categoria.objects.get(nombre="Ropa"),
        "proveedor": Proveedor.objects.get(nombre="Laura Gómez"),
    },
    # Hogar
    {
        "nombre": "Set de Cuchillos Cocina",
        "descripcion": "Set de 5 cuchillos de acero inoxidable.",
        "precio_venta": Decimal("1200.75"),
        "stock": 10,
        "categoria": Categoria.objects.get(nombre="Hogar"),
        "proveedor": Proveedor.objects.get(nombre="Juan Pérez"),
    },
]

for data in productos_data:
    prod, creado = Producto.objects.get_or_create(nombre=data["nombre"], defaults=data)
    if creado:
        print(f"✅ Producto creado: {data['nombre']}")
    else:
        print(f"ℹ️ Producto existente: {data['nombre']}")

print("\n🎉 --- CARGA DE DATOS DE EJEMPLO FINALIZADA CON ÉXITO ---\n")
