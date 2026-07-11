// Fetches a text/markdown endpoint and copies its body to the clipboard,
// with a brief confirmation on the triggering button.
async function copyEndpointToClipboard(url, buttonEl) {
    const original = buttonEl.textContent;
    try {
        const response = await fetch(url);
        const text = await response.text();
        await navigator.clipboard.writeText(text);
        buttonEl.textContent = "Copied!";
    } catch (err) {
        buttonEl.textContent = "Copy failed";
    } finally {
        setTimeout(function () {
            buttonEl.textContent = original;
        }, 1500);
    }
}
