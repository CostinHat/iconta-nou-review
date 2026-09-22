---
title: Corectarea diferențelor de stoc constatate la inventar
description: Diferențele de stoc nu se înregistrează direct ca plus sau minus — întâi se verifică dacă se pot compensa (OMFP 2861/2009 pct. 40) și dacă se aplică scăzăminte legale (pct. 41), iar minusul imputabil rămas se recuperează la valoarea de înlocuire, nu prin TVA colectată.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez diferențele de stoc constatate la inventarul anual?

Aproape orice inventar anual scoate la iveală diferențe: un sortiment lipsește, altul e în plus, uneori pe aceeași gestiune și în aceeași perioadă. Greșeala frecventă e să tratezi fiecare diferență separat, ca minus sau plus definitiv, fără să verifici întâi dacă legea permite compensarea lor sau aplicarea unor scăzăminte. Ordinea contează, pentru că schimbă atât suma imputabilă, cât și înregistrările contabile.

## Temeiul legal

::: ghid-temei
**OMFP 2861/2009, Anexă, pct. 40** — evaluare și compensare:

Alin. (1)-(2): *„40. - (1) În situația constatării unor plusuri în gestiune, bunurile respective se evaluează potrivit reglementărilor contabile aplicabile. (2) În cazul constatării unor lipsuri imputabile în gestiune, administratorii trebuie să impute persoanelor vinovate bunurile lipsă la valoarea lor de înlocuire."*

Alin. (3): *„La stabilirea valorii debitului, în cazurile în care lipsurile în gestiune nu sunt considerate infracțiuni, se are în vedere posibilitatea compensării lipsurilor cu eventualele plusuri constatate, dacă sunt îndeplinite următoarele condiții: - să existe riscul de confuzie între sorturile aceluiași bun material...; - diferențele constatate în plus sau în minus să se refere la aceeași perioadă de gestiune și la aceeași gestiune."*

Alin. (4): *„Nu se admite compensarea în cazurile în care s-a făcut dovada că lipsurile constatate la inventariere provin din sustragerea sau din degradarea bunurilor respective datorată vinovăției persoanelor care răspund de gestionarea acestor bunuri."*

Alin. (5): *„Listele cu sorturile de produse, mărfuri, ambalaje și alte valori materiale care întrunesc condițiile de compensare datorită riscului de confuzie se aprobă anual de către administratori... Compensarea se face pentru cantități egale între plusurile și lipsurile constatate."*

**OMFP 2861/2009, Anexă, pct. 41 alin. (1) și (3)** — scăzăminte: se calculează *„numai în situația în care cantitățile lipsă sunt mai mari decât cantitățile constatate în plus"*, aplicate întâi pe bunurile cu lipsuri; *„Pentru pagubele constatate în gestiune răspund persoanele vinovate de producerea lor. Imputarea acestora se face la valoarea de înlocuire."*
:::

## Ordinea corectă de tratare a diferențelor

**Pasul 1 — verifici dacă se poate compensa.** Compensarea plus-minus e permisă doar dacă sunt îndeplinite cumulativ condițiile de la pct. 40 alin. (3): risc de confuzie între sorturile aceluiași bun, aceeași gestiune, aceeași perioadă de gestiune, iar sortimentele eligibile figurează pe o listă aprobată anual de administratori (alin. 5). Compensarea se face pentru **cantități egale**, eliminând diferența începând cu sorturile cu prețurile unitare cele mai scăzute. Dacă lipsa vine dovedit din sustragere sau degradare imputabilă, compensarea e interzisă (alin. 4), oricât de asemănătoare ar fi sorturile.

**Pasul 2 — aplici scăzămintele legale**, dar numai pe ce rămâne necompensat și numai dacă lipsa cantitativă depășește plusul: scăzămintele se scad întâi din lipsurile constatate, în limitele legale ale bunului respectiv.

**Pasul 3 — înregistrezi ce rămâne.** Plusul rămas se evaluează potrivit reglementărilor contabile aplicabile și intră în gestiune. Minusul rămas se descarcă din gestiune la valoarea contabilă (`60x = 3xx`, de exemplu `607 = 371` pentru mărfuri), iar dacă e imputabil, valoarea de înlocuire recuperată de la vinovat se înregistrează separat, prin `4282 = 7581` (salariat) sau `461 = 7581` (terț).

## TVA la minusul care rămâne imputabil

Valoarea de înlocuire, potrivit pct. 40 alin. (2), include și TVA — dar asta nu înseamnă că imputarea generează TVA colectată în contabilitate. Legea taxei tratează separat cele două lucruri: imputarea unei sume bănești către gestionar nu e o livrare, deci nu intră în sfera TVA; în schimb, lipsa bunului din gestiune poate declanșa o ajustare a TVA deductibile deja exercitate la achiziție, indiferent dacă lipsa e sau nu imputată. Detaliem exact acest mecanism, cu toate excepțiile, în ghidul dedicat descărcării de gestiune pentru lipsuri.

## Ce se greșește în practică

- **Se înregistrează minusul direct, fără să se verifice compensarea.** Dacă sortimentele îndeplinesc condițiile de la pct. 40 alin. (3) și figurează pe lista aprobată anual, o parte din lipsă trebuie compensată cu plusul, nu imputată integral.
- **Se scad scăzămintele înainte de a determina corect minusul net**, sau se aplică pe bunuri care de fapt sunt în plus — scăzămintele se calculează doar pe partea de lipsă care depășește plusul, conform pct. 41 alin. (1).
- **Se pune TVA colectată pe suma imputată gestionarului**, tratând-o ca pe o vânzare. Imputarea unei sume bănești nu e o operațiune în sfera TVA.

## Ce face iConta.eu

Modulul de inventariere calculează plusurile și minusurile cantitativ-valorice pe fiecare sortiment din listele de inventariere și generează notele contabile de descărcare de gestiune (`60x = 3xx`) la valoarea contabilă pentru minusuri. Regula de compensare plus-minus (sortimente confundabile, aceeași gestiune și perioadă, listă aprobată anual) și aplicarea scăzămintelor legale nu sunt calculate automat de acest modul — valorile finale de plus și de minus trebuie stabilite, conform pct. 40, înainte de a fi introduse în aplicație.

[iConta.eu](/)
