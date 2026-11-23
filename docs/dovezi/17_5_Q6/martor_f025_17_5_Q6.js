(blocaje) => {
  // Execută prin page.evaluate pe pagina reală, imediat după încărcarea controalelor.
  const fer = document.querySelector(".fereastra-overlay:not(.fundal) .fereastra");
  if (!fer || !fer.querySelector("#il-sem-blocaje")) throw Error("Nu s-au încărcat blocajele lunii");
  const text = (s) => (s || "").trim().replace(/\s+/g, " ");
  function lizibil(el) {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0 || r.left < -0.5 || r.top < -0.5 ||
        r.right > innerWidth + 0.5 || r.bottom > innerHeight + 0.5) return false;
    for (let p = el; p; p = p.parentElement) {
      const st = getComputedStyle(p);
      if (p.hidden || st.display === "none" || st.visibility !== "visible" || Number(st.opacity) === 0) return false;
      if (p === el) continue;
      const a = p.getBoundingClientRect(), x = a.left + p.clientLeft, y = a.top + p.clientTop;
      if (/hidden|scroll|auto|clip/.test(st.overflowY) && (r.top < y-0.5 || r.bottom > y+p.clientHeight+0.5)) return false;
      if (/hidden|scroll|auto|clip/.test(st.overflowX) && (r.left < x-0.5 || r.right > x+p.clientWidth+0.5)) return false;
    }
    const hit = document.elementFromPoint(r.left + r.width/2,r.top + r.height/2);
    return Boolean(hit && (el.contains(hit) || hit.contains(el)));
  }
  const grup = fer.querySelector("#il-sem-blocaje");
  const rows = Array.from(grup.querySelectorAll(".ds-semnal-cutie"));
  const rowFor = (b) => b && rows.find(row => {
    const label = row.querySelector(".ds-semnal-text");
    return label && text(label.title || label.textContent) === text(b.mesaj);
  });
  const reev = rowFor(blocaje.find(b => b.cod === "REEVALUARE_VALUTA"));
  const primul = rowFor(blocaje[0]);
  const buttons = [...fer.querySelectorAll('button,[role="button"]')].filter(b => text(b.getAttribute("aria-label") || b.textContent) === "Reevaluare valută");
  const unc = buttons.length === 1 ? buttons[0] : null;
  return {
    viewport:[innerWidth,innerHeight],
    butoane_total:buttons.length,
    butoane_rand:buttons.filter(b => reev && reev.contains(b)).length,
    butoane_fixe:buttons.filter(b => fer.querySelector("#il-controale")?.contains(b) && b.closest(".ds-actiuni-rand") && !grup.contains(b)).length,
    id_unic: Boolean(unc && unc.id === "il-reevaluare" && document.querySelectorAll("#il-reevaluare").length === 1),
    actionabil: Boolean(unc && !unc.disabled && unc.getAttribute("aria-disabled") !== "true"),
    buton_vizibil_initial:lizibil(unc),
    rand_reevaluare_vizibil_initial:lizibil(reev),
    primul_blocaj_vizibil_initial:lizibil(primul)
  };
}
