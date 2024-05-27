from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save


# Create Customer Profile
class Ciudad(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    nombre = models.CharField(max_length=200)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='comunas')

    def __str__(self):
        return f'{self.nombre}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_direccion = models.CharField(max_length=255)
    shipping_ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Shipping Address - {self.user.username}'

def create_shipping(sender, instance, created, **kwargs):
    if created:
        ShippingAddress.objects.create(user=instance)

post_save.connect(create_shipping, sender=User)

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    descripcion = models.CharField(max_length=250)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    imagen = CloudinaryField('imagen')

    def __str__(self):
        return self.nombre

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.producto.nombre} - Cantidad: {self.cantidad}'

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='DetallePedido')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='pendiente')
    direccion_entrega = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)

    def calcular_total_pedido(self):
        detalle_pedidos = self.detallepedido_set.all()
        total = sum(detalle.cantidad * detalle.producto.precio for detalle in detalle_pedidos)
        return total

    def __str__(self):
        return f'Pedido {self.id} - Usuario: {self.usuario.username} - Estado: {self.estado}'

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Detalle de Pedido {self.pedido.id} - Producto: {self.producto.nombre} - Cantidad: {self.cantidad}'
