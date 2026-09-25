---
title: "Impozitarea câștigului din cesiunea părților sociale 2026"
description: "Cum se calculează câștigul impozabil dintr-o cesiune de părți sociale ale unui SRL de către o persoană fizică, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impozitarea câștigului din cesiunea părților sociale 2026

Părțile sociale ale unui SRL sunt, din punct de vedere fiscal, titluri de valoare — iar vânzarea (cesiunea) lor de către un asociat persoană fizică generează un câștig impozabil calculat după aceleași reguli aplicabile transferului oricărui titlu de valoare.

## Temeiul legal

::: ghid-temei
„Câștigul/pierderea din transferul titlurilor de valoare, altele decât instrumentele financiare derivate și cele reglementate la alin. (2)-(6), reprezintă diferența pozitivă/negativă realizată între valoarea de înstrăinare/prețul de vânzare și valoarea lor fiscală, după caz, pe tipuri de titluri de valori, care include costurile aferente tranzacției [...], dovedite cu documente justificative."
— Legea 227/2015 (Codul fiscal), art. 94 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Elementele de calcul, potrivit legii:

- **baza de calcul** e diferența dintre prețul de cesiune (prevăzut în contractul de cesiune de părți sociale) și **valoarea fiscală** a părților sociale — de regulă, valoarea nominală vărsată la înființare sau la o majorare ulterioară de capital, plus costurile aferente tranzacției dovedite cu documente justificative;
- pentru tranzacțiile efectuate **prin intermediari** (entitățile prevăzute la art. 96^1 alin. 1 — brokeri, societăți de administrare a investițiilor), impozitul se reține la sursă prin aplicarea unei cote de **3%** dacă titlurile au fost deținute mai mult de 365 de zile, respectiv **6%** dacă au fost deținute mai puțin de 365 de zile (art. 97 alin. 8^1 lit. a);
- pentru o **cesiune directă de părți sociale ale unui SRL**, realizată de regulă fără intermediar (prin act de cesiune și înregistrare la ONRC), sursele verificate nu detaliază explicit mecanismul de reținere la sursă aplicabil acestui caz specific — regula de determinare a câștigului (art. 94) rămâne aceeași, dar modul concret de declarare (reținere la sursă vs. autoimpunere prin Declarația Unică) pentru cesiunile fără intermediar necesită verificare suplimentară la sursă, dincolo de ce oferă documentele consultate pentru acest ghid;
- dacă vânzătorul e o **persoană juridică**, nu o persoană fizică, regimul e diferit: câștigul din cesiune intră în rezultatul fiscal supus impozitului pe profit (sau impozitului pe veniturile microîntreprinderilor, dacă firma e la regimul micro), nu regulilor de mai sus, specifice persoanelor fizice.

## Ce se greșește în practică

- Se aplică automat cota de dividende (16%, din 2026) câștigului din cesiune, în loc de regulile specifice titlurilor de valoare (art. 94 și 97) — sunt regimuri fiscale distincte, cu baze de calcul diferite.
- Se calculează câștigul raportat la valoarea de piață a firmei, nu la prețul efectiv din contractul de cesiune — baza legală e prețul de vânzare convenit, nu o estimare de valoare.
- Se omite includerea costurilor aferente tranzacției (taxe notariale, ONRC) în calculul valorii fiscale/câștigului, deși legea le permite explicit, cu condiția să fie dovedite cu documente justificative.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul dedicat calculului impozitului pe câștigul din cesiunea de părți sociale — spre deosebire de dividende și de lichidare, pentru care aplicația are motoare de calcul explicite (`core/decontari_asociati.py`, `core/lichidare.py`), cesiunea de părți sociale între asociați sau către un terț nu e acoperită de niciun modul specific. Calculul și declararea acestui impozit rămân, pentru moment, în sarcina contabilului.

[iConta.eu](/)
