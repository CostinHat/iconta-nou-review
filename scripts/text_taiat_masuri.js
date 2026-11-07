// Detectorul de text tăiat (comanda 17.2-B): se evaluează în pagină (pg.evaluate), după ce ecranul e deschis; măsoară ultima fereastră de lucru (antet, corp,
// bară de jos) și întoarce {taiate, numar, numar_fara_proba, ferestre}. Trei tipuri: „lat” (overflow-x hidden/clip sau ellipsis, scrollWidth > clientWidth),
// „inalt” (overflow-y hidden/clip, scrollHeight > clientHeight), „iesit” (textul propriu iese orizontal din strămoșul care taie sau din ecran).
// Fără excepții scrise aici: orice abatere rămâne în numărătoare.
(() => {
  const toate = [...document.querySelectorAll(".fereastra")];
  const F = toate[toate.length - 1] || null;
  const taiate = [];
  const rezultat = () => ({ taiate, numar: taiate.length, numar_fara_proba: taiate.filter((t) => !t.proba).length, ferestre: toate.length });
  if (!F) return rezultat();
  const norm = (t) => (t || "").replace(/\s+/g, " ").trim();
  // copiate identic din scripts/verificator_design_masuri.js (inDetaliiInchise, vizibil): un element dintr-un <details> închis nu e la vedere
  const inDetaliiInchise = (el) => { const d = el.closest("details:not([open])"); return !!d && !el.closest("summary"); };
  const vizibil = (el) => !!(el.offsetParent || el.getClientRects().length) && getComputedStyle(el).visibility !== "hidden" && !inDetaliiInchise(el);
  const ascuns = (el) => !(el instanceof HTMLElement) || ["SCRIPT", "STYLE", "NOSCRIPT"].includes(el.tagName) || !!el.closest("[hidden], .sr-only")
    || !vizibil(el) || el.getBoundingClientRect().width === 0;
  const areText = (el) => norm(el.textContent) !== "";
  const textPropriu = (el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim() !== "");
  const taie = (v) => v === "hidden" || v === "clip";
  const selector = (el) => {
    const c = (typeof el.className === "string" ? el.className.trim().split(/\s+/)[0] : "") || "";
    return (el.tagName.toLowerCase() + (c ? "." + c : "") + (el.id ? "#" + el.id : "")).slice(0, 60);
  };
  const intrare = (tip, el, w, sw, h, sh) => ({ tip, selector: selector(el), text: norm(el.innerText || el.textContent).slice(0, 30), w: Math.round(w), sw: Math.round(sw),
    h: Math.round(h), sh: Math.round(sh), proba: el.hasAttribute("data-proba-17-2-b") });
  const elemente = [F, ...F.querySelectorAll("*")].filter((el) => !ascuns(el));

  // (c) iesit: textul propriu al elementului iese din strămoșul cel mai apropiat cu overflow-x hidden/clip sau din ecran; un strămoș auto/scroll între ele = conținut derulat
  const iesit = new Map();   // element -> strămoșul care taie
  for (const el of elemente) {
    if (!textPropriu(el)) continue;
    let taietor = null, derulat = false;
    // un element fixed nu e tăiat de niciun strămoș; unul absolute e tăiat numai de blocul lui de conținut (offsetParent) și de strămoșii acestuia
    const pozitie = getComputedStyle(el).position;
    let p = pozitie === "fixed" ? null : el.parentElement;
    if (pozitie === "absolute") while (p && p !== el.offsetParent) p = p.parentElement;
    for (; p; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === "auto" || ox === "scroll") { derulat = true; break; }
      if (!taietor && taie(ox)) taietor = p;
    }
    if (derulat && !taietor) continue;
    const r = el.getBoundingClientRect();
    let afara = false;
    if (taietor) {
      const rt = taietor.getBoundingClientRect();
      afara = r.right > rt.right + 1 || r.left < rt.left - 1;
    }
    if (!derulat && r.right > innerWidth + 1) afara = true;
    if (!afara) continue;
    iesit.set(el, taietor);
    taiate.push(intrare("iesit", el, taietor ? taietor.clientWidth : innerWidth, taietor ? r.right - taietor.getBoundingClientRect().left : r.right, el.clientHeight, el.scrollHeight));
  }

  // un strămoș cu overflow ascuns nu se numără la „lat” dacă depășirea lui vine numai din descendenți numărați la „iesit” (același caz nu se numără de două ori)
  const explicat = (el) => {
    const ies = [...iesit].filter(([, t]) => t === el).map(([d]) => d);
    if (!ies.length) return false;
    const rt = el.getBoundingClientRect();
    for (const d of el.querySelectorAll("*")) {
      if (ascuns(d)) continue;
      const r = d.getBoundingClientRect();
      if ((r.right > rt.right + 1 || r.left < rt.left - 1) && !(iesit.has(d) || ies.some((i) => d.contains(i)) || !areText(d))) return false;
    }
    return true;
  };

  for (const el of elemente) {
    if (!areText(el)) continue;
    const cs = getComputedStyle(el);
    // (a) lat
    if (el.scrollWidth > el.clientWidth + 1 && (taie(cs.overflowX) || cs.textOverflow === "ellipsis") && !explicat(el))
      taiate.push(intrare("lat", el, el.clientWidth, el.scrollWidth, el.clientHeight, el.scrollHeight));
    // (b) inalt
    if (el.scrollHeight > el.clientHeight + 1 && taie(cs.overflowY))
      taiate.push(intrare("inalt", el, el.clientWidth, el.scrollWidth, el.clientHeight, el.scrollHeight));
  }
  return rezultat();
})()
