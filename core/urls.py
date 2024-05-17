from django.urls import path, include
from .views import *
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('productos', ProductoViewset)
router.register('CategoriaProducto', CategoriaProductoViewset)

urlpatterns = [
    #API
    path('api/', include(router.urls)),

    path('' , index , name='index'),
    path('shop/', shop, name="shop"),
    path('testimonial/', testimonial, name="testimonial"),
    path('why/', why, name="why"),
    path('account/', account, name="account"),

    #REGISTRO
    path('registro/', registro, name="registro"),
    #LOGOUT
    path('accounts/logout/', views.logout_view, name='logout'),

    #CRUD
    path('add/', add, name="add"),
    path('update/<id>/', update, name="update"),
    path('delete/<id>/', delete, name="delete"),

    #FILTRO
    path('filter/', views.filter_products, name='filter'),

    #CART
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:carrito_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('ver/', ver_carrito, name='ver_carrito'),
    path('realizar_pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('detalle_pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('actualizar_carrito/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('comprar/', comprar, name='comprar'),
    path('recibir_confirmacion/', views.recibir_confirmacion, name='recibir_confirmacion'),

    #CORREO
    path('enviar_correo/', views.enviar_correo, name='enviar_correo'),

]