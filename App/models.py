from django.db import models

# Create your models here.
class user_signup(models.Model) :
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Profile_pictures(models.Model) :
    user = models.ForeignKey(user_signup, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_images/')

    def __str__(self):
        return self.user.username


class Property_Register(models.Model) :
    propertyname = models.CharField(max_length=100)
    price = models.BigIntegerField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    latitude = models.FloatField()
    longitude = models.FloatField()
    mobile = models.BigIntegerField(unique=True)
    email = models.EmailField(max_length=100)
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return self.propertyname+ ', ' +self.city
    
    


class Payment(models.Model):
    user=models.ForeignKey(user_signup,on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    amount=models.DecimalField(default=0, decimal_places=2, max_digits=10)
    payment_id=models.CharField()

    def __str__(self):
        return self.username