(() => {
  const root = document.documentElement;
  const key = "infractl-theme";
  const saved = localStorage.getItem(key);
  root.dataset.theme = (saved === "light" || saved === "dark") ? saved : "dark";

  const theme = document.querySelector("#theme-toggle");
  if (theme) {
    theme.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem(key, next);
    });
  }

  const menu = document.querySelector("#menu-toggle");
  if (menu) {
    menu.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      document.querySelector(".sidebar")?.classList.toggle("open");
    });
  }
})();
