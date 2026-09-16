from django.conf import settings
from django.db import models
from django.templatetags.static import static


class MenuItem(models.Model):
    VEG = "veg"
    NON_VEG = "non-veg"
    CATEGORY_CHOICES = [
        (VEG, "Veg"),
        (NON_VEG, "Non-Veg"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default=VEG)

    # Points at a filename inside menu/static/menu/images/, e.g. "chappathi.jpg"
    # Kept as a plain field (rather than ImageField) so the existing static
    # image files from the original front-end project can be reused as-is.
    image = models.CharField(max_length=200, help_text="Filename inside menu/static/menu/images/")

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        return static(f"menu/images/{self.image}")


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "menu_item")

    def __str__(self):
        return f"{self.user} \u2665 {self.menu_item}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_price(self):
        return self.price_at_order * self.quantity

    def __str__(self):
        return f"Order #{self.pk} - {self.menu_item} x{self.quantity} ({self.user})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
