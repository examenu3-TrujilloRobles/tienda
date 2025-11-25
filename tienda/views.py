from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
# Módulos de autenticación necesarios para la app
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
# Módulos necesarios para transacciones (CRÍTICO para registrar_venta)
from django.db import transaction 
from datetime import date, datetime, time  # Asegúrate de importarlo al inicio del archivo
from django.utils import timezone
from django.db.models import Sum, Count
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta
from .forms import DetalleVentaForm
from .forms import VentaForm
from django import forms

# Modelos y Forms
from .models import Producto, Categoria, Proveedor, Cliente, PerfilUsuario, Venta, DetalleVenta 
from .forms import (
    ProductoForm, 
    CategoriaForm, 
    ProveedorForm, 
    ClienteForm,
) 

# Módulos CRÍTICOS para el reporte de ventas y dashboard
from django.db.models import Sum, Count 
from django.utils import timezone 
from datetime import timedelta, datetime, time # <<< IMPORTACIONES AÑADIDAS

DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    can_delete=True
)

# IMPORTANTE: Se asume que el decorador rol_requerido existe en .decorators. Si no, se define aquí.
# Si el archivo .decorators.py existe, borra esta definición de aquí.
def rol_requerido(*roles_permitidos):
    """
    Decorador personalizado que verifica si el usuario tiene uno de los roles permitidos.
    También permite acceso a clientes autenticados si se incluye 'cliente' en los roles_permitidos.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder')
                return redirect('login')

            # Si es superusuario, acceso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Intentar obtener PerfilUsuario (empleado)
            try:
                perfil = request.user.perfil
                if perfil.rol in roles_permitidos:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, f'Acceso denegado. Requiere rol: {", ".join(roles_permitidos)}')
                    return redirect('dashboard')

            # Si NO tiene PerfilUsuario → puede ser un CLIENTE
            except PerfilUsuario.DoesNotExist:
                if hasattr(request.user, 'cliente') and 'cliente' in roles_permitidos:
                    return view_func(request, *args, **kwargs)
                messages.error(request, 'No tienes permisos para acceder.')
                return redirect('dashboard')

        return _wrapped_view
    return decorator


# ============ VISTAS BASADAS EN CLASES (CBVs) PARA AUTENTICACIÓN ============
class CustomLoginView(LoginView):
    """Vista de Login personalizada, basada en LoginView de Django."""
    template_name = 'tienda/login.html'
    next_page = reverse_lazy('dashboard') 
    
    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido {form.get_user().username}!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """Vista de Logout personalizada, basada en LogoutView de Django."""
    next_page = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Sesión cerrada correctamente')
        return super().dispatch(request, *args, **kwargs)


# ============ VISTA PRINCIPAL (DASHBOARD) ============
@login_required
def dashboard(request):
    """Vista principal que muestra el dashboard con estadísticas y cálculo de ventas."""
    
    # Cálculos base
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_clientes = Cliente.objects.count()
    
    # LÓGICA DE CÁLCULO DE VENTAS DE HOY USANDO RANGO
    now = timezone.localtime(timezone.now())
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    ventas_hoy_query = Venta.objects.filter(
        fecha_venta__gte=start_of_day,
        fecha_venta__lt=end_of_day
    ).aggregate(
        total_hoy=Sum('total')
    )['total_hoy']
    
    total_ventas_hoy = ventas_hoy_query or 0.00
    
    productos_recientes = Producto.objects.order_by('-id')[:5]
    
    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_proveedores': total_proveedores,
        'total_clientes': total_clientes,
        'productos_recientes': productos_recientes,
        'total_ventas_hoy': total_ventas_hoy, 
    }
    
    return render(request, 'tienda/dashboard.html', context)


# ============ VISTAS CRUD PARA PRODUCTOS ============
@login_required
def producto_lista(request):
    """Vista que lista todos los productos"""
    productos = Producto.objects.all()
    return render(request, 'tienda/producto_lista.html', {'productos': productos})


@login_required
@rol_requerido('gerente', 'administrador')
def producto_crear(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('producto_lista')
    else:
        form = ProductoForm()
    
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def producto_editar(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador') 
def producto_eliminar(request, pk):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete() 
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('producto_lista')
    
    return render(request, 'tienda/producto_eliminar.html', {'producto': producto})


# ============ VISTAS CRUD PARA CATEGORÍAS ============
@login_required
@rol_requerido('gerente', 'administrador', 'cliente','vendedor') 
def categoria_lista(request):
    """Vista que lista todas las categorías"""
    categorias = Categoria.objects.all()
    return render(request, 'tienda/categoria_lista.html', {'categorias': categorias})


@login_required
@rol_requerido('gerente', 'administrador') 
def categoria_crear(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    
    return render(request, 'tienda/categoria_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def categoria_editar(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'tienda/categoria_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador') 
def categoria_eliminar(request, pk):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente')
        return redirect('categoria_lista')
    
    return render(request, 'tienda/categoria_eliminar.html', {'categoria': categoria})


# ============ VISTAS CRUD PARA PROVEEDORES ============
@login_required
@rol_requerido('gerente', 'administrador','vendedor')
def proveedor_lista(request):
    """Vista que lista todos los proveedores"""
    proveedores = Proveedor.objects.all()
    return render(request, 'tienda/proveedor_lista.html', {'proveedores': proveedores})


@login_required
@rol_requerido('gerente', 'administrador')
def proveedor_crear(request):
    """Vista para crear un nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm()
    
    return render(request, 'tienda/proveedor_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def proveedor_editar(request, pk):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'tienda/proveedor_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')
def proveedor_eliminar(request, pk):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente')
        return redirect('proveedor_lista')
    
    return render(request, 'tienda/proveedor_eliminar.html', {'proveedor': proveedor})


# ============ VISTAS CRUD PARA CLIENTES ============
@login_required
@rol_requerido('gerente', 'administrador','vendedor')
def cliente_lista(request):
    """Vista que lista todos los clientes"""
    clientes = Cliente.objects.all()
    return render(request, 'tienda/cliente_lista.html', {'clientes': clientes})


@login_required
@rol_requerido('gerente', 'administrador')
def cliente_crear(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('cliente_lista')
    else:
        form = ClienteForm()
    
    return render(request, 'tienda/cliente_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def cliente_editar(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'tienda/cliente_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')
def cliente_eliminar(request, pk):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente')
        return redirect('cliente_lista')
    
    return render(request, 'tienda/cliente_eliminar.html', {'cliente': cliente})


# ============ VISTAS PARA VENTAS (REGISTRAR) ============
try:
    from .forms import VentaForm, DetalleVentaFormSet 
except ImportError:
    VentaForm = None
    DetalleVentaFormSet = None
    print("ADVERTENCIA: No se pudieron importar VentaForm o DetalleVentaFormSet. 'registrar_venta' fallará.")


@login_required
@rol_requerido('vendedor', 'gerente', 'administrador')
def registrar_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    venta = form.save(commit=False)
                    venta.empleado = request.user

                    # Calcular total de la venta y asignar precio_unitario
                    total_calculado = 0
                    detalles = formset.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        detalle.precio_unitario = detalle.producto.precio_venta  # <--- asignación automática
                        subtotal = detalle.precio_unitario * detalle.cantidad
                        total_calculado += subtotal
                    venta.total = total_calculado
                    venta.save()

                    # Guardar detalles y actualizar stock
                    for detalle in detalles:
                        detalle.save()
                        producto = detalle.producto
                        if producto.stock >= detalle.cantidad:
                            producto.stock -= detalle.cantidad
                            producto.save()
                        else:
                            raise Exception(f'Stock insuficiente para {producto.nombre}')

                messages.success(request, f"Venta #{venta.pk} registrada con éxito.")
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Error al registrar la venta: {e}")
        else:
            # Esto mostrará errores en consola y mensaje al usuario
            print("Errores de VentaForm:", form.errors)
            print("Errores de DetalleVentaFormSet:", formset.errors)
            messages.warning(request, "Revisa los errores del formulario o de los detalles.")
    else:
        form = VentaForm()
        formset = DetalleVentaFormSet()

    contexto = {
        'titulo': 'Registrar Nueva Venta',
        'form': form,
        'detalle_formset': formset,
    }
    return render(request, 'tienda/registrar_venta.html', contexto)





@login_required
@rol_requerido('gerente', 'administrador','vendedor') 
def reporte_ventas(request):
    """
    Muestra el reporte de ventas y permite filtrar por una fecha específica.
    Si no hay ventas, muestra la tabla vacía y totales en 0.
    """

    now = timezone.localtime(timezone.now())

    # Obtener la fecha seleccionada por GET, si no hay usar HOY
    fecha_str = request.GET.get('fecha_inicio')
    if fecha_str:
        try:
            filtro_fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            filtro_fecha = now.date()
    else:
        filtro_fecha = now.date()

    # Definir inicio y fin del día
    inicio_dia = timezone.make_aware(datetime.combine(filtro_fecha, time.min))
    fin_dia = timezone.make_aware(datetime.combine(filtro_fecha, time.max))

    # Filtrar ventas y detalles
    ventas_filtradas = Venta.objects.filter(fecha_venta__range=(inicio_dia, fin_dia))
    detalles_ventas_filtrados = DetalleVenta.objects.filter(
        venta__in=ventas_filtradas
    ).select_related('venta', 'producto', 'venta__vendido_por').order_by('-venta__fecha_venta')

    # Totales
    total_vendido = ventas_filtradas.aggregate(total=Sum('total'))['total'] or 0.00
    numero_ventas = ventas_filtradas.count()
    promedio_venta = total_vendido / numero_ventas if numero_ventas > 0 else 0.00

    contexto = {
        'titulo': 'Reporte de Ventas',
        'detalles_ventas': detalles_ventas_filtrados,
        'total_vendido': total_vendido,
        'numero_ventas': numero_ventas,
        'promedio_venta': promedio_venta,
        'fecha_inicio': filtro_fecha.strftime('%Y-%m-%d'),  # Para mostrar en el input
        'today_date': now.strftime('%Y-%m-%d'),            # Fecha por defecto
    }

    return render(request, 'tienda/reporte_ventas.html', contexto)

# =======================
# VISTAS PARA CLIENTES (ROL CLIENTE)
# =======================
@login_required
@rol_requerido('cliente')
def cliente_dashboard(request):
    """Dashboard exclusivo para clientes (solo ven sus propias compras)."""
    cliente = getattr(request.user, 'cliente', None)
    if not cliente:
        messages.error(request, "Tu cuenta no está asociada a un cliente.")
        return redirect('login')

    # Obtener las ventas del cliente autenticado
    ventas_cliente = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')

    context = {
        'titulo': 'Mi Panel de Cliente',
        'cliente': cliente,
        'ventas': ventas_cliente,
    }
    return render(request, 'tienda/cliente_dashboard.html', context)


@login_required
@rol_requerido('cliente')
def cliente_detalle_venta(request, pk):
    """Permite al cliente ver el detalle de una venta suya."""
    cliente = getattr(request.user, 'cliente', None)
    venta = get_object_or_404(Venta, pk=pk, cliente=cliente)
    detalles = venta.detalles.all()
    
    context = {
        'titulo': f'Detalle de Venta #{venta.pk}',
        'venta': venta,
        'detalles': detalles,
    }
    return render(request, 'tienda/cliente_detalle_venta.html', context)