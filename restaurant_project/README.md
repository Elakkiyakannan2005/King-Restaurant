# Authentic Indian Restaurant — Django Backend

This wires your original static `restaurant.html / .css / .js` site up to a
real Django backend: a database-driven menu, user accounts, per-user
favorites, order placement/history, and a contact form — all manageable
from the Django admin.

## What changed vs. the static version

| Feature | Before | Now |
|---|---|---|
| Menu items | hard-coded in HTML | `MenuItem` model, editable in `/admin/` |
| Login / Sign up | fake card, no backend | real Django auth (`django.contrib.auth`), AJAX |
| Favorites (heart icon) | CSS class toggle only, lost on refresh | `Favorite` model, persisted per user |
| "My Orders" tab | not wired up | `Order` model, created when you click "Order Now" |
| Contact form | did nothing | saved to `ContactMessage`, viewable in admin |

The page is still a single page (`menu/templates/menu/index.html`) — tabs,
the preview/order popup, and the login card all still work exactly like
before, just backed by real data now instead of hard-coded markup.

## Project layout

```
restaurant_project/
├── manage.py
├── requirements.txt
├── restaurant_project/       # Django project (settings, urls)
└── menu/                     # Django app
    ├── models.py              # MenuItem, Favorite, Order, ContactMessage
    ├── views.py                # page + AJAX endpoints
    ├── urls.py
    ├── admin.py
    ├── forms.py                # SignUpForm, ContactForm
    ├── management/commands/seed_menu.py   # loads your original 21 dishes
    ├── templates/menu/         # index.html + _card.html partial
    └── static/menu/
        ├── restaurant.css      # your original CSS + a few additions
        ├── restaurant.js       # updated to call the Django API
        └── images/             # <-- put your dish/background/logo images here
```

## 1. Install & set up

```bash
cd restaurant_project
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_menu      # loads the 21 dishes from your original site
python manage.py createsuperuser
```

## 2. Add your images

The original project referenced images (`background.jpg`, `logo.png`,
`chappathi.jpg`, etc.) that weren't part of the files you uploaded. Copy
all of your image/video assets into:

```
menu/static/menu/images/
```

using the **same filenames** referenced in `menu/management/commands/seed_menu.py`
and `menu/templates/menu/index.html`. If a dish's image filename differs,
either rename the file or update the `image` value for that `MenuItem` in
the Django admin (`/admin/menu/menuitem/`).

## 3. Run it

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

## How the moving parts work

- **Auth** — `POST /api/login/` and `POST /api/signup/` are called via
  `fetch()` from the login/sign-up card and return JSON. `POST /api/logout/`
  logs you out. All use Django's built-in `django.contrib.auth` (secure
  password hashing, sessions, CSRF).
- **Favorites** — clicking a heart calls `POST /api/favorite/<item_id>/toggle/`,
  which creates/deletes a `Favorite` row for the logged-in user. Requires
  login (you'll be prompted to log in if you're not).
- **Orders** — clicking "Order Now" in a preview popup calls
  `POST /api/order/` with `{item_id, quantity}`, creating an `Order` row.
  The "My Orders" tab lists all of the current user's past orders.
- **Contact form** — a normal (non-AJAX) POST to `/contact/`, saved as a
  `ContactMessage`, viewable in the admin.
- **Menu admin** — add, edit, or disable dishes at
  `/admin/menu/menuitem/` without touching any code.

## Notes / next steps

- `SECRET_KEY` in `settings.py` is a placeholder — replace it (and set
  `DEBUG = False`, a real `ALLOWED_HOSTS`, and a production database) before
  deploying.
- The DB is SQLite for simplicity; swap the `DATABASES` setting for
  Postgres/MySQL in production.
- Orders currently store one dish per order row (matching the original
  UI, which orders one dish at a time via its own popup). If you'd like a
  proper multi-item shopping cart + checkout instead, that's a
  straightforward follow-up (an `Order` + `OrderItem` model split).
