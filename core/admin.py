from django.contrib import admin
from .models import *

# DEJA EN MODO TABLA LA VISUALIZACION EN EL ADMIN
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre','precio','stock','descripcion','categoria']
    search_fields = ['nombre']

class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['id','producto','cantidad']

admin.site.register(CategoriaProducto)
admin.site.register(Producto)

admin.site.register(Carrito)
admin.site.register(DetallePedido)
admin.site.register(Pedido)
