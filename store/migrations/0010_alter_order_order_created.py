# Generated by Django 4.1.6 on 2023-02-28 20:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_cart_updated_at_category_is_deleted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 28, 20, 13, 11, 386986, tzinfo=datetime.timezone.utc), verbose_name=''),
        ),
    ]
