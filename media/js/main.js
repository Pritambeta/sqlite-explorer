function showAlert(message, color) {
    let elem = document.createElement("div");
    elem.setAttribute("class", "alertbox");
    elem.classList.add(`alert-${color}`);
    elem.innerHTML = `
    <p class="alerttext">${message}</p>
    <span class="alertclose" onclick="document.body.removeChild(this.parentNode)">&times;</span>
    `;
    window.alertBox = elem;
    document.body.appendChild(elem);
    setTimeout(() => {
        document.body.removeChild(elem);
    }, 4000);
}

function copyText(button, selector) {
    button.innerHTML = "Copied!";
    let value = document.querySelector(selector).value;
    let textarea = document.createElement("textarea");
    textarea.innerHTML = value;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    setTimeout(() => {
        button.innerHTML = "Copy"
    }, 2000);
}
function clearText(selector) {
    document.querySelector(selector).value = "";
}

function parseText(string) {
    return string.replaceAll("'", "&apos;");
}
function refreshData() {
    fetch("/~refresh");
}