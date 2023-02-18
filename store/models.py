from django.db import models
from django.utils.translation import gettext_lazy as _
from customer.models import User

# Create your models here.
#PRODUCT models here
#############################################

class Product(models.Model):
    product_name = models.CharField(_("product_name"), max_length=50)    
    product_stock_amount = models.IntegerField(_("stock"))
    product_prize = models.IntegerField(_("prize"))
    product_text = models.TextField(_(""))
    product_available = models.BooleanField(_(""))
    product_category = models.ForeignKey("Category", verbose_name=_(""), on_delete=models.CASCADE)
    product_size = models.ForeignKey("Size", verbose_name=_(""), on_delete=models.CASCADE)
    product_image = models.ForeignKey("Images", verbose_name=_(""), on_delete=models.CASCADE)
    

class Size (models.Model):
    size_type = models.CharField(_(""), max_length=50,default='normal')

class Category(models.Model):
    category_name = models.CharField(_(""), max_length=50)

class Images(models.Model):
    image1 = models.ImageField(_(""), upload_to='image_uploads',default='blank_img.jpg')
    image2  = models.ImageField(_(""), upload_to='image_uploads',default='blank_img.jpg')
    image3  = models.ImageField(_(""), upload_to='image_uploads',default='blank_img.jpg')


class Cart(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", verbose_name=_(""), on_delete=models.CASCADE)
    quantity = models.IntegerField(_(""))
    purchased = models.BooleanField(_(""),default=False)
    status = models.CharField(_(""), max_length=50,null=True)
    
class Order(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    cart = models.ManyToManyField("Cart", verbose_name=_(""),related_name='cart')
    delivery_address = models.ForeignKey("customer.Address", verbose_name=_(""), on_delete=models.DO_NOTHING)
    order_created = models.DateTimeField(_(""), auto_now=True, auto_now_add=False)
    order_modified = models.DateField(_(""), auto_now=False, auto_now_add=True)
    paid = models.BooleanField(_(""))
    payment_details = models.ForeignKey("Payment", verbose_name=_(""), on_delete=models.CASCADE)
    order_processed = models.BooleanField(_(""),default=False)

class Payment_method(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    name = models.CharField(_(""), max_length=50)
    card_number = models.CharField(_(""), max_length=50,null=True)
    expire_date = models.DateField(_(""), auto_now=False, auto_now_add=False,null=True)
    cvv = models.IntegerField(_(""),null=True)
    upi_id = models.CharField(_(""), max_length=50,null=True)

class Payment(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    payment_type = models.ForeignKey("Payment_method", verbose_name=_(""), on_delete=models.CASCADE,default='cod')
    amount = models.FloatField(_(""))
    date = models.DateField(_(""), auto_now=True, auto_now_add=False)




