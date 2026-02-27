from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import RegisterForm, ProfileEditForm, UserEmailForm
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()   # username OR email
        password = request.POST.get('password', '').strip()
        remember = request.POST.get('remember') == 'on'
        user = authenticate(request, username=identifier, password=password)
        if user is None and '@' in identifier:
            try:
                u = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)

            # Remember me:
            # إذا غير مفعّل => الجلسة تنتهي عند إغلاق المتصفح
            if not remember:
                request.session.set_expiry(0)

            messages.success(request, "تم تسجيل الدخول.")
            return redirect('home')

        messages.error(request, "اسم المستخدم/البريد أو كلمة المرور غير صحيحة.")

    return render(request, 'accounts/login.html')
    
def logout_view(request):
    logout(request)
    messages.info(request, "You are logged out.")
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created, you can log in now.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.user.is_staff:
        return redirect('home')
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    if request.user.is_staff:
        return redirect('home')

    profile = request.user.profile
    if request.method == 'POST':
        pform = ProfileEditForm(request.POST, request.FILES, instance=profile)
        eform = UserEmailForm(request.POST, instance=request.user)
        if pform.is_valid() and eform.is_valid():
            pform.save()
            eform.save()
            messages.success(request, "Data has been updated.")
            return redirect('profile')
    else:
        pform = ProfileEditForm(instance=profile)
        eform = UserEmailForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'pform': pform, 'eform': eform})
