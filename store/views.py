# store/views.py

from decimal import Decimal
import random



from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import (
    ContactForm,
    ProfileForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from .models import (
    BlogPost,
    ContactMessage,
    Order,
    OrderReview,
    Profile,
    Project,
)


# -------------------------------------------------------------------
# HELPER: dummy SMS sender (replace with real API later)
# -------------------------------------------------------------------
def send_sms(phone: str, message: str) -> None:
    """
    Temporary SMS sender for development.
    Replace this with actual integration (Twilio / MSG91 / etc.).
    """
    print(f"[DEBUG SMS] To: {phone} | Message: {message}")


# -------------------------------------------------------------------
# EMAIL VERIFICATION
# -------------------------------------------------------------------
def verify_email(request, uidb64, token):
    """
    Called when user clicks the verification link in email.
    Activates account if token is valid.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been verified! Please login.")
        return redirect("store:login")
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("store:signup")


# -------------------------------------------------------------------
# OTP-BASED PASSWORD RESET (SKELETON)
# -------------------------------------------------------------------
def send_otp(request):
    """
    POST: phone -> send OTP via SMS and cache it.
    """
    if request.method != "POST":
        return JsonResponse({"status": "method_not_allowed"}, status=405)

    phone = request.POST.get("phone")
    if not phone:
        return JsonResponse({"status": "no_phone"}, status=400)

    otp = random.randint(100000, 999999)
    cache.set(phone, otp, timeout=180)  # 3 minutes validity
    send_sms(phone, f"Your Techsense OTP is: {otp}")
    return JsonResponse({"status": "sent"})


def verify_otp(request):
    """
    POST: phone + otp -> verifies OTP.
    If ok, store phone in session for reset_password.
    """
    if request.method != "POST":
        return JsonResponse({"status": "method_not_allowed"}, status=405)

    phone = request.POST.get("phone")
    otp_input = request.POST.get("otp")
    if not phone or not otp_input:
        return JsonResponse({"status": "invalid_data"}, status=400)

    otp = cache.get(phone)

    if otp and str(otp) == otp_input:
        request.session["phone_verified"] = phone
        return JsonResponse({"status": "verified"})
    return JsonResponse({"status": "failed"})

def forgot_password(request):
    """
    Page where user enters phone number and requests OTP.
    Frontend will call send_otp and verify_otp via AJAX.
    """
    return render(request, "store/forgot_password.html")

def reset_password(request):
    """
    Final step of OTP reset flow.
    User must have a verified phone in session.
    """
    if not request.session.get("phone_verified"):
        messages.error(request, "Please verify OTP before resetting your password.")
        return redirect("store:forgot_password")

    if request.method == "POST":
        new_pass = request.POST.get("password")
        phone = request.session["phone_verified"]

        try:
            profile = Profile.objects.get(phone=phone)
        except Profile.DoesNotExist:
            messages.error(request, "No user found for this phone number.")
            return redirect("store:forgot_password")

        user = profile.user
        user.set_password(new_pass)
        user.save()
        del request.session["phone_verified"]

        messages.success(request, "Password updated successfully! Please login.")
        return redirect("store:login")

    return render(request, "store/reset_password.html")


# -------------------------------------------------------------------
# PUBLIC PAGES
# -------------------------------------------------------------------
def home(request):
    # featured project
    featured_project = (
        Project.objects.filter(is_active=True, is_featured=True)
        .order_by("-created_at")
        .first()
    )

    # latest active projects
    latest_projects = (
        Project.objects.filter(is_active=True)
        .order_by("-created_at")[:6]
    )

    # latest published blog posts
    latest_posts = (
        BlogPost.objects.filter(is_published=True)
        .order_by("-created_at")[:3]
    )

    context = {
        "featured_project": featured_project,
        "latest_projects": latest_projects,
        "latest_posts": latest_posts,
    }
    return render(request, "store/home.html", context)


def project_list(request):
    q = request.GET.get("q", "").strip()
    tech = request.GET.get("tech", "").strip()
    category = request.GET.get("category", "").strip()
    level = request.GET.get("level", "").strip()

    projects = Project.objects.filter(is_active=True).order_by("-created_at")

    if q:
        projects = projects.filter(
            Q(title__icontains=q)
            | Q(short_description__icontains=q)
            | Q(description__icontains=q)
        )

    if tech:
        projects = projects.filter(tech_stack__icontains=tech)

    if category:
        projects = projects.filter(category=category)

    if level:
        projects = projects.filter(level=level)

    tech_list = (
        Project.objects.filter(is_active=True)
        .values_list("tech_stack", flat=True)
        .distinct()
    )

    context = {
        "projects": projects,
        "q": q,
        "tech": tech,
        "tech_list": tech_list,
        "category": category,
        "level": level,
    }
    return render(request, "store/project_list.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)
    extra_images = project.images.all()  # FK with related_name='images'
    return render(
        request,
        "store/project_detail.html",
        {"project": project, "extra_images": extra_images},
    )


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "store/blog_list.html", {"posts": posts})


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    related_posts = (
        BlogPost.objects.filter(is_published=True)
        .exclude(pk=pk)[:3]
    )
    return render(
        request,
        "store/blog_detail.html",
        {"post": post, "related_posts": related_posts},
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks! Your project idea has been submitted. We’ll contact you soon.",
            )
            return redirect("store:contact")
    else:
        form = ContactForm()

    return render(request, "store/contact.html", {"form": form})


# -------------------------------------------------------------------
# AUTH: SIGNUP / LOGIN / LOGOUT
# -------------------------------------------------------------------
def user_signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # create inactive user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False
            user.save()

            # send verification email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_link = request.build_absolute_uri(
                reverse(
                    "store:verify_email",
                    kwargs={"uidb64": uid, "token": token},
                )
            )

            subject = "Verify your Techsense Account"
            message = (
                f"Hi {user.username},\n\n"
                f"Please click the link below to verify your email address:\n{verify_link}\n\n"
                f"If you did not create this account, you can ignore this email."
            )
            EmailMessage(subject, message, to=[user.email]).send()

            messages.success(
                request,
                "Account created! Please check your email and verify your account before logging in.",
            )
            return redirect("store:login")
    else:
        form = UserRegistrationForm()

    return render(request, "store/signup.html", {"form": form})


from django.contrib.auth import get_user_model
UserModel = get_user_model()

def user_login(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Try to authenticate first
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("store:home")

        # If auth failed, check if user exists but is inactive (email not verified)
        try:
            existing_user = UserModel.objects.get(username=username)
            if not existing_user.is_active:
                error = "Your email is not verified yet. Please check your inbox for the verification link."
            else:
                error = "Invalid username or password."
        except UserModel.DoesNotExist:
            error = "Invalid username or password."

    return render(request, "store/login.html", {"error": error})



def user_logout(request):
    logout(request)
    return redirect("store:home")


# -------------------------------------------------------------------
# ORDERS & BUY FLOW
# -------------------------------------------------------------------
@login_required
def buy_project(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)

    order = Order.objects.create(
        user=request.user,
        project=project,
        status="pending",
    )

    messages.success(
        request,
        f"Order placed for '{project.title}'. We will contact you soon.",
    )
    return redirect("store:order_detail", order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    review = getattr(order, "review", None)

    if request.method == "POST":
        # Cancel order
        if "cancel_order" in request.POST and order.status == "pending":
            order.status = "cancelled"
            order.save()
            messages.success(request, "Your order has been cancelled.")
            return redirect("store:order_detail", order_id=order.id)

        # Submit / update review (only when completed)
        if "submit_review" in request.POST and order.status == "completed":
            rating = int(request.POST.get("rating", 5))
            comment = request.POST.get("comment", "").strip()
            OrderReview.objects.update_or_create(
                order=order,
                defaults={"rating": rating, "comment": comment},
            )
            messages.success(request, "Thanks for your feedback!")
            return redirect("store:order_detail", order_id=order.id)

    context = {
        "order": order,
        "review": review,
    }
    return render(request, "store/order_detail.html", context)


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/my_orders.html", {"orders": orders})


# -------------------------------------------------------------------
# ACCOUNT / PROFILE VIEWS
# -------------------------------------------------------------------
@login_required
def account_dashboard(request):
    return render(request, "store/account_dashboard.html")


@login_required
def account_settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("store:account_settings")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "store/account_settings.html", context)


@login_required
def account_change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            messages.success(request, "Password updated successfully.")
            return redirect("store:account_change_password")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "store/account_change_password.html", {"form": form})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated ✅")
            return redirect("store:account_dashboard")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "store/profile_edit.html", context)


# -------------------------------------------------------------------
# CART
# -------------------------------------------------------------------
@login_required
def add_to_cart(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)

    cart = request.session.get("cart", {})
    project_id = str(project.id)

    if project_id in cart:
        cart[project_id] += 1
    else:
        cart[project_id] = 1

    request.session["cart"] = cart
    messages.success(request, f"'{project.title}' added to your cart.")
    return redirect("store:view_cart")


@login_required
def view_cart(request):
    cart = request.session.get("cart", {})
    project_ids = cart.keys()

    projects = Project.objects.filter(id__in=project_ids)
    items = []
    total = Decimal("0")

    for project in projects:
        qty = cart.get(str(project.id), 0)
        subtotal = project.price * qty
        total += subtotal
        items.append(
            {
                "project": project,
                "qty": qty,
                "subtotal": subtotal,
            }
        )

    gst = total * Decimal("0.18")
    grand_total = total + gst

    return render(
        request,
        "store/cart.html",
        {
            "items": items,
            "total": total,
            "gst": gst,
            "grand_total": grand_total,
        },
    )


@login_required
def remove_from_cart(request, project_id):
    cart = request.session.get("cart", {})
    project_id = str(project_id)
    if project_id in cart:
        del cart[project_id]
        request.session["cart"] = cart
        messages.success(request, "Item removed from cart.")
    return redirect("store:view_cart")
