from django.contrib import admin
from App.models import Property_Register, user_signup, Profile_pictures, Payment

# Register your models here.

admin.site.register(Property_Register)
admin.site.register(user_signup)
admin.site.register(Profile_pictures)
admin.site.register(Payment)