---
title: "Ce fac dacă ANAF semnalează diferențe între D300 și D394?"
description: "De ce D300 și D394 nu trebuie să fie egale ca sumă totală și ce verifici concret când ANAF semnalează o diferență."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă ANAF semnalează diferențe între D300 și D394?

D300 (decontul de TVA) și D394 nu sunt, prin construcție, aceeași sumă privită din două unghiuri — D394 e un subset al lui D300, nu o oglindă a lui. O notificare de la ANAF pe o diferență între cele două nu înseamnă automat o eroare; înseamnă că trebuie verificat dacă diferența are explicație structurală sau e chiar o greșeală.

## Temeiul legal

::: ghid-temei
„[...] se înscrie perioada fiscală declarată pentru depunerea decontului de taxă pe valoarea adăugată (formularul 300) [...] L - luna, T - trimestrul, S - semestrul, A - anul."
— OPANAF 2194/2025, Anexa 2, secțiunea 1 lit. a) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:781-783)

„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025, Anexa 2 pct.1 lit.b) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:741-742)
:::

Cele două texte explică de ce D300 și D394 nu trebuie comparate sumă cu sumă:

- **Perioada fiscală e identică** — D394 se raportează pe aceeași perioadă (lună/trimestru) ca decontul de TVA de la care se leagă. Deci, dacă diferența vine din perioade nealiniate, e o eroare de completare, nu o discrepanță de fond.
- **Conținutul nu e identic.** D300 cuprinde tot TVA-ul firmei — inclusiv achizițiile/livrările intracomunitare și importurile. D394 exclude explicit achizițiile intracomunitare (care merg în D390) — deci suma din D394 e, prin lege, mai mică sau egală cu partea „națională" a lui D300, niciodată o replică integrală a lui.

## Ce se greșește în practică

- Se așteaptă ca totalul bazei impozabile din D300 să fie egal cu totalul din D394, și orice diferență e tratată ca eroare — de fapt diferența e normală ori de câte ori firma are operațiuni intracomunitare sau importuri, care apar doar în D300.
- Se corectează D394 „ca să iasă" egal cu D300, introducând acolo operațiuni care, prin lege, nu trebuie declarate în D394 (achizițiile intracomunitare).
- Se ignoră perioada de raportare diferită — pentru declarația trimestrială, câmpul „lună" din D394 se codifică pe ultima lună a trimestrului, nu pe luna curentă, iar o citire greșită a acestei reguli poate crea aparența unei diferențe.

## Ce face iConta.eu

Nu există, la generarea declarației, niciun mecanism live care compară automat D300 cu D394 — cele două se generează separat, fiecare cu propria validare pe validatorul oficial ANAF (DUK). Există, doar la nivel de dezvoltare, un gard intern (`core/test_d300_d394_paritate.py`) care confruntă cele două calcule pe cotă de TVA — dar chiar acest gard e documentat în cod ca fiind tautologic: ambele generatoare citesc aceleași linii de factură și deduc cota identic, deci prinde doar o eventuală divergență între cele două generatoare, nu o eroare reală de conținut, și nu rulează la generarea efectivă a declarației de către utilizator. Verificarea internă din aplicație pentru D394 e limitată, la rulare, la propria consistență: o a doua cale de calcul independentă (`core/d394_reconciliere.py`) recalculează totalurile pe cotă direct din liniile de factură și oprește generarea dacă diferă de rezultatul generatorului principal — dar și această gardă compară D394 cu el însuși, nu cu D300.

Concret, când ANAF semnalează o diferență, verificarea trebuie făcută manual: separă din D300 partea de operațiuni intracomunitare și importuri (care nu apar deloc în D394), apoi compară doar restul — operațiunile naționale — cu ce a generat D394 pentru aceeași perioadă.

[iConta.eu](/)
