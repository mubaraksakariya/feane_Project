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
    product_category = models.ForeignKey("Category", verbose_name=_(""), on_delete=models.SET_NULL , null=True)
    product_size = models.ForeignKey("Size", verbose_name=_(""), on_delete=models.SET_NULL, null=True)
    
    @property
    def first_image(self):
        images = Images.objects.filter(product = self.id)
        if images:
            return images[0].image
        else:
            return None

class Size (models.Model):
    size_type = models.CharField(_(""), max_length=50,default='normal')

class Category(models.Model):
    category_name = models.CharField(_(""), max_length=50)

class Images(models.Model):
    product = models.ForeignKey("Product", verbose_name=_(""), on_delete=models.CASCADE)
    image = models.ImageField(_(""), upload_to='image_uploads',default='blank_img.jpg')
    


class Cart(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", verbose_name=_(""), on_delete=models.CASCADE)
    quantity = models.IntegerField(_(""))
    purchased = models.BooleanField(_(""),default=False)
    status = models.CharField(_(""), max_length=50,null=True)
    
    @property
    def total(self):
        return self.product.product_prize * self.quantity
    
class Order(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    cart = models.ManyToManyField("Cart", verbose_name=_(""),related_name='cart')
    delivery_address = models.ForeignKey("customer.Address", verbose_name=_(""), on_delete=models.SET_NULL,null=True)
    order_created = models.DateTimeField(_(""), auto_now=True, auto_now_add=False)
    order_modified = models.DateField(_(""), auto_now=False, auto_now_add=True)
    paid = models.BooleanField(_(""))
    payment_details = models.ForeignKey("Payment", verbose_name=_(""), on_delete=models.CASCADE)
    order_processed = models.BooleanField(_(""),default=False)

    @property
    def total(self):
        cart = self.cart.all()
        return sum([item.total for item in cart])


# class Payment_method(models.Model):
#     user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
#     name = models.CharField(_(""), max_length=50)
#     card_number = models.CharField(_(""), max_length=50,null=True)
#     expire_date = models.DateField(_(""), auto_now=False, auto_now_add=False,null=True)
#     cvv = models.IntegerField(_(""),null=True)
#     upi_id = models.CharField(_(""), max_length=50,null=True)

class Payment(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    payment_type = models.CharField(_(""), max_length=50,null=True)
    payment_id = models.CharField(_(""), max_length=50,null=True)
    date = models.DateField(_(""), auto_now=True, auto_now_add=False)




