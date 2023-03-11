# Generated by Django 4.1.6 on 2023-03-10 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_alter_wallet_amount'),
        ('store', '0021_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='wallet_transaction',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.wallet', verbose_name=''),
        ),
    ]