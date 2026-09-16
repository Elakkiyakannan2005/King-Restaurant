// ---------------------------------------------------------------------
// CSRF helper (Django convention: read the csrftoken cookie and send it
// back as the X-CSRFToken header on every POST fetch call)
// ---------------------------------------------------------------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const CSRF_TOKEN = () => getCookie("csrftoken");

async function postJSON(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRF_TOKEN(),
        },
        body: JSON.stringify(data || {}),
    });
    let payload = {};
    try {
        payload = await response.json();
    } catch (e) {
        // non-JSON response
    }
    return { ok: response.status, ...payload };
}

async function postForm(url, formEl) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": CSRF_TOKEN() },
        body: new FormData(formEl),
    });
    let payload = {};
    try {
        payload = await response.json();
    } catch (e) {
        // non-JSON response
    }
    payload._status = response.status;
    return payload;
}

// ---------------------------------------------------------------------
// Product preview popups
// ---------------------------------------------------------------------
let previewContainer = document.querySelector(".products-preview");
let previewBox = previewContainer.querySelectorAll(".preview");

document.querySelectorAll(".tab-container .cards .details").forEach(details => {
    details.onclick = () => {
        previewContainer.style.display = "flex";
        let name = details.getAttribute("data-name");

        previewBox.forEach(preview => {
            preview.classList.remove("active");
            let target = preview.getAttribute("data-target");
            if (name == target) {
                preview.classList.add("active");
            }
        });
    };
});

// close preview
previewBox.forEach(close => {
    close.querySelector(".fa-solid").onclick = () => {
        close.classList.remove("active");
        previewContainer.style.display = "none";
    };
});

// ---------------------------------------------------------------------
// Login / Sign up card
// ---------------------------------------------------------------------
function openLoginCard(event) {
    if (event) event.preventDefault();
    document.getElementById("login-card").classList.add("active");
}

function closeLoginCard() {
    document.getElementById("login-card").classList.remove("active");
}

function showSignupForm(event) {
    if (event) event.preventDefault();
    document.getElementById("login-form").style.display = "none";
    document.getElementById("signup-form").style.display = "block";
}

function showLoginForm(event) {
    if (event) event.preventDefault();
    document.getElementById("signup-form").style.display = "none";
    document.getElementById("login-form").style.display = "block";
}

async function handleLogin(event) {
    event.preventDefault();
    const form = document.getElementById("login-form");
    const errorBox = document.getElementById("login-error");
    errorBox.style.display = "none";

    const result = await postForm(API_URLS.login, form);

    if (result.success) {
        window.location.reload();
    } else {
        errorBox.textContent = result.message || "Login failed. Please check your details.";
        errorBox.style.display = "block";
    }
}

async function handleSignup(event) {
    event.preventDefault();
    const form = document.getElementById("signup-form");
    const errorBox = document.getElementById("signup-error");
    errorBox.style.display = "none";

    const result = await postForm(API_URLS.signup, form);

    if (result.success) {
        window.location.reload();
    } else {
        const errors = result.errors
            ? Object.values(result.errors).map(e => e.map(x => x.message).join(" ")).join(" ")
            : "Sign up failed. Please check your details.";
        errorBox.textContent = errors;
        errorBox.style.display = "block";
    }
}

async function handleLogout(event) {
    if (event) event.preventDefault();
    await postJSON(API_URLS.logout, {});
    window.location.reload();
}

// ---------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------
function show_tab(id, element) {
    document.querySelectorAll(".tab-container").forEach(container => {
        container.classList.remove("active");
    });
    document.querySelectorAll(".tab").forEach(tab => {
        tab.classList.remove("active");
    });

    document.getElementById(id).classList.add("active");
    element.classList.add("active");
}

// ---------------------------------------------------------------------
// Orders
// ---------------------------------------------------------------------
async function order_submit(itemId) {
    const isAuthenticated = document.body.getAttribute("data-authenticated") === "true";
    if (!isAuthenticated) {
        alert("Please log in to place an order.");
        openLoginCard();
        return;
    }

    const qtyInput = document.getElementById(`qty-${itemId}`);
    const quantity = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;

    const result = await postJSON(API_URLS.placeOrder, { item_id: itemId, quantity });

    if (result.success) {
        alert(`Order placed: ${result.item_name} x${result.quantity} — Rs.${result.total_price}`);
        window.location.reload(); // refresh so "My Orders" tab shows the new order
    } else {
        alert(result.message || "Could not place the order. Please try again.");
    }
}

// ---------------------------------------------------------------------
// Favorites (heart icon)
// ---------------------------------------------------------------------
async function toggleHeart(button, itemId) {
    const isAuthenticated = document.body.getAttribute("data-authenticated") === "true";
    if (!isAuthenticated) {
        alert("Please log in to save favorites.");
        openLoginCard();
        return;
    }

    const url = `/api/favorite/${itemId}/toggle/`;
    const result = await postJSON(url, {});

    if (!result.success) {
        alert(result.message || "Could not update favorites.");
        return;
    }

    const heart = button.querySelector("i");
    if (result.is_favorite) {
        button.classList.add("active");
        heart.classList.remove("fa-regular");
        heart.classList.add("fa-solid");
    } else {
        button.classList.remove("active");
        heart.classList.remove("fa-solid");
        heart.classList.add("fa-regular");
    }
}
