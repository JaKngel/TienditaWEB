from django.contrib import admin
from .models import *

# DEJA EN MODO TABLA LA VISUALIZACION EN EL ADMIN
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'descripcion', 'categoria']
    search_fields = ['nombre']

class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'cantidad', 'fecha_agregado']
    search_fields = ['usuario__username', 'producto__nombre']

class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad']
    search_fields = ['pedido__id', 'producto__nombre']

class PedidoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_pedido', 'estado', 'direccion_entrega']
    search_fields = ['usuario__username', 'estado', 'direccion_entrega']

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'shipping_full_name', 'shipping_direccion', 'shipping_ciudad', 'shipping_comuna']
    search_fields = ['user__username', 'shipping_full_name', 'shipping_direccion']

class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

class ComunaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad']
    search_fields = ['nombre', 'ciudad__nombre']

class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Registro de todos los modelos
admin.site.register(Ciudad, CiudadAdmin)
admin.site.register(Comuna, ComunaAdmin)
admin.site.register(Profile)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(DetallePedido, DetallePedidoAdmin)
admin.site.register(Pedido, PedidoAdmin)
