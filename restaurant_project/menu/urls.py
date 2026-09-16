from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/login/", views.login_view, name="login"),
    path("api/signup/", views.signup_view, name="signup"),
    path("api/logout/", views.logout_view, name="logout"),
    path("api/favorite/<int:item_id>/toggle/", views.toggle_favorite, name="toggle_favorite"),
    path("api/order/", views.place_order, name="place_order"),
    path("contact/", views.contact_view, name="contact"),
]
