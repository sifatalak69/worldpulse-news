
const languageBtn = document.getElementById("languageBtn");

let currentLanguage = "en";

languageBtn.addEventListener("click", function () {
    currentLanguage = currentLanguage === "en" ? "bn" : "en";

    document.documentElement.lang = currentLanguage;

    document.querySelectorAll("[data-en][data-bn]")
        .forEach(function (element) {
            element.textContent =
                currentLanguage === "bn"
                    ? element.dataset.bn
                    : element.dataset.en;
        });

    languageBtn.textContent =
        currentLanguage === "bn" ? "English" : "বাংলা";

    const searchInput = document.querySelector(
        '.search-form input[name="q"]'
    );

    searchInput.placeholder =
        currentLanguage === "bn"
            ? "খবর খুঁজুন..."
            : "Search news...";
});
