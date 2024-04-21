from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .forms import *
from globals.email import EmailService
from chat.models import Room


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, _('Activate you account'))
                return redirect('send_activation_view')
        else:
            messages.error(request, _('Invalid Credentials'))

    return render(request, 'user/login.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            activation = Activation(user=user)
            activation.save()

            # send activation code
            activation_code = activation.activation_code
            activation_link = f'http://127.0.0.1:8000/user/activate/{activation_code}/'
            EmailService.send_activation_email(
                activation_link,
                from_email=settings.EMAIL_HOST_USER,
                to_emails=[user.email]
            )
            messages.success(request, _(f'Account was created for {form.cleaned_data["email"]}'))
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'user/register.html', {'form': form})


def activate_account(request, code):
    activation = Activation.objects.filter(activation_code=code).first()
    now = timezone.now()

    if not activation:
        messages.error(request, _('Invalid activation code'))
        return redirect('login')

    if (now - activation.expired_at).total_seconds() > 0:
        messages.error(request, _('Invalid / expired activation code'))
        return redirect('login')

    user = activation.user
    user.is_active = True
    user.save()

    messages.success(request, _('Account has been activated successfully'))
    return redirect('login')


def activation_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Users.objects.filter(email=email).first()
        if not user:
            messages.success(request, _('User with this email does not exist'))
            return redirect('send_activation_view')

        if user.is_active:
            messages.success(request, _('User already activated'))
            return redirect('login')

        activation = Activation(user=user)
        activation.save()
        activation_code = activation.activation_code
        activation_link = f'http://127.0.0.1:8000/user/activate/{activation_code}/'
        EmailService.send_activation_email(
            activation_link,
            from_email=settings.EMAIL_HOST_USER,
            to_emails=[user.email]
        )
        messages.success(request, _(f'Please check your mail for activation link'))
        return redirect('login')

    return render(request, 'user/activation_request.html')


def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Users.objects.filter(email=email).first()
        if not user:
            messages.success(request, _('User with this email does not exist'))
            return redirect('login')

        if not user.is_active:
            messages.success(request, _('Activate your account'))
            return redirect('send_activation_view')

        code = PasswordReset(user=user)
        code.save()
        reset_code = code.reset_code
        reset_link = f'http://127.0.0.1:8000/user/reset/password/{reset_code}/'
        EmailService.send_reset_password_email(
            reset_link,
            from_email=settings.EMAIL_HOST_USER,
            to_emails=[user.email]
        )
        messages.success(request, _(f'Please check your mail for activation link'))
        return redirect('login')

    return render(request, 'user/forget-password.html')


def reset_password(request, code):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        password_reset = PasswordReset.objects.filter(reset_code=code).first()
        now = timezone.now()

        if not password_reset:
            messages.error(request, _('Invalid code'))
            return redirect('forget_password')

        if (now - password_reset.expired_at).total_seconds() > 0:
            messages.error(request, _('Invalid / expired code'))
            return redirect('forget_password')

        user = password_reset.user
        user.set_password(new_password)
        password_reset.expired_at = now
        user.save()
        password_reset.save()

        messages.success(request, _('Account has been activated successfully'))
        return redirect('login')

    return render(request, 'user/reset_password.html')


@login_required
def dashboard(request):
    rooms = Room.objects.all()
    context = {
        'rooms': rooms
    }
    return render(request, 'user/dashboard.html', context)


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


def error_401(request, exception=None):
    return render(request, 'user/401.html', status=401)


def error_403(request, exception=None):
    return render(request, 'user/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'user/404.html', status=404)


def error_500(request, exception=None):
    return render(request, 'user/500.html', status=500)
