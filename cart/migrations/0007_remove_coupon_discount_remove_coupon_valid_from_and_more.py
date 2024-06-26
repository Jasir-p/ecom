# Generated by Django 5.0.3 on 2024-05-12 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0006_coupon_created"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coupon",
            name="discount",
        ),
        migrations.RemoveField(
            model_name="coupon",
            name="valid_from",
        ),
        migrations.RemoveField(
            model_name="coupon",
            name="valid_to",
        ),
        migrations.AddField(
            model_name="coupon",
            name="discount_amount",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="coupon",
            name="end_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="coupon",
            name="min_amount",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="coupon",
            name="quantity",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="coupon",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="coupon",
            name="title",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="code",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
