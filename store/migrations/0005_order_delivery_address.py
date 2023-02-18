# Generated by Django 4.1.6 on 2023-02-18 05:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('store', '0004_cart_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='customer.address', verbose_name=''),
            preserve_default=False,
        ),
    ]
