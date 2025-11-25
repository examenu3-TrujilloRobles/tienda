from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    # ==============================
    # PÁGINAS PRINCIPALES
    # ==============================
    path('', views.dashboard, name='home'),                 # Página raíz (inicio)
    path('home/', views.dashboard, name='home_redirect'),   # Permite acceder también con /home/
    path('dashboard/', views.dashboard, name='dashboard'),  # Página principal del panel

    # ==============================
    # AUTENTICACIÓN
    # ==============================
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # ==============================
    # CRUD PRODUCTOS
    # ==============================
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/crear/', views.producto_crear, name='producto_crear'),
    path('productos/editar/<int:pk>/', views.producto_editar, name='producto_editar'),
    path('productos/eliminar/<int:pk>/', views.producto_eliminar, name='producto_eliminar'),

    # ==============================
    # CRUD CATEGORÍAS
    # ==============================
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    path('categorias/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),
    path('categorias/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),

    # ==============================
    # CRUD PROVEEDORES
    # ==============================
    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/editar/<int:pk>/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/eliminar/<int:pk>/', views.proveedor_eliminar, name='proveedor_eliminar'),

    # ==============================
    # CRUD CLIENTES
    # ==============================
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/crear/', views.cliente_crear, name='cliente_crear'),
    path('clientes/editar/<int:pk>/', views.cliente_editar, name='cliente_editar'),
    path('clientes/eliminar/<int:pk>/', views.cliente_eliminar, name='cliente_eliminar'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    path('cliente/venta/<int:pk>/', views.cliente_detalle_venta, name='cliente_detalle_venta'),

    # ==============================
    # REPORTES
    # ==============================
    path('registrar-venta/', views.registrar_venta, name='registrar_venta'),
    path('reporte-ventas/', views.reporte_ventas, name='reporte_ventas'),
]
