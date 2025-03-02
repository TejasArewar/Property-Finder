from django.shortcuts import render,redirect, get_object_or_404
from App.models import user_signup, Property_Register, Profile_pictures, Payment
from django.contrib import messages
import random
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse

# Create your views here.

def home(request) :
    location = Property_Register.objects.all()
    return render(request, 'home.html', {'location' : location})



def signup(request) :
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        try :
            validate_email(email)
        except ValidationError :
            messages.error(request, 'Invalid email format.')
            return redirect('/signup/')

        if confirm_password == password:
            if user_signup.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('/signup/')

            elif user_signup.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('/signup/')

            else:
                password = make_password(password)
                user = user_signup.objects.create(
                    username=username,
                    email=email,
                    password=password,
                    confirm_password=confirm_password
                    )
                user.save()
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('/login/')

        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('/signup/')

    return render(request, 'signup.html')
    

def login(request) :
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = user_signup.objects.get(username=username)
            if user.username == username and check_password(password,user.password):   # check_password is used to unhash the password
                request.session['id'] = user.id
                return redirect('/property/')
            else:
                messages.info(request,'Invalid Credentials')
                return redirect('/login/')
            
        except user_signup.DoesNotExist:
            messages.info(request,'Username does not Exists')
            return redirect('/login/')
    return render(request, 'login.html')


