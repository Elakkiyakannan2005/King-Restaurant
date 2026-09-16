import json
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import SignUpForm, ContactForm
from .models import MenuItem, Favorite, Order


def index(request):
    veg_items = MenuItem.objects.filter(category=MenuItem.VEG, is_available=True)
    non_veg_items = MenuItem.objects.filter(category=MenuItem.NON_VEG, is_available=True)

    favorite_ids = set()
    favorite_items = []
    orders = []

    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list("menu_item_id", flat=True)
        )
        favorite_items = MenuItem.objects.filter(id__in=favorite_ids)
        orders = Order.objects.filter(user=request.user).select_related("menu_item")

    context = {
        "veg_items": veg_items,
        "non_veg_items": non_veg_items,
        "all_items": list(veg_items) + list(non_veg_items),
        "favorite_ids": favorite_ids,
        "favorite_items": favorite_items,
        "orders": orders,
        "signup_form": SignUpForm(),
        "contact_form": ContactForm(),
    }
    return render(request, "menu/index.html", context)


# ---------------------------------------------------------------------
# Auth (AJAX, JSON in / JSON out — the login/signup cards live on the
# same page rather than on separate pages)
# ---------------------------------------------------------------------

@require_POST
def login_view(request):
    email_or_username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    user = authenticate(request, username=email_or_username, password=password)
    if user is None:
        # Allow logging in with an email address too.
        from django.contrib.auth.models import User

        try:
            matched = User.objects.get(email__iexact=email_or_username)
            user = authenticate(request, username=matched.username, password=password)
        except User.DoesNotExist:
            user = None

    if user is not None:
        login(request, user)
        return JsonResponse({"success": True, "username": user.username})
    return JsonResponse({"success": False, "message": "Invalid email/username or password."}, status=400)


@require_POST
def signup_view(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse({"success": True, "username": user.username})
    return JsonResponse({"success": False, "errors": form.errors.get_json_data()}, status=400)


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"success": True})


# ---------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------

@login_required
@require_POST
def toggle_favorite(request, item_id):
    item = MenuItem.objects.filter(id=item_id).first()
    if item is None:
        return JsonResponse({"success": False, "message": "Item not found."}, status=404)

    favorite, created = Favorite.objects.get_or_create(user=request.user, menu_item=item)
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    return JsonResponse({"success": True, "is_favorite": is_favorite, "item_id": item.id})


# ---------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------

@login_required
@require_POST
def place_order(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = request.POST

    item_id = payload.get("item_id")
    quantity = int(payload.get("quantity") or 1)

    item = MenuItem.objects.filter(id=item_id, is_available=True).first()
    if item is None:
        return JsonResponse({"success": False, "message": "Item not found."}, status=404)
    if quantity < 1:
        quantity = 1

    order = Order.objects.create(
        user=request.user,
        menu_item=item,
        quantity=quantity,
        price_at_order=item.price,
    )

    return JsonResponse(
        {
            "success": True,
            "order_id": order.id,
            "item_name": item.name,
            "quantity": order.quantity,
            "total_price": str(order.total_price),
        }
    )


# ---------------------------------------------------------------------
# Contact form (plain POST + redirect, using Django messages)
# ---------------------------------------------------------------------

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks! Your message has been sent.")
        else:
            messages.error(request, "Please check the contact form and try again.")
    return redirect("/#contact")
