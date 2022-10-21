const navbar = document.querySelector(".nav__link");
const menuBtn = document.querySelector("#mobileMenu");
const mobileMenu = document.querySelector(".mobile-menu-links");

menuBtn.addEventListener("click", function () {
  mobileMenu.classList.toggle("hide");
});

window.addEventListener("resize", function () {
  if (window.innerWidth > 768) {
    mobileMenu.classList.add("hide");
  }
});
