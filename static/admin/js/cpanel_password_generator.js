(function () {
  function randomFromCharset(length, charset) {
    var result = "";
    var cryptoObj = window.crypto || window.msCrypto;

    if (cryptoObj && cryptoObj.getRandomValues) {
      var values = new Uint32Array(length);
      cryptoObj.getRandomValues(values);
      for (var i = 0; i < length; i += 1) {
        result += charset[values[i] % charset.length];
      }
      return result;
    }

    for (var j = 0; j < length; j += 1) {
      result += charset[Math.floor(Math.random() * charset.length)];
    }
    return result;
  }

  function generateSecurePassword() {
    var upper = "ABCDEFGHJKLMNPQRSTUVWXYZ";
    var lower = "abcdefghijkmnopqrstuvwxyz";
    var digits = "23456789";
    var symbols = "!@#$%^&*()-_=+[]{}";
    var all = upper + lower + digits + symbols;

    var password = [
      randomFromCharset(1, upper),
      randomFromCharset(1, lower),
      randomFromCharset(1, digits),
      randomFromCharset(1, symbols),
      randomFromCharset(12, all),
    ].join("");

    return password
      .split("")
      .sort(function () {
        return Math.random() - 0.5;
      })
      .join("");
  }

  function attachButton(inputId, buttonText) {
    var input = document.getElementById(inputId);
    if (!input || input.dataset.generatorAttached === "1") {
      return;
    }

    input.dataset.generatorAttached = "1";

    var button = document.createElement("button");
    button.type = "button";
    button.className = "button";
    button.textContent = buttonText;
    button.style.marginLeft = "8px";
    button.style.verticalAlign = "middle";

    button.addEventListener("click", function () {
      input.value = generateSecurePassword();
      input.focus();
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });

    input.insertAdjacentElement("afterend", button);
  }

  function init() {
    attachButton("id_cpanel_password", "Generar segura");
    attachButton("id_cpanel_new_password", "Generar segura");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
