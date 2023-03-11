# Generated by Django 4.1.6 on 2023-03-02 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='')),
                ('discount', models.IntegerField(verbose_name='')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.coupon', verbose_name=''),
        ),
    ]