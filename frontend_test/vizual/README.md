# frontend_test/vizual — infrastructură de testare vizuală (permanentă)

Trei unelte care rulează pe pagina RANDATĂ (Playwright, autentificat via `w_auth`), nu pe HTML static.
Introduse 17.08.2026 (marca de referință intrare 66f50cd). **Nu repară** — măsoară și marchează.

Rulare (pe server, în `~/iconta_nou`, cu serviciul la 127.0.0.1:8010):
```
set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a
export PYTHONPATH=$HOME/iconta_nou:$HOME/iconta_nou/frontend_test:$HOME/iconta_nou/frontend_test/vizual
./venv/bin/python frontend_test/vizual/<unealta>.py
```

## Cele 5 ecrane (nav_ecrane.ECRANE)
Un singur loc de adevăr pentru „ce înseamnă ecranul X": `import_mijloace_fixe`, `vector_fiscal`,
`plan_conturi`, `stat_plata`, `declaratii`. Navigare reutilizabilă din `w_auth.deschide_firma`
(tenant_003 „Comert Micro TVA", token mințuit fără parolă).

## 1. axe_scan.py — axe-core injectat (v4.10.2, vandorizat offline)
Rulează axe pe wcag2a+2aa+21 și extrage explicit cele trei interese: **contrast**
(`color-contrast`), **fără etichetă** (`label`/`*-name`), și **title** în trei categorii:
`strict` (title, zero text, fără aria), `glif` (vizibil doar un glif, nume real în title),
`extra` (etichetă vizibilă reală, dar title cară ALTĂ informație — ex. motivul blocării).
Ieșire: `raport_axe.txt` + `.json`.

## 2. mobil_scan.py — emulare telefon (Pixel 5: touch, fără hover, 393px)
Același traseu pe profil mobil. Enumeră ce devine inaccesibil: tooltip-uri `title`
(dispar pe touch — marcate cele cu info unică), reguli CSS `:hover` care ascund/arată conținut,
ținte de atingere <44px, overflow orizontal. Ieșire: `raport_mobil.txt` + `.json` + `mobil_*.png`.

## 3. interactiune_scan.py — comportamentul la apăsare, și textul lung
Apasă butoanele fiecărui ecran (ne-destructiv, cu re-navigare), umple casetele cu text lung +
diacritice, pe axe desktop **și** mobil. Prinde: erori de consolă la apăsare, layout rupt, revărsare
orizontală, ținte <24px, `title`-only. Ieșire: `acoperire_vizuala.json` (se comite), cuplat mecanic
de `core/test_acoperire_vizuala.py` — o schimbare de UI nu se poate comite fără scan proaspăt.

## Ce NU mai există: comparația de capturi
`baseline_scan.py` și `baseline/*.png` au fost **scoase pe 03.09.2026**, prin decizie de arhitectură:
*un baseline vizual e o probă care îmbătrânește prin construcție — se strică la orice schimbare
legitimă, iar atunci se regenerează ca să treacă și devine formalitate.* Ce s-a păstrat sunt
**regulile** (contrast, revărsare la 393 px, elemente vizibile fără derulare), care nu îmbătrânesc.
Motivul întreg: `METODA_VERIFICARE.md` §27.

## Gardă
`core/test_infra_vizuala.py` pică dacă lipsește oricare unealtă de **regulă**, `axe.min.js` sau
`nav_ecrane.py` — și, în direcția opusă, pică dacă `baseline_scan.py`/`baseline/` **reapar**.
