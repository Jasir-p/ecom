# Generated by Django 5.0.3 on 2024-04-29 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Order", "0004_order_trackig_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="status",
            field=models.CharField(default="pending", max_length=20, null=True),
        ),
    ]
