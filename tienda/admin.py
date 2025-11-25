from django.contrib import admin
# Importamos TODOS nuestros modelos, incluyendo Venta y DetalleVenta
from .models import Categoria, Producto, Proveedor, Cliente, PerfilUsuario, Venta, DetalleVenta 
# ↑↑↑ IMPORTACIÓN CORREGIDA/AMPLIADA ↑↑↑


# ============ CONFIGURACIÓN DEL ADMIN PARA PERFILES DE USUARIO ============
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # ... (código existente para PerfilUsuarioAdmin)
    list_display = ('user', 'rol', 'departamento', 'activo', 'fecha_contratacion') 
    list_filter = ('rol', 'activo', 'departamento') 
    search_fields = ('user__username', 'user__email', 'departamento') 
    list_editable = ('rol', 'activo') 
    ordering = ('-fecha_contratacion',) 


# ============ CONFIGURACIÓN DEL ADMIN PARA CATEGORÍAS ============
@admin.register(Categoria) 
class CategoriaAdmin(admin.ModelAdmin):
    # ... (código existente para CategoriaAdmin)
    list_display = ('id', 'nombre', 'fecha_creacion') 
    search_fields = ('nombre',) 
    list_filter = ('fecha_creacion',) 
    ordering = ('nombre',) 


# ============ CONFIGURACIÓN DEL ADMIN PARA PRODUCTOS ============
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # ... (código existente para ProductoAdmin)
    list_display = ('id', 'nombre', 'categoria', 'precio_venta', 'stock', 'activo', 'fecha_creacion') 
    search_fields = ('nombre', 'descripcion') 
    list_filter = ('categoria', 'activo', 'fecha_creacion') 
    list_editable = ('precio_venta', 'stock', 'activo') # Usar precio_venta
    ordering = ('-fecha_creacion',) 


# ============ CONFIGURACIÓN DEL ADMIN PARA PROVEEDORES ============
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    # ... (código existente para ProveedorAdmin)
    list_display = ('id', 'nombre', 'empresa', 'telefono', 'email', 'fecha_registro')
    search_fields = ('nombre', 'empresa', 'email') 
    list_filter = ('fecha_registro',)
    ordering = ('empresa',)


# ============ CONFIGURACIÓN DEL ADMIN PARA CLIENTES ============
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # ... (código existente para ClienteAdmin)
    list_display = ('id', 'nombre', 'apellido', 'email', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'email') 
    list_filter = ('fecha_registro',)
    ordering = ('apellido', 'nombre') 


# ============ CONFIGURACIÓN DEL ADMIN PARA VENTAS ============
class DetalleVentaInline(admin.TabularInline):
    """Permite editar los detalles de venta dentro del formulario de Venta."""
    model = DetalleVenta
    extra = 0 # No muestra filas vacías por defecto

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'total', 'cliente', 'vendido_por')
    list_filter = ('fecha_venta',)
    search_fields = ('cliente__nombre', 'cliente__apellido')
    readonly_fields = ('total',) # El total se calcula automáticamente
    inlines = [DetalleVentaInline] # Muestra los detalles de venta

# Si Venta y DetalleVenta no se registran en los decoradores, puedes usar esta alternativa:
# admin.site.register(DetalleVenta) 
# admin.site.register(Venta, VentaAdmin)