from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import datetime

"""
Los modelos de la aplicacion
"""

# Create your models here.
# Modelo Perfil
class Profile(models.Model):
    ####
    # Relacion con el modelo User de Django (uno a uno)
    # ondelete=CASCADE indica que al eliminar un usuario, se elimina
    # cualquier dato relacionado con este
    ####
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Atributos adicionales para el usuario
    # DNI: Campo string, con longitud maxima 8
    documento_identidad = models.CharField(max_length=8)
    # Fecha de nacimiento: Campo fecha
    fecha_nacimiento = models.DateField()
    # Estado: Campo string, con longitud maxima 3
    estado = models.CharField(max_length=3)

    ## Opciones de genero
    MASCULINO = 'MA'
    FEMENINO = 'FE'
    NO_BINARIO = 'NB'
    GENERO_CHOICES = [
        (MASCULINO, 'Masculino'),
        (FEMENINO, 'Femenino'),
        (NO_BINARIO, 'No Binario')
    ]
    # Genero: Campo string, con longitud maxima 2 y cuyo valor debe estar en la lista GENERO_CHOICES
    genero = models.CharField(max_length=2, choices=GENERO_CHOICES)

    # Al hacer print, se muestra el campo usuario
    def __str__(self):
        return self.user.get_username()


    # Metodo de validacion
    def validate_data(self):
        now = datetime.datetime.now()
        # Restamos la fecha actual con la de nacimiento para obtener la edad
        edad = int((now.date()-self.fecha_nacimiento).days/365.25) - ((now.month, now.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        if edad < 18:
            raise ValidationError(
                _('Invalid value: %(value)s. Must be over 18'),
                params={'value': str(edad)},
            )

        if(len(self.documento_identidad)!=8):
            raise ValidationError(
                _('Invalid value: %(value)s. DNI must be 8 characters'),
                params={'value': str(len(self.documento_identidad))},
            )


# Modelo Comerciante
class Comerciante(models.Model):
    # Relacion con el modelo Perfil
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comerciante: {self.user_profile.user.get_username()}'

    # Registrar comercio
    def register_commerce(self, ruc, razon_social, telefono):
        nuevo_proveedor = Proveedor.objects.create(ruc=ruc,razon_social=razon_social, telefono=telefono, comerciante=self)
        nuevo_proveedor.save()



# Modelo Colaborador
class Colaborador(models.Model):
    # Relacion con el modelo Perfil
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    # Atributos especificos del Colaborador
    # Reputacion: Campo tipo flotante
    reputacion = models.FloatField()
    #####
    # Relacion con el modelo Localizacion (many to many)
    # Un colaborador puede estar asignado a varias localizaciones
    # y una localizacion puede estar asingada a varios colaboradores
    #####
    cobertura_entrega = models.ManyToManyField(to='Localizacion')

    def __str__(self):
        return f'Colaborador: {self.user_profile.user.get_username()}'


# Modelo Localizacion
class Localizacion(models.Model):
    # Distrito: Campo string, longitud maxima de 20 caracters
    distrito = models.CharField(max_length=20)
    # Provincia: Campo string, longitud maxima de 20 caracters
    provincia = models.CharField(max_length=20)
    # Departamento: Campo string, longitud maxima de 20 caracters
    departamento = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.distrito}, {self.provincia}, {self.departamento}'


# Modelo Cliente
class Cliente(models.Model):
    # Relacion con el modelo Perfil
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    # Atributos especificos del Cliente
    preferencias = models.ManyToManyField(to='Categoria')

    def __str__(self):
        return f'Cliente: {self.user_profile.user.get_username()}'


# Modelo Categoria
class Categoria(models.Model):
    # Codigo: Campo string con longitud maxima 4
    codigo = models.CharField(max_length=4)
    # Nombre: Campo string con longitud maxima 20
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.codigo}: {self.nombre}'


# Modelo Producto
class Producto(models.Model):
    ####
    # Relaciones (many to one)
    # Una categoria (o un proveedor) puede tener varios productos asignados
    # Al borrar, los modelos que dependen de este, ponen sus campos como null
    ####
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True)

    # Atributos
    # Nombre: Campo string con longitud maxima 20
    nombre = models.CharField(max_length=20)
    # Descripcion: Campo tipo texto
    descripcion = models.TextField()
    # Precio: Campo tipo float
    precio = models.FloatField()
    # Estado: Campo string con longitud maxima 3
    estado = models.CharField(max_length=3)
    # Descuento: Campo tipo float con valor default 0
    descuento = models.FloatField(default=0)

    def __str__(self):
        return self.nombre

    # Retorna precio final con descuento
    def get_precio_final(self):
        return self.precio * (1 - self.descuento)

    # Retorna codigo de producto
    def sku(self):
        codigo_categoria = self.categoria.codigo.zfill(4)
        codigo_producto = str(self.id).zfill(6)

        return f'{codigo_categoria}-{codigo_producto}'

    # Metodo de validacion
    def validate_data(self):
        if self.precio<0:
            raise ValidationError(
                _('Invalid value: %(value)s. Price must be over 0'),
                params={'value': str(self.precio)},
            )

        if(self.descuento<0 or self.descuento>1):
            raise ValidationError(
                _('Invalid value: %(value)s. Discount must be over 0 and less than 1'),
                params={'value': str(self.descuento)},
            )


# Modelo ProductoImage
class ProductoImage(models.Model):
    # Relacion con la tabla producto
    product = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='images')
    # Image: Campo tipo imagen
    image = models.ImageField(upload_to="products", null=True, blank=True)


# Modelo Proveedor
class Proveedor(models.Model):
    # Comerciante
    comerciante = models.OneToOneField(Comerciante, on_delete=models.CASCADE, null=True)
    # Ruc: Campo string con longitud maxima 11
    ruc = models.CharField(max_length=11)
    # Razon social: Campo string con longitud maxima 20
    razon_social = models.CharField(max_length=20)
    #Telefono: Campo string con longitud maxima 9
    telefono = models.CharField(max_length=9)

    def __str__(self):
        return self.razon_social


    # Metodo de validacion
    def validate_data(self):
        if(len(self.telefono)!=9):
            raise ValidationError(
                _('Invalid value: %(value)s. Phone must be 9 characters'),
                params={'value': str(len(self.telefono))},
            )

        if(len(self.ruc)!=11):
            raise ValidationError(
                _('Invalid value: %(value)s. RUC must be 11 characters'),
                params={'value': str(len(self.ruc))},
            )


    def register_product(self,categoria,nombre,descripcion,precio,estado,descuento):
        producto = Producto.objects.create(categoria=categoria, nombre=nombre, descripcion=descripcion, precio=precio, estado=estado, descuento=descuento, proveedor=self)
        try:
            producto.validate_data()
        except Exception as e:
            producto.delete()
            print("error1")
            print(e)
            raise e

        return producto

    """
    def update_product(self):
        productos = self.producto_set.all()
    """


# Modelo Pedido
class Pedido(models.Model):
    # Relaciones (many to one)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    repartidor = models.ForeignKey('Colaborador', on_delete=models.SET_NULL, null=True)
    ubicacion = models.ForeignKey('Localizacion', on_delete=models.SET_NULL, null=True)

    # Atributos
    # Fecha creacion: Campo tipo fecha_hora, automaticamente guarda la fecha en que se registra
    fecha_creacion = models.DateTimeField(auto_now=True)
    # Fecha entrega: Campo tipo fecha hora
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    # Estado: Campo string con longitud maxima 3
    estado = models.CharField(max_length=3)
    # Direccion entrega: Campo string con longitud maxima 100
    direccion_entrega = models.CharField(max_length=100, blank=True, null=True)
    # Tarifa: Campo float
    tarifa = models.FloatField(blank=True, null=True)
    # Comprobante: Campo opcion multiple
    FACTURA = 'Factura'
    BOLETA = 'Boleta'
    TIPO_COMPROBANTE = [(FACTURA, 'Factura'),(BOLETA, 'Boleta')]
    comprobante = models.CharField(max_length=7, choices=TIPO_COMPROBANTE, null=True)


    def __str__(self):
        return f'{self.cliente} - {self.fecha_creacion} - {self.estado}'

    # Retorna el total de costo del pedido
    def get_total(self):
        # Obtiene el detalle dle pedido
        detalles = self.detallepedido_set.all()
        total = 0
        # Para cada elemento, suma el subtotal
        for detalle in detalles:
            total += detalle.get_subtotal()
        total += self.tarifa
        return total

    # Retorna true si se puede cancelar pedido o false, de lo contrario
    def puede_cancelar(self):
        # El pedido se puede cancelar si no hay colaborador asignado
        if self.repartidor is None:
            return True

        # El pedido se puede cancelar antes de las 12 horas
        now = datetime.datetime.now(self.fecha_creacion.tzinfo)
        # Restamos la fecha actual con la de creacion para obtener las horas pasadas
        edad = int((now-self.fecha_creacion).days)*24

        if edad > 12:
            return False
        return True


    # Cancela el pedido
    def cancelar_pedido(self):
        return self.delete()


# Clase DetallePedido
class DetallePedido(models.Model):
    # Relaciones (many to one)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)

    # Atributos
    # Cantidad: Campo tipo entero
    cantidad = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.pedido.id} - {self.cantidad} x {self.producto.nombre}'

    # Retorna el subtotal del pedido
    def get_subtotal(self):
        return self.producto.get_precio_final() * self.cantidad


# Comentarios en el pedido
class Comment(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Comentario {} escrito por {}'.format(self.body, self.usuario)
