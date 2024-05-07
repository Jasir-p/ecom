# Generated by Django 4.2.6 on 2024-03-25 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("B_name", models.CharField(max_length=60)),
                ("cover_image", models.ImageField(upload_to="brand/")),
                ("B_description", models.CharField(max_length=260)),
            ],
        ),
        migrations.CreateModel(
            name="Catagory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cat_name", models.CharField(max_length=60)),
                ("cover_image", models.ImageField(upload_to="catagory/")),
                ("cat_description", models.CharField(max_length=260)),
            ],
        ),
    ]
