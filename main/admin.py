from django.contrib import admin

from .models import *

"""
En el archivo admin.py, se configura lo que se ve y puede hacer en la vista admin
(http://<ip>/admin/)
Usuario: Anel
Password: KBfjZb36krNf3eX
"""


# Indica que se pueden editar los usuarios cliente
class ClienteInline(admin.TabularInline):
    model=Cliente


# Indica que se pueden editar los usuarios colaborador
class ColaboradorInline(admin.TabularInline):
    model=Colaborador


# Integra las dos clases anteriores a una vista profile admin
# En otras palabras, se pueden editar ambas clases en una sola vista
class ProfileAdmin(admin.ModelAdmin):
    inlines = [
        ClienteInline,
        ColaboradorInline
    ]


# Indica que se pueden editar las imagenes del producto
class ProductoImageInline(admin.TabularInline):
    model=ProductoImage


# Agrega la clase anterior a la vista producto admin
class ProductoAdmin(admin.ModelAdmin):
    inlines = [
        ProductoImageInline,
    ]

# Register your models here.
# Todos los modelos que se pueden editar
admin.site.register(Cliente)
admin.site.register(Colaborador)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Localizacion)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Comerciante)
admin.site.register(ProductoImage)
admin.site.register(Comment)
