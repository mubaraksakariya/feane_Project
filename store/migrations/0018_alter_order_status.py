# Generated by Django 4.1.6 on 2023-03-01 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('1', 'Waiting to accept order'), ('2', 'Your order is being Prepared'), ('3', 'Ready to Ship'), ('4', 'Out for delivery'), ('0', 'Cancelled')], default='1', max_length=20),
        ),
    ]
