# Generated by Django 5.0.3 on 2024-06-02 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Userapp", "0003_customuser_referal_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wallet",
            name="referral_deposit",
        ),
        migrations.AddField(
            model_name="wallet_transaction",
            name="referral_deposit",
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]
