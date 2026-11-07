// Script de unică folosință (17.3, pct.2 d): starea ferestrei de sus cu formularul deschis — „←” activ?, „Renunță” în bară?, al cui?
(() => {
  const toate = [...document.querySelectorAll(".fereastra")];
  const F = toate[toate.length - 1];
  if (!F) return { fereastra: false };
  const norm = (t) => (t || "").replace(/\s+/g, " ").trim();
  const sageata = F.querySelector(".nav-inapoi");
  const bara = F.querySelector(".fereastra-jos");
  const renunta = bara ? [...bara.querySelectorAll("button")].filter((x) => norm(x.innerText) === "Renunță") : [];
  return {
    fereastra: true,
    titlu: norm((F.querySelector(".fir-acum") || {}).textContent),
    ferestre: toate.length,
    are_sageata: !!sageata && getComputedStyle(sageata).display !== "none",
    cu_formular: !!bara && bara.dataset.cuFormular === "1",
    renunta_in_bara: renunta.length,
    renunta_al_ecranului: renunta.some((x) => x.classList.contains("fj-al-ecranului")),
  };
})()
