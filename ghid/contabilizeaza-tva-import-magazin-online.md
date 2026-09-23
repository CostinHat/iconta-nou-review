---
title: "Cum se contabilizează TVA la import pentru un magazin online?"
description: Dacă magazinul online cumpără marfă en-gros din afara UE cu declarație vamală de import, contabilizarea e cea standard de import; dacă vinde direct clienților colete de sub 150 euro prin platforme, acel regim nu are corespondent în iConta.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează TVA la import pentru un magazin online?

Întrebarea ascunde de fapt două situații diferite pentru un magazin online, care trebuie tratate separat. Prima: magazinul cumpără marfă en-gros din afara UE, cu declarație vamală de import completă (DVI), pentru a o revinde ulterior — acesta e un import clasic. A doua: magazinul (sau platforma prin care vinde) livrează direct clienților colete individuale de mică valoare, cumpărate în numele clientului dintr-o țară terță — acesta e regimul special pentru loturi de maximum 150 euro, netratat aici.

## Temeiul legal

::: ghid-temei
„(1) Baza de impozitare pentru importul de bunuri este valoarea în vamă a bunurilor, stabilită conform legislației vamale în vigoare, la care se adaugă orice taxe, impozite, comisioane și alte taxe datorate în afara României, precum și cele datorate ca urmare a importului bunurilor în România, cu excepția taxei pe valoarea adăugată care urmează a fi percepută."

— Codul fiscal (Legea 227/2015 consolidat), art. 289 alin. (1)
:::

::: ghid-temei
„c) pentru taxa achitată pentru importul de bunuri, altele decât cele prevăzute la lit. d), să dețină declarația vamală de import sau actul constatator emis de organele vamale, care să menționeze persoana impozabilă ca importator al bunurilor din punctul de vedere al taxei, precum și documente care să ateste plata taxei de către importator [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 299 alin. (1) lit. c)
:::

Pentru marfa cumpărată en-gros cu DVI completă, regulile sunt cele generale de import: bază de TVA = valoare vamală + taxe vamale + accize + cheltuieli accesorii (art. 289), iar TVA-ul se tratează după statutul firmei — plată la vamă și deducere pe DVI (art. 299 alin. 1 lit. c), autolichidare prin certificat de amânare (art. 326 alin. 4), sau cost, pentru neplătitori.

Pentru vânzarea directă de colete mici (sub 150 euro) prin platforme online, legea prevede un regim separat (art. 270 alin. 15, art. 315^2, art. 315^3), care nu face obiectul acestui ghid.

## Ce se greșește în practică

- Se contabilizează orice marfă cumpărată "din afara UE pentru magazinul online" ca fiind sub același regim, fără să se distingă între o achiziție en-gros cu DVI (import clasic) și vânzarea la distanță de colete individuale sub 150 euro prin platformă (regim special separat).
- Se lasă cota de TVA la valoarea implicită, presupunând-o automat cea standard curentă, fără verificare pentru operațiunea concretă de import.
- Se introduce procentul taxei vamale ca sumă, nu ca procent din valoarea vamală, umflând artificial baza de TVA.

## Ce face iConta.eu

Pentru achiziția en-gros din afara UE cu declarație vamală de import, ecranul „Import extracomunitar (DVI)" calculează baza de TVA (valoare vamală + taxe vamale + accize + accesorii, cu cota declarată explicit) și generează automat nota contabilă potrivit modului de tratare a TVA: linie de bază pe contul de destinație (ex. 371, marfă) față de 401, taxa vamală pe 446 dacă există, și linia de TVA — 4426=4427 pentru certificat de amânare, 4426=446 pentru plată la vamă cu deducere pe DVI, sau TVA inclus în costul mărfii pentru neplătitori. Conturile folosite (401, 446, 4426, 4427) provin din planul de conturi standard; modulul de import nu conține un citat explicit dintr-un ordin (OMFP) care să justifice punctual alegerea contului 446 pentru taxa vamală/TVA la vamă — dacă e nevoie de o justificare contabilă detaliată a acestui cont, temeiul trebuie căutat separat, în reglementările contabile generale.

Pentru vânzarea directă de colete mici (sub 150 euro) prin platforme online către clienți finali, **iConta nu are o funcționalitate dedicată** — ecranul de import extracomunitar e construit pentru operațiuni cu DVI completă, nu pentru acest regim special de vânzare la distanță.

[iConta.eu](/)
