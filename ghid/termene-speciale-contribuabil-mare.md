---
title: "Ce termene speciale are un contribuabil mare"
description: "Termenele diferite pentru marii contribuabili la avizul de inspecție fiscală și la obligația de depunere SAF-T (D406), potrivit Codului de procedură fiscală și OPANAF 1783/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce termene speciale are un contribuabil mare

Încadrarea la categoria „mari contribuabili" nu schimbă doar organul fiscal competent — aduce și termene diferite, atât la inspecția fiscală, cât și la obligația de raportare SAF-T.

## Temeiul legal

::: ghid-temei
„Avizul de inspecție fiscală se comunică contribuabilului/plătitorului, înainte de începerea inspecției fiscale, astfel: a) cu 30 de zile pentru marii contribuabili; b) cu 15 zile pentru ceilalți contribuabili/plătitori."
— Legea nr. 207/2015, art. 122 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Obligația de transmitere a fișierului standard de control fiscal prin intermediul Declarației informative D406 devine efectivă pentru fiecare categorie de contribuabili, astfel: — pentru contribuabilii încadrați în categoria marilor contribuabili la data de 1 ianuarie 2022 [...] obligația de depunere [...] începe de la data de 1 ianuarie 2022 [...]; — pentru contribuabilii încadrați în categoria contribuabili mijlocii la data de 31 decembrie 2021, obligația [...] începe de la data de 1 ianuarie 2023 [...]; — pentru contribuabilii încadrați în categoria de contribuabili mici la data de 31 decembrie 2021, obligația [...] începe de la data de 1 ianuarie 2025 [...]."
— OPANAF nr. 1.783/2021, Anexa 5, pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Din cele două surse rezultă două termene speciale distincte, cu logici diferite:

- **Avizul de inspecție fiscală**: marii contribuabili sunt înștiințați cu **30 de zile** înainte de începerea inspecției, față de doar 15 zile pentru restul contribuabililor — dublu termen de pregătire, prevăzut expres de Codul de procedură fiscală.
- **SAF-T (D406)**: marii contribuabili au fost prima categorie obligată să depună SAF-T, începând cu 1 ianuarie 2022 — cu doi ani înaintea contribuabililor mijlocii (2023) și cu trei ani înaintea celor mici (2025).
- Cele două termene nu sunt legate între ele — unul ține de procedura de control, celălalt de calendarul de intrare în vigoare a unei obligații declarative — dar amândouă pornesc de la aceeași încadrare oficială ANAF în categoria „mari contribuabili".

## Ce se greșește în practică

- Se aplică termenul de 15 zile pentru avizul de inspecție și la un contribuabil mare, ignorând că art. 122 alin. (2) lit. a) prevede expres 30 de zile pentru această categorie.
- Se presupune că toate firmele au aceeași dată de referință pentru SAF-T — de fapt data de la care curge obligația depinde strict de categoria (mare/mijlociu/mic) în care contribuabilul era încadrat la data de referință stabilită de ANAF.
- Se ignoră faptul că, o dată intrat sub obligația SAF-T, contribuabilul continuă să raporteze chiar dacă ulterior „coboară" într-o categorie pentru care termenul de referință nu s-a împlinit încă — regulă explicită în Anexa 5 pct. 2.

## Ce face iConta.eu

Generatorul de D406 din iConta.eu (`core/d406.py` și fișierele `d406_*.py`) produce declarația SAF-T pe baza datelor firmei, dar aplicația nu urmărește automat, la data acestui ghid, calendarul de intrare treptată în obligația de depunere (mare/mijlociu/mic contribuabil) și nici termenele diferențiate pentru avizul de inspecție fiscală — acestea rămân verificări pe care contabilul trebuie să le facă separat, în funcție de încadrarea comunicată de ANAF pentru firma respectivă.

[iConta.eu](/)
