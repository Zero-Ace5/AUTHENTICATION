from django.core.mail import send_mail


def send_signup_mail(email, otp, user_type):
    subject = f"Welcome {user_type.capitalize()} - OTP {otp}"
    message = (
        f"Welcome! \n\n"
        f"User Type: {user_type.capitalize()}\n\n"
        f"Your OTP is: {otp}\n\n"
        f"This OTP is valid for 5 minutes."
    )
    send_mail(subject, message, None, [email])


def send_login_email(email, otp):
    subject = f"Your login OTP is {otp}"
    message = (
        f"Your OTP is: {otp}\n\nThis OTP is valid for 5 minutes."
    )
    send_mail(subject, message, None, [email])

# None is sender's mail
