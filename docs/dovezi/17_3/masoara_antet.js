// Script de unică folosință (17.3, pct.2 c): bara de sus a ferestrei la 603×590 — placeholderul căutării, calea întreagă din `title`, `scrollWidth <= clientWidth` pe .fereastra-fir, înălțimea barei
(() => {
  const toate = [...document.querySelectorAll(".fereastra")]; const F = toate[toate.length - 1];
  const ant = F.querySelector(".fereastra-antet"), fir = F.querySelector(".fereastra-fir"), cauta = F.querySelector("input.cautare-camp");
  const vizibil = (e) => !!(e.offsetParent || e.getClientRects().length);
  return { latime_fereastra: innerWidth, antet_px: Math.round(ant.getBoundingClientRect().height), placeholder: cauta ? cauta.placeholder : null,
    fir_scrollWidth: fir.scrollWidth, fir_clientWidth: fir.clientWidth, fir_incape: fir.scrollWidth <= fir.clientWidth,
    segmente_vizibile: [...fir.children].filter(vizibil).map((x) => x.className + ": " + x.textContent.trim()), cale_intreaga_in_title: fir.title,
    fir_inaltime_px: Math.round(fir.getBoundingClientRect().height) };
})()
