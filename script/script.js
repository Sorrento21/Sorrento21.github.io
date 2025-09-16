// script.js
document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector("header nav ul");

    menuToggle.addEventListener("click", function() {
        navLinks.classList.toggle("active");
    });
});
