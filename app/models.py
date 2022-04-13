from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from api.signals import *


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have a valid email address.")

        # if not kwargs.get("username"):
        #     raise ValueError("Users must have a valid username.")

        # account = self.model(
        #     email=self.normalize_email(email), username=kwargs.get("username")
        # )
        account = self.model(
            email=self.normalize_email(email)
        )

        account.set_password(password)
        account.save()
        print("js,fjklsdjfklsjdfklsdjfklsdfjsldfjsljfljskfjsjkfjlsjfjsdlfjksdjfl*********************************************************************")
        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_superuser = True
        account.is_staff = True
        account.save()

        return account

# Create your models here.

class UserAccount(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, blank=True, null=True)
    image = models.ImageField(default = "default.jpg", upload_to = "media")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = "email"
    objects = AccountManager()

class Customers(UserAccount):
    class Meta:
        db_table = 'Customer'

    def __str__(self):
        return self.email

class Sellers(UserAccount):
    class Meta:
        db_table = 'Seller'
    shop_name=models.CharField(max_length=100,blank=True, null=True)
    is_seller=models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Category(models.Model):
    category_name = models.CharField(unique=True,max_length=100,null=False,blank=False)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(unique=True,max_length=100)
    product_description = models.TextField(blank=True, null=True)
    product_price = models.FloatField()
    product_image = models.ImageField(upload_to="images/", blank=True, null=True)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    seller = models.ForeignKey(Sellers, on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.product_name



@receiver(post_save,sender=Customers)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        print("Customers*****************************************")
        Token.objects.create(user=instance)

@receiver(post_save,sender=Sellers)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        print("sellers*****************************************")
        Token.objects.create(user=instance)
