from django.db import models

class Notification(models.Model):
    heading = models.CharField( max_length=100)
    text = models.TextField()
    image = models.ImageField( upload_to='image_uploads', height_field=None, width_field=None, max_length=None,null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
