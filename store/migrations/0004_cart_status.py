# Generated by Django 4.1.6 on 2023-02-18 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_order_order_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(max_length=50, null=True, verbose_name=''),
        ),
    ]
