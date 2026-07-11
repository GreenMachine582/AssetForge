// Filter-bar helper: maintains the filter-count badge and wires the
// clear-all button. HTMX's own hx-push-url already keeps the URL in sync
// when filters change; this only handles the reverse (URL -> form on load
// is handled server-side by pre-filling field values from the querystring).
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("[data-filters-form]");
    if (!form) return;

    function updateBadge() {
        const params = new URLSearchParams(new FormData(form));
        let count = 0;
        for (const value of params.values()) {
            if (value) count++;
        }
        const badge = document.getElementById("filter-count-badge");
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count + (count === 1 ? " filter" : " filters");
            badge.classList.remove("d-none");
        } else {
            badge.classList.add("d-none");
        }
    }

    form.addEventListener("change", updateBadge);
    updateBadge();

    const clearBtn = document.getElementById("clear-filters-btn");
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            window.location.href = "/assets";
        });
    }
});
