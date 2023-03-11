# Generated by Django 4.1.6 on 2023-03-01 17:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_alter_user_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateTimeField(auto_now_add=True, verbose_name='')),
                ('transaction_type', models.CharField(choices=[('1', 'Cancellation'), ('2', 'Deposit'), ('3', 'Payment'), ('4', 'Others')], default='1', max_length=20)),
                ('amount', models.FloatField(verbose_name='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='')),
            ],
        ),
    ]