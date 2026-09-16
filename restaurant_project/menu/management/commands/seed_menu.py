from django.core.management.base import BaseCommand
from django.utils.text import slugify

from menu.models import MenuItem

VEG_ITEMS = [
    ("Chappathi", "chappathi.jpg", 50),
    ("Appam", "appam.jpg", 50),
    ("Curd Rice", "curd rice.jpg", 70),
    ("Dosai", "dosai.jpg", 50),
    ("Full Mills", "full mils2.png", 150),
    ("Idiyappam", "idiyappam2.png", 40),
    ("Idili", "idili2.png", 30),
    ("Lemon Rice", "leamon.png", 60),
    ("Mushroom Briyani", "mushroom briyani.jpg", 120),
    ("Poori", "puri.jpg", 50),
    ("Tomato Rice", "tomato rice.jpg", 60),
    ("Veg Briyani", "veg briyani.jpg", 100),
]

NON_VEG_ITEMS = [
    ("Chicken Briyani", "chiken briyani1.jpg", 180),
    ("Mutton Briyani", "mutun briyani.jpg", 200),
    ("Apollo Fish", "apollo fish.jpg", 170),
    ("Chettinad Chicken", "chiken_chettinad.jpg", 250),
    ("Chicken 65", "chiken65.jpg", 80),
    ("Goan Fish Curry", "goan_fish_curry.jpg", 140),
    ("Kasha Mangsho", "kasha_mangsho.jpg", 170),
    ("Rogan Josh", "ragan_josh.jpg", 160),
    ("Tandoori Chicken", "tandoori_chiken.jpg", 250),
]

DESCRIPTION = "Lorem ipsum dolor, sit amet consectetur adipisicing elit. Iure quae pariatu"


class Command(BaseCommand):
    help = "Seeds the database with the original restaurant menu items."

    def handle(self, *args, **options):
        created_count = 0

        for name, image, price in VEG_ITEMS:
            _, created = MenuItem.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "image": image,
                    "price": price,
                    "category": MenuItem.VEG,
                    "description": DESCRIPTION,
                },
            )
            created_count += int(created)

        for name, image, price in NON_VEG_ITEMS:
            _, created = MenuItem.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "image": image,
                    "price": price,
                    "category": MenuItem.NON_VEG,
                    "description": DESCRIPTION,
                },
            )
            created_count += int(created)

        self.stdout.write(self.style.SUCCESS(f"Seeded menu items. {created_count} new item(s) created."))
