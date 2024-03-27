# Generated by Django 4.2.6 on 2024-03-26 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0002_size_variant_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='color_products',
            name='img1',
        ),
        migrations.RemoveField(
            model_name='color_products',
            name='img2',
        ),
        migrations.RemoveField(
            model_name='color_products',
            name='img3',
        ),
        migrations.AddField(
            model_name='product',
            name='img1',
            field=models.ImageField(null=True, upload_to='products/'),
        ),
        migrations.AddField(
            model_name='product',
            name='img2',
            field=models.ImageField(null=True, upload_to='products/'),
        ),
        migrations.AddField(
            model_name='product',
            name='img3',
            field=models.ImageField(null=True, upload_to='products/'),
        ),
    ]
