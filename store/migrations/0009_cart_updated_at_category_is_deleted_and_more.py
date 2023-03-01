# Generated by Django 4.1.6 on 2023-02-28 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_product_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='category',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name=''),
        ),
        migrations.AddField(
            model_name='category',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='size',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name=''),
        ),
        migrations.AddField(
            model_name='size',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]