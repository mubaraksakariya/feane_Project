# Generated by Django 4.1.6 on 2023-02-17 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.ManyToManyField(related_name='cart', to='store.cart', verbose_name=''),
        ),
    ]
