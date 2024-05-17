#Nos va a permitir cenvertir la data
from .models import *
from rest_framework import serializers



class CategoriaProductoSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'

class ProductoSerializers(serializers.ModelSerializer):
    tipo = CategoriaProductoSerializers(read_only=True)
    class Meta:
        model = Producto
        fields = '__all__'

