# Generated by Django 2.2.3 on 2019-10-09 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20191002_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=100),
        ),
    ]