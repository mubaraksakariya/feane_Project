from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.utils.translation import gettext_lazy as _
from store.models import Cart
from feaneAdmin.models import Notification

# Custom USER models here. email and password for authentication
###########################################
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=13)
    phone_number_verified = models.BooleanField(_(""),default=False)
    otp = models.IntegerField(default=0000,null=True)
    email = models.EmailField(_('email address'),unique=True)
    blocked = models.BooleanField(_(""),default=False)
    updated_at = models.DateField(_(""), auto_now=True, auto_now_add=False)
    is_deleted = models.BooleanField(_(""),default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    @property
    def wallet_balance(self):
        wallet = Wallet.objects.filter(user = self)
        if wallet is not None:
            balance = sum([item.amount for item in wallet])
            return balance
        else:
            return 0
    
    @property
    def cart_count(self):
        cart_count = Cart.objects.filter(user = self,purchased = False).count()
        return cart_count

    @property
    def messages(self):
        mess = Message.objects.filter(user = self,is_deleted = False,is_read = False)
        return mess
    
    @property
    def notification(self):
        notifications = Notification.objects.filter(is_read = False, is_deleted = False)
        for item in notifications:
            print(item.heading)
        return notifications



class Address(models.Model):
    user = models.ForeignKey("User", verbose_name=_(""), on_delete=models.CASCADE)
    house_number = models.CharField(_(""), max_length=50)
    building_number = models.CharField(_(""), max_length=50)
    street_name = models.CharField(_(""), max_length=50)
    city = models.CharField(_(""), max_length=50)
    pin_number = models.IntegerField(_(""))
    phone_number = models.CharField(_(""), max_length=50)
    disabled = models.BooleanField(_(""),default=False)
    last_modified = models.DateField(_(""), auto_now=True, auto_now_add=False)
    is_deleted = models.BooleanField(_(""),default=False)

class Wallet(models.Model):
    TRANSACTION_CHOICES = (
        ('1', 'Cancellation'),
        ('2', 'Deposit'),
        ('3', 'Payment'),
        ('4', 'Others'),
        ('5', 'Order refusal')
    )
    user = models.ForeignKey("User", verbose_name=_(""), on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(_(""), auto_now=False, auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES,default='1')
    order = models.ForeignKey("store.Order", verbose_name=_(""), on_delete=models.CASCADE,null=True)
    amount = models.FloatField(_(""),default= 0)

class Message(models.Model):
    def get_default_user():
        return 
    user = models.ForeignKey("User", verbose_name=_(""), on_delete=models.CASCADE,related_name="recieved")
    heading = models.TextField(_(""))
    text = models.TextField(_(""))
    sender = models.ForeignKey("User", verbose_name=_(""), on_delete=models.CASCADE,default=get_default_user)
    created_at = models.DateTimeField(_(""), auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(_(""), auto_now=True, auto_now_add=False)
    is_read = models.BooleanField(_(""),default=False)
    is_deleted = models.BooleanField(_(""),default= False)

