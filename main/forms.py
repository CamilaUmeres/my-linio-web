from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import Http404

from .models import *

"""
Formulario para crear un usuario
Contiene los campos requeridos y opcionales (required=False) para crear un usuario
"""
class UserForm(UserCreationForm):
    # django.contrib.auth.User attributes
    # Primer nombre: Variable string. Validacion 150 caracteres maximo
    first_name = forms.CharField(max_length=150, required=False)
    # Apellido: Variable string. Validacion 150 caracteres maximo
    last_name = forms.CharField(max_length=150, required=False)
    # Email: Variable objeto Email. Validacion 150 caracteres maximo, required=True por default
    email = forms.EmailField(max_length=150)

    # Profile attributes
    # DNI: Variable tipo string. Validacion 8 caracteres maximo, required=True por default
    documento_identidad = forms.CharField(max_length=8)
    # Fecha de nacimiento: Variable tipo date. required=True por default
    fecha_nacimiento = forms.DateField()
    # Estado: Variable tipo string. Validacion 3 caracteres maximo, required=True por default
    estado = forms.CharField(max_length=3)
    ## Opciones de genero
    MASCULINO = 'MA'
    FEMENINO = 'FE'
    NO_BINARIO = 'NB'
    GENERO_CHOICES = [
        (MASCULINO, 'Masculino'),
        (FEMENINO, 'Femenino'),
        (NO_BINARIO, 'No Binario')
    ]
    # Genero: Variable tipo seleccion multiple (combobox), required=True por default
    genero = forms.ChoiceField(choices=GENERO_CHOICES)

    # Colaborador attributes
    # Es colaborador? Variable tipo boolean (checkbox)
    is_colaborador = forms.BooleanField(required=False)
    # Reputacion: Variable tipo float
    reputacion = forms.FloatField(required=False)
    # Cobertura entrega: Variable seleccion multiple, cuya data proviene de la base de datos
    cobertura_entrega = forms.ModelChoiceField(queryset=Localizacion.objects.all(), required=False)

    # Cliente attributes
    # Es cliente? Variable tipo boolean (checkbox)
    is_cliente = forms.BooleanField(required=False)
    # Preferencias: Variable seleccion multiple, cuya data proviene de la base de datos
    preferencias = forms.ModelChoiceField(queryset=Categoria.objects.all(), required=False)

    # Comerciatne attributes
    # Es comerciante? Variable tipo boolean (checkbox)
    is_comerciante = forms.BooleanField(required=False)

    # Modelo User y sus campos
    class Meta:
        model = User
        fields = ['username',
        'first_name',
        'last_name',
        'email',
        'documento_identidad',
        'fecha_nacimiento',
        'estado',
        'genero',
        'is_cliente',
        'preferencias',
        'is_colaborador',
        'reputacion',
        'cobertura_entrega',
        'is_comerciante'
        ]



"""
Formulario para crear un comercio
Contiene los campos requeridos y opcionales (required=False) para crear un comercio
"""
class CommerceForm(forms.Form):
    # Ruc: Variable string. Validacion 11 caracteres maximo
    ruc = forms.CharField(max_length=11)
    # Razon social: Variable string. Validacion 20 caracteres maximo
    razon_social = forms.CharField(max_length=20)
    # Telefono: Variable string. Validacion 9 caracteres maximo
    telefono = forms.CharField(max_length=9)

    # Modelo Comercio y sus campos
    class Meta:
        model = Proveedor
        fields = ['ruc',
        'razon_social',
        'telefono'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CommerceForm, self).__init__(*args, **kwargs)




"""
Formulario para crear un producto
Contiene los campos requeridos y opcionales (required=False) para crear un producto
"""
class ProductForm(forms.Form):
    # Categoria: Variable seleccion multiple.
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), required=False)
    # Nombre: Variable string. Validacion 20 caracteres maximo
    nombre = forms.CharField(max_length=20)
    # Descripcion: Variable texto.
    descripcion = forms.CharField()
    # Precio: Campo float con valor precio
    precio = forms.FloatField()
    # Estado: Campo string con longitud maxima 3
    estado = forms.CharField(max_length=3)
    # Descuento: Campo tipo float
    descuento = forms.FloatField(required=False)
    # Imagen
    imagen = forms.ImageField()


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ProductForm, self).__init__(*args, **kwargs)


# Clase para guardar comentarios (comunicacion entre proveedor y cliente)
class CommentForm(forms.Form):
    # Body: Texto del cuerpo.
    body = forms.CharField(widget=forms.Textarea)

    # Modelo Comment y sus campos
    class Meta:
        model = Comment
        fields = ['body',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.pedido_pk = kwargs.pop('pedido_pk')
        super(CommentForm, self).__init__(*args, **kwargs)
