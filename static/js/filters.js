// Filter-bar helper: maintains the filter-count badge and wires the
// clear-all button. URL sync (pushState) and re-fetching table data on
// filter change are handled by the inline script in assets.html; form
// fields are pre-filled on load server-side from the querystring.
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
