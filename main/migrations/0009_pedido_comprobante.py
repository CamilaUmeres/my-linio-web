# Generated by Django 3.0.6 on 2020-11-28 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20201128_0233'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='comprobante',
            field=models.CharField(choices=[('Recibo', 'Recibo'), ('Boleta', 'Boleta')], max_length=6, null=True),
        ),
    ]
