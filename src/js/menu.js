// Mobile navigation: toggle the nav list open/closed when the hamburger is tapped.
// The `.active` class is styled in styles/site.css (@media max-width: 768px).
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector(".menu-toggle");
  var navList = document.querySelector("header nav ul");
  if (!toggle || !navList) return;

  toggle.addEventListener("click", function () {
    navList.classList.toggle("active");
  });

  // Close the menu after a link is chosen.
  navList.addEventListener("click", function (e) {
    if (e.target.tagName === "A") navList.classList.remove("active");
  });
});
