---
title: "Care este calendarul fiscal pentru o întreprindere individuală în 2026?"
description: "Termenul legal de 25 mai pentru declarația unică a persoanelor fizice care obțin venituri din activități independente, inclusiv cazurile care obligă la o declarație suplimentară în cursul anului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este calendarul fiscal pentru o întreprindere individuală în 2026?

O întreprindere individuală (ÎI) e, din punct de vedere fiscal, o persoană fizică autorizată care realizează venituri din activități independente — calendarul ei principal se leagă de declarația unică, nu de declarațiile specifice persoanelor juridice.

## Temeiul legal

::: ghid-temei
„(3) Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice se completează și se depune la organul fiscal competent, pentru fiecare an fiscal, până la data de 25 mai inclusiv a anului următor celui de realizare a veniturilor. Prevederea se aplică și în situațiile prevăzute la alin. (2)."
— Legea 227/2015 (Codul fiscal), art. 122 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text și din contextul art. 122 rezultă calendarul concret al unei întreprinderi individuale:

- **Termenul general e 25 mai inclusiv a anului următor** celui de realizare a veniturilor — pentru veniturile realizate în 2026, declarația unică se depune până la 25 mai 2027.
- **Declarația nu se depune o singură dată la final de an**, ci și în cursul anului, în situații speciale: începerea sau încetarea activității, întreruperea/suspendarea temporară a activității, sau modificări ale clauzelor contractuale relevante pentru venit (art. 122 alin. (2)) — fiecare astfel de eveniment declanșează o obligație declarativă, nu doar cea de la 25 mai.
- **Aceeași declarație acoperă atât impozitul pe venit, cât și contribuțiile sociale** (CAS, CASS) — nu există declarații separate pentru fiecare, spre deosebire de o firmă cu salariați, care depune D112 lunar.
- **Termene distincte pot exista pentru bonificații de plată anticipată** — Codul fiscal prevede, pentru anumite facilități de reducere a impozitului, termene mai scurte (ex. 15 aprilie, pentru anumite bonificații aplicabile veniturilor unui an anterior), separate de termenul general de depunere.

## Ce se greșește în practică

- Se depune declarația unică o singură dată, la sfârșitul anului fiscal, ignorând obligația de declarare suplimentară la începerea/încetarea/suspendarea activității în cursul anului.
- Se confundă termenul general de 25 mai cu termenele scurte, speciale, legate de bonificațiile de plată anticipată — ratarea termenului scurt nu înseamnă ratarea declarației, dar înseamnă pierderea bonificației.
- Se presupune că întreprinderea individuală are un calendar identic cu al unui SRL (declarații lunare/trimestriale de TVA, impozit pe profit) — regimul de bază al ÎI e anual, prin declarația unică, cu excepțiile care apar doar dacă firma are salariați sau e înregistrată în scopuri de TVA.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează CAS și CASS pentru declarația unică prin `core/d212_engine.py` (`calculeaza_cas()`, `calculeaza_cass()`, `calculeaza_d212()`), cu plafoanele anuale aduse din `plafoane_an()`. Modulul de urmărire a obligațiilor fiscale (`core/control_fiscal_api.py`) tratează însă explicit D212 ca fiind **rutată separat** de calendarul general de obligații pe care îl monitorizează pentru celelalte declarații (D100, D300, D112 etc.) — termenul de 25 mai nu apare în tabloul unic de scadențe urmărite automat de aplicație pentru restul declarațiilor. Calculul sumelor e automatizat; urmărirea scadenței de 25 mai (și a termenelor declarative suplimentare din cursul anului) rămâne, la acest moment, în afara acestui tablou unificat.

[iConta.eu](/)
