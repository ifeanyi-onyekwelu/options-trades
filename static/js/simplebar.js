(function () {
  "use strict";

  // Initialize SimpleBar for custom scrollbar
  var myElement = document.getElementById("sidebar-scroll");
  if (myElement) {
    new SimpleBar(myElement, {
      autoHide: true,
    });
  }

  // Sidebar submenu toggle logic
  document.addEventListener("DOMContentLoaded", function () {
    const subMenus = document.querySelectorAll(".slide.has-sub");

    subMenus.forEach((menu) => {
      const menuItem = menu.querySelector(".side-menu__item");
      menuItem.addEventListener("click", function (e) {
        e.preventDefault();

        // Toggle open class
        menu.classList.toggle("open");

        // Find submenu and toggle visibility
        const subMenu = menu.querySelector(".slide-menu");
        if (menu.classList.contains("open")) {
          subMenu.style.display = "block";
        } else {
          subMenu.style.display = "none";
        }
      });
    });
  });
})();
