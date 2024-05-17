from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

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
    direccion_entrega = models.CharField(max_length=250, default='')  # Valor por defecto: cadena vacía
    metodo_pago = models.CharField(max_length=50, default='')  # Valor por defecto: cadena vacía


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
