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

## 3. baseline_scan.py — comparație de capturi (echivalent toHaveScreenshot)
Fără argument = **stabilește** baseline-urile + self-diff (flakiness: captură de două ori).
`--compare` = compară captura curentă cu `baseline/<ecran>.png`, raportează pixeli diferiți + %,
prag 0.05%. Determinism: viewport fix 1280x1800 + animații oprite; toleranță 16/canal.
Baseline-urile din `baseline/*.png` SE versionează — sunt referința pentru tura următoare.

## Gardă
`core/test_infra_vizuala.py` pică dacă lipsește oricare unealtă, `axe.min.js`, `nav_ecrane.py`
sau vreun baseline — infra nu poate dispărea tăcut (Regula 6).