def logout(request) :
    if request.session.get('id'):
        request.session.flush()
        messages.success(request, "Logged out successfully.")
    return redirect('/login/')


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        otp = request.POST.get('otp')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = user_signup.objects.get(username=username)
        except user_signup.DoesNotExist:
            messages.error(request, "Username does not exist")
            return render(request, 'forgot_password.html')

        if 'send_otp' in request.POST:
            otp_code = random.randint(1000,9999)
            user.email_otp = otp_code
            user.save()
            send_mail(
                'One Time Password for password Reset',
                f'Your OTP for password reset is: {otp_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "OTP has been sent to your email")
            return render(request, 'forgot_password.html')

        if otp == user.email_otp:
            if password == confirm_password:
                user.save()
                messages.success(request, "Your password has been updated successfully")
                return redirect('/login/')
            else:
                messages.error(request, "Passwords do not match")
                return render(request, 'forgot_password.html')

        else:
            messages.error(request, "Invalid OTP")
            return render(request, 'forgot_password.html')

    return render(request, 'forgot_password.html')



def profile_pic(request, id) :
    if request.method == "POST":
        profile_picture = request.FILES.get('profile_pic')
        user_id = request.session.get('id')

        if not user_id:
            messages.error(request, "User session not found. Please log in again.")
            return redirect('/login/')

        try:
            user = user_signup.objects.get(id=user_id)
            profile_pics, created = Profile_pictures.objects.get_or_create(user=user)
            profile_pics.profile_pic = profile_picture
            profile_pics.save()
            messages.success(request, "Profile picture updated successfully.")
        except user_signup.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('/property/')

    return redirect('/property/')



def delete_profile_pic(request, id) :
    pic = Profile_pictures.objects.get(id = id)
    pic.delete()
    return redirect('/property/')


def property(request):
    properties = Property_Register.objects.all()

    user_id = request.session.get('id')

    try:
        button = user_signup.objects.get(id=user_id)
    except user_signup.DoesNotExist:
        button = None

    is_subscribed = Payment.objects.filter(user=button).exists() if button else False

    profiles = user_signup.objects.get(id=user_id) if user_id else None
    profile_pic = None
    if profiles:
        try:
            profile_pic = Profile_pictures.objects.get(user=profiles)
        except Profile_pictures.DoesNotExist:
            profile_pic = None

    if request.method == "POST":
        if 'contact' in request.POST:
            property_id = request.POST.get('property_id')
            owner_mail = Property_Register.objects.filter(id=property_id).first()

            if owner_mail:
                subject = 'Inquiry for your Property'
                from_email = 'tejas.arewar.ta@gmail.com'
                msg_owner = f"""
                    <html>
                        <body>
                            <p><strong>{profiles.username}</strong> has shown interest in your Property.</p>
                            <p><strong>{profiles.username}</strong> wants to get your contact details for further discussion of your Property.</p>
                            <p>You may share your details on his/her email({profiles.email}).</p>
                            <h5>Property Details -</h5>
                            <p>Name : {owner_mail.propertyname}</p>
                            <p>Price : {owner_mail.price}</p>
                            <p>Area : {owner_mail.area}</p>
                            <p>City : {owner_mail.city}</p>
                            <p>State : {owner_mail.state}</p>
                            <p>Thank you.</p>
                        </body>
                    </html>
                """
                to_email_owner = owner_mail.email
                msg_owner = EmailMultiAlternatives(subject, msg_owner, from_email, [to_email_owner])
                msg_owner.content_subtype = 'html'

                msg_user = f"""
                    <p>Thank you for showing interest in the property.</p>
                    <p>The property owner will reach out to you soon for further discussions regarding your inquiry.</p>
                    <p>We appreciate your interest in our listings.</p>
                    <h5>Property Details -</h5>
                    <p>Name : {owner_mail.propertyname}</p>
                    <p>Price : {owner_mail.price}</p>
                    <p>Area : {owner_mail.area}</p>
                    <p>City : {owner_mail.city}</p>
                    <p>State : {owner_mail.state}</p>
                    <p>Best regards,</p>
                    <p><strong>Property Finder</strong> 🗺️</p>
                """
                to_email_user = profiles.email
                msg_user = EmailMultiAlternatives('Property Interest Confirmation', msg_user, from_email, [to_email_user])
                msg_user.content_subtype = 'html'

                try:
                    msg_owner.send()
                    msg_user.send()
                    messages.success(request, 'Mail sent successfully.')
                except Exception as e:
                    messages.error(request, f"Error sending mail for property: {str(e)}")
            else:
                messages.error(request, 'Property not found.')
            return redirect('property')

        elif 'propertynames' in request.POST:
            propertyname = request.POST.get('propertyname')
            price = request.POST.get('price')
            state = request.POST.get('state')
            city = request.POST.get('city')
            area = request.POST.get('area')
            pincode = request.POST.get('pincode')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            mobile = request.POST.get('mobile')
            email = request.POST.get('email')
            image = request.FILES.get('image')

            if Property_Register.objects.filter(propertyname=propertyname).exists():
                messages.info(request, 'Property Name already exists')
            else:
                try:
                    Property_Register.objects.create(
                        propertyname=propertyname,
                        price=price,
                        state=state,
                        city=city,
                        area=area,
                        pincode=pincode,
                        latitude=latitude,
                        longitude=longitude,
                        mobile=mobile,
                        email=email,
                        image=image
                    )
                    messages.success(request, 'Property added successfully!')
                except Exception as e:
                    messages.error(request, f"Error saving property: {str(e)}")

            return redirect('property')

    properties_add = Property_Register.objects.exclude(email=profiles.email)

    city = request.POST.get('city', '')
    area = request.POST.get('area', '')
    if city and area:
        properties_add = properties_add.filter(city__icontains=city, area__icontains=area)
    elif city:
        properties_add = properties_add.filter(city__icontains=city)
    elif area:
        properties_add = properties_add.filter(area__icontains=area)

    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'price_low_to_high':
        properties_add = properties_add.order_by('price')
    elif sort_by == 'price_high_to_low':
        properties_add = properties_add.order_by('-price')

    return render(request, 'property.html', {
        'properties': properties,
        'profiles': profiles,
        'profile_pic': profile_pic,
        'properties_add': properties_add,
        'is_subscribed': is_subscribed
    })





def my_adds(request) :
    user_id = request.session.get('id')
    profiles = user_signup.objects.get(id=user_id) if user_id else None
    profile_pic = None

    if profiles:
        try:
            profile_pic = Profile_pictures.objects.get(user=profiles)
        except Profile_pictures.DoesNotExist:
            profile_pic = None
        properties = Property_Register.objects.filter(email=profiles.email)
    else:
        properties = Property_Register.objects.none()

    return render(request, 'my_adds.html', {
        'properties': properties,
        'profiles': profiles,
        'profile_pic': profile_pic,
    })




def edit_prop(request, pk):
    property = get_object_or_404(Property_Register, pk=pk)

    if request.method == 'POST':
        propertyname = request.POST.get('propertyname')
        price = request.POST.get('price')
        state = request.POST.get('state')
        city = request.POST.get('city')
        area = request.POST.get('area')
        pincode = request.POST.get('pincode')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        image = request.FILES.get('image')

        if not propertyname or not price or not state or not city or not area or not pincode or not latitude or not longitude or not mobile or not email:
            return HttpResponse("All fields are required.", status=400)

        try:
            price = float(price)
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return HttpResponse("Invalid price or coordinates.", status=400)

        property.propertyname = propertyname
        property.price = price
        property.state = state
        property.city = city
        property.area = area
        property.pincode = pincode
        property.latitude = latitude
        property.longitude = longitude
        property.mobile = mobile
        property.email = email

        if image:
            property.image = image 

        property.save()
        return redirect('/my_adds/')

    else:
        return render(request, 'edit_prop.html', {'property': property})



def delete_prop(request, id):
    prop = get_object_or_404(Property_Register, id=id)
    prop.delete()
    return redirect('/my_adds/')




def subscription(request):
    user_id = request.session.get('id')

    try:
        user = user_signup.objects.get(id=user_id)
    except user_signup.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('/login/')

    is_subscribed = Payment.objects.filter(user=user).exists()
    return render(request, 'subscription.html', {'is_subscribed': is_subscribed})



def subscription_success(request, payment_id, payment):
    user_id = request.session.get('id')

    if not user_id:
        return redirect('/login/')

    try:
        user = user_signup.objects.get(id=user_id)
    except user_signup.DoesNotExist:
        messages.error(request, 'Please Signup First.')
        return redirect('/signup/')

    if Payment.objects.filter(user=user).exists():
        messages.info(request, 'You have already Subscribed.')
        return redirect('/property/')

    Payment.objects.create(
        user=user,
        username=user.username,
        email=user.email,
        amount=payment,
        payment_id=payment_id
    )

    send_mail(
        'Premium Subscription Successful',
        f'Hello {user.username},\n\nYou have successfully subscribed to our Property Finder Premium. Your payment amount is {payment} and payment ID is {payment_id}.\n\nThank you for Subscribing.\n\n\n\n\n\n\n\nBest Regards\nProperty Finder 🗺️',
        'tejas.arewar.ta@gmail.com',
        [user.email],
        fail_silently=False,
    )

    messages.success(request, 'Premium Subscription Successful')
    return render(request, 'subscription_success.html', {'payment_id': payment_id})
