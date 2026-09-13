(() => {
  const root = document.documentElement;
  const themeKey = "infractl-theme";
  const saved = localStorage.getItem(themeKey);
  root.dataset.theme = (saved === "light" || saved === "dark") ? saved : "dark";

  const theme = document.querySelector("#theme-toggle");
  if (theme) {
    theme.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem(themeKey, next);
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

  /*
   * Sidebar navigation is a recursive tree. A node may contain children at any
   * depth, so structures such as Web Servers > Nginx > Security > TLS work
   * without adding new CSS classes for every level.
   */
  const navigation = window.INFRACTL_NAV || [];


  const sidebar = document.querySelector(".sidebar");
  const script = document.currentScript || [...document.scripts].find((s) => /\/assets\/app\.js(?:\?|$)/.test(s.src));
  const siteRoot = script ? new URL("../", script.src) : new URL("/", location.href);
  const iconSprite = new URL("assets/icons.svg", siteRoot).href;
  const openKey = "infractl-nav-open";
  let rememberedOpen = new Set();

  try {
    rememberedOpen = new Set(JSON.parse(localStorage.getItem(openKey) || "[]"));
  } catch (_) {
    rememberedOpen = new Set();
  }

  const normalizePath = (value) => {
    const path = new URL(value, location.href).pathname.replace(/\/index\.html$/, "/");
    return path.endsWith("/") ? path : `${path}/`;
  };

  const currentPath = normalizePath(location.href);
  const hrefFor = (href) => new URL(href || "./", siteRoot).href;
  const nodePath = (node) => normalizePath(hrefFor(node.href));
  const isExactActive = (node) => currentPath === nodePath(node);
  const hasActiveDescendant = (node) => (node.children || []).some((child) => isExactActive(child) || hasActiveDescendant(child));

  const persistOpenState = () => {
    try { localStorage.setItem(openKey, JSON.stringify([...rememberedOpen])); } catch (_) {}
  };

  const makeIcon = (name, color) => {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", `side-icon ${color || ""}`.trim());
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `${iconSprite}#${name || "note"}`);
    svg.appendChild(use);
    return svg;
  };

  const renderNode = (node, depth = 0) => {
    const wrapper = document.createElement("div");
    wrapper.className = "side-node";
    wrapper.style.setProperty("--depth", depth);

    const row = document.createElement("div");
    row.className = "side-row";
    const children = node.children || [];
    const hasChildren = children.length > 0;
    const id = node.href || `${node.label}-${depth}`;
    const exactActive = isExactActive(node);
    const activeBelow = hasActiveDescendant(node);

    if (hasChildren) {
      const toggle = document.createElement("button");
      toggle.className = "side-toggle";
      toggle.type = "button";
      toggle.setAttribute("aria-label", `Toggle ${node.label}`);

      const shouldOpen = activeBelow || exactActive || rememberedOpen.has(id);
      wrapper.classList.toggle("expanded", shouldOpen);
      toggle.setAttribute("aria-expanded", String(shouldOpen));
      toggle.innerHTML = '<span class="side-chevron">›</span>';
      toggle.addEventListener("click", () => {
        const next = !wrapper.classList.contains("expanded");
        wrapper.classList.toggle("expanded", next);
        toggle.setAttribute("aria-expanded", String(next));
        if (next) rememberedOpen.add(id); else rememberedOpen.delete(id);
        persistOpenState();
      });
      row.appendChild(toggle);
    } else {
      const spacer = document.createElement("span");
      spacer.className = "side-toggle-spacer";
      row.appendChild(spacer);
    }

    const link = document.createElement("a");
    link.className = "side-link";
    if (exactActive) link.classList.add("active");
    if (activeBelow) link.classList.add("ancestor-active");
    link.href = hrefFor(node.href);
    link.appendChild(makeIcon(node.icon, node.color));
    const text = document.createElement("span");
    text.textContent = node.label;
    link.appendChild(text);
    row.appendChild(link);
    wrapper.appendChild(row);

    if (hasChildren) {
      const branch = document.createElement("div");
      branch.className = "side-children";
      children.forEach((child) => branch.appendChild(renderNode(child, depth + 1)));
      wrapper.appendChild(branch);
    }

    return wrapper;
  };

  if (sidebar) {
    sidebar.replaceChildren();

    const home = document.createElement("a");
    home.className = "side-home";
    home.href = hrefFor("");
    home.innerHTML = "⌂ <span>Home</span>";
    if (currentPath === normalizePath(home.href)) home.classList.add("active");
    sidebar.appendChild(home);

    navigation.forEach((entry) => {
      if (entry.group) {
        const heading = document.createElement("div");
        heading.className = "side-group";
        heading.textContent = entry.group;
        sidebar.appendChild(heading);
        (entry.items || []).forEach((node) => sidebar.appendChild(renderNode(node)));
      } else {
        sidebar.appendChild(renderNode(entry));
      }
    });
  }
})();


function initCodeCopyButtons() {
  document.querySelectorAll(".doc pre").forEach((pre) => {
    if (pre.querySelector(".code-copy")) return;

    const button = document.createElement("button");

    button.className = "code-copy";
    button.type = "button";
    button.setAttribute("aria-label", "Copy code");

    button.innerHTML = `
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <rect x="9" y="9" width="13" height="13" rx="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span>Copy</span>
    `;

    button.addEventListener("click", async () => {
      const code = pre.querySelector("code");
      const text = code ? code.innerText : pre.innerText;

      try {
        await navigator.clipboard.writeText(text);

        button.classList.add("copied");
        button.querySelector("span").textContent = "Copied";

        setTimeout(() => {
          button.classList.remove("copied");
          button.querySelector("span").textContent = "Copy";
        }, 1500);
      } catch (error) {
        console.error("Failed to copy code:", error);
      }
    });

    pre.appendChild(button);
  });
}

document.addEventListener("DOMContentLoaded", initCodeCopyButtons);