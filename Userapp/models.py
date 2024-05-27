from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save,post_delete
from Order.models import OrderProduct


from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=25, unique=True)


class Wallet(models.Model):
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(blank=True, default=0)
    referral_deposit = models.PositiveIntegerField(blank=True, default=0)

    def __str__(self):
        name = f"{self.user.username}  "
        email = self.user.email
        balance = self.balance
        return f"{name} {email} | Balance : {balance}"


        
@receiver(post_save, sender=CustomUser)
def Create_User_Wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        print("wallet created successfully!!")


class Wallet_transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderProduct, on_delete=models.CASCADE, null=True, blank=True)
    transaction_id = models.CharField(
        max_length=50,
        unique=True,
    )
    money_deposit = models.PositiveBigIntegerField(blank=True, default=0)
    money_withdrawn = models.PositiveBigIntegerField(blank=True, default=0)
    transaction_time = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     if self.money_deposit:
    #         money = "+{}".format(self.money_deposit)
    #     elif self.money_withdrawn:
    #         money = "-{}".format(self.money_withdrawn)
    #     id = self.transaction_id
    #     item = self.order_item
    #     name = f"{self.wallet.user.username} "
    #     time = self.transaction_time
    #     return f"{id} | {item} - {name} : {time} | {money}"
