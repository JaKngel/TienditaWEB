# VAMOS A CREAR UN FORMULARIO QUE SE REUTILIZA EN EL AGREGAR Y ACTUALIZAR
from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm



class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(max_length=254, required=True, label='Correo electrónico')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput,
                                help_text='La contraseña debe contener al menos 8 caracteres.')
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        help_texts = {
            'username': 'El nombre de usuario debe contener entre 150 caracteres o menos y puede contener letras, dígitos y los siguientes caracteres especiales: @/./+/-/_',
        }


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('telefono', 'direccion', 'ciudad', 'comuna')
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'comuna': 'Comuna',
        }


class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['shipping_full_name', 'shipping_direccion', 'shipping_ciudad', 'shipping_comuna']
        labels = {
            'shipping_full_name': 'Nombre completo',
            'shipping_direccion': 'Dirección',
            'shipping_ciudad': 'Ciudad',
            'shipping_comuna': 'Comuna',
        }




class ProductoForm(ModelForm):

    nombre = forms.CharField(min_length=4,widget=forms.TextInput(attrs={"placeholder":"Ingrese Nombre"}))
    precio = forms.IntegerField(min_value=0,widget=forms.NumberInput(attrs={"placeholder":"Ingrese Precio"}))
    stock = forms.IntegerField(min_value=0,widget=forms.NumberInput(attrs={"placeholder":"Ingrese Stock"}))
    descripcion = forms.CharField(min_length=10,max_length=250,widget=forms.Textarea(attrs={"rows":4}))

    class Meta:
        model = Producto
        #fields = ['nombre','precio','stock','descripcion','tipo']
        fields = '__all__'


class CategoryForm(ModelForm):

    class Meta:
        model = CategoriaProducto
        #fields = ['nombre','precio','stock','descripcion','tipo']
        fields = '__all__'



class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion_entrega']
        widgets = {
            'direccion_entrega': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PedidoForm, self).__init__(*args, **kwargs)
        self.fields['direccion_entrega'].queryset = ShippingAddress.objects.filter(user=self.instance.usuario)
        self.fields['direccion_entrega'].label = 'Dirección de entrega'



from django import forms
from captcha.fields import CaptchaField

class ContactForm(forms.Form):
    Formulario_contacto = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField()


