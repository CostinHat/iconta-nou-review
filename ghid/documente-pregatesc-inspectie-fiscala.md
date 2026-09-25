---
title: "Ce documente pregătesc pentru o inspecție fiscală?"
description: "Ce documente și informații trebuie puse la dispoziția organului de inspecție fiscală, potrivit Codului de procedură fiscală, și ce conține avizul de inspecție."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce documente pregătesc pentru o inspecție fiscală?

Documentele necesare rezultă chiar din avizul de inspecție fiscală, care indică expres obligațiile fiscale și perioadele ce urmează a fi verificate. Practic, contribuabilul trebuie să pună la dispoziția inspectorilor toate documentele care justifică situația fiscală pentru acele obligații și acele perioade — evidența contabilă, declarațiile depuse, contractele și documentele justificative aferente.

## Temeiul legal

::: ghid-temei
„(7) Avizul de inspecție fiscală cuprinde:
a) temeiul juridic al inspecției fiscale;
b) data de începere a inspecției fiscale;
c) obligațiile fiscale, alte obligații prevăzute de legislația fiscală și contabilă, precum și perioadele ce urmează a fi supuse inspecției fiscale;
d) posibilitatea de a solicita amânarea datei de începere a inspecției fiscale;
e) posibilitatea depunerii sau corectării declarației de impunere aferentă perioadelor și creanțelor fiscale ce vor face obiectul inspecției fiscale, până la data începerii inspecției fiscale."
— Legea 207/2015 privind Codul de procedură fiscală, art. 122 alin. (7) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Avizul de inspecție fiscală se comunică în scris, cu **30 de zile înainte pentru marii contribuabili** și cu **15 zile înainte pentru ceilalți contribuabili/plătitori** — interval în care se poate pregăti documentația.
- Avizul precizează exact ce obligații fiscale și ce perioade sunt vizate (de exemplu TVA pe ultimii 5 ani, sau impozit pe profit pe un anumit exercițiu financiar) — pregătirea documentelor se face în funcție de acest conținut, nu „la general".
- Contribuabilul are dreptul, până la data începerii inspecției, să depună sau să corecteze declarațiile de impunere aferente perioadelor vizate — o ultimă șansă de a regulariza eventuale erori înainte de control.
- La începerea inspecției, organul de inspecție fiscală trebuie să prezinte legitimația și ordinul de serviciu; începerea se consemnează în registrul unic de control, dacă firma are obligația de a-l ține.
- La finalul inspecției, contribuabilul trebuie să dea o declarație scrisă, pe propria răspundere, că a pus la dispoziție toate documentele și informațiile solicitate, și că acestea i-au fost restituite integral.

## Ce se greșește în practică

- Se pregătesc doar documentele „evidente" (facturi, extrase de cont), ignorând citirea atentă a avizului, care indică exact ce obligații și ce perioade sunt vizate — o inspecție parțială pe TVA nu cere aceleași documente ca una pe impozit pe profit.
- Se ratează fereastra de 15/30 de zile dintre comunicarea avizului și începerea inspecției — interval în care se pot corecta declarații sau depune declarații omise, fără riscul sancțiunilor aplicabile în timpul controlului.
- Se semnează declarația finală de la sfârșitul inspecției fără verificarea atentă a listei de documente returnate, ceea ce poate crea probleme ulterioare de dovadă.
- Se confundă inspecția fiscală (procedură amplă, cu aviz prealabil, pe obligații și perioade determinate) cu un control inopinat sau cu verificarea documentară — fiecare are reguli proprii de anunțare și de conduită.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcție care să genereze automat lista de documente necesare pentru o inspecție fiscală reală ANAF**. Aplicația are un ecran de „control fiscal" (`control_fiscal_api.py`, `control_incrucisat.py`, `alerte_control_fiscal.py`), dar acesta e un **semafor intern de conformare** — compară declarațiile depuse (D112, D300, D390) cu ce ar trebui depus și semnalează inconsecvențe sau declarații lipsă. E util pentru a intra pregătit într-o inspecție reală (declarațiile sunt coerente între ele), dar nu înlocuiește pregătirea documentelor justificative cerute efectiv de organul fiscal, pe baza avizului de inspecție.

[iConta.eu](/)
