from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import pytz

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
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(_(""),default=False)


    @property
    def first_image(self):
        images = Images.objects.filter(product = self.id)
        if images:
            return images[0].image
        else:
            return None

class Size (models.Model):
    size_type = models.CharField(_(""), max_length=50,default='normal')
    is_deleted = models.BooleanField(_(""),default=False)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    category_name = models.CharField(_(""), max_length=50)
    is_deleted = models.BooleanField(_(""),default=False)
    updated_at = models.DateTimeField(auto_now=True)

class Images(models.Model):
    product = models.ForeignKey("Product", verbose_name=_(""), on_delete=models.CASCADE)
    image = models.ImageField(_(""), upload_to='image_uploads',default='blank_img.jpg')

class Cart(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", verbose_name=_(""), on_delete=models.CASCADE)
    quantity = models.IntegerField(_(""))
    purchased = models.BooleanField(_(""),default=False)
    status = models.CharField(_(""), max_length=50,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total(self):
        return (self.product.product_prize) * (self.quantity)
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('0', 'Requested for Cancel'),
        ('1', 'Waiting to accept order'),
        ('2', 'Order is being Prepared'),
        ('3', 'Ready to Ship'),
        ('4', 'Out for delivery'),
        ('5', 'Done'),
        ('6', 'Cancelled'),
        ('7', 'Order Refused'),
    )

    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    cart = models.ManyToManyField("Cart", verbose_name=_(""),related_name='cart')
    delivery_address = models.ForeignKey("customer.Address", verbose_name=_(""), on_delete=models.SET_NULL,null=True)
    order_created = models.DateTimeField(_(""), auto_now=False, auto_now_add=True)
    order_modified = models.DateField(_(""), auto_now=True, auto_now_add=False)
    paid = models.BooleanField(_(""))
    payment_details = models.ForeignKey("Payment", verbose_name=_(""), on_delete=models.CASCADE)
    order_processed = models.BooleanField(_(""),default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='1')
    coupon = models.ForeignKey("Coupon", verbose_name=_(""), on_delete=models.CASCADE,null=True)

    @property
    def order_date(self):
        return self.order_created
    
    @property
    def order_progress(self):
        return int(self.status)*25
    
    @property
    def total(self):
        cart = self.cart.all()
        return sum([item.total for item in cart])
    
    @property
    def discounted_total(self):
        value =  self.total
        if self.coupon is not None:
            value = value*((100 - self.coupon.discount)/100)
        return value
    @property
    def amount_to_pay(self):
        if self.payment_details.wallet_transaction is not None:
            wallet_amount_payed =  self.payment_details.wallet_transaction.amount
        else:
            wallet_amount_payed = 0
        print("amount to pay is")
        print(wallet_amount_payed)
        return (self.discounted_total + wallet_amount_payed)

class Coupon(models.Model):
    name = models.CharField(_(""), max_length=50)
    discount = models.IntegerField(_(""))
    created_at = models.DateTimeField(_(""), auto_now=False, auto_now_add=True)
    is_deleted = models.BooleanField(_(""),default=False)

class Payment(models.Model):
    user = models.ForeignKey("customer.User", verbose_name=_(""), on_delete=models.CASCADE)
    payment_type = models.CharField(_(""), max_length=50,null=True)
    payment_id = models.CharField(_(""), max_length=50,null=True)
    wallet_transaction = models.ForeignKey("customer.Wallet", verbose_name=_(""), on_delete=models.CASCADE,null=True)
    date = models.DateField(_(""), auto_now=True, auto_now_add=False)


