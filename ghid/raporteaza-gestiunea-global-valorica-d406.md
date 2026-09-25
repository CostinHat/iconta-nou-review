---
title: "Cum se raportează gestiunea global-valorică în D406?"
description: "Ce prevede declarația D406 (SAF-T) pentru stocuri și de ce gestiunea ținută la preț de vânzare (metoda global-valorică) nu are, în iConta.eu, un traseu automat spre secțiunea PhysicalStock."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează gestiunea global-valorică în D406?

Secțiunea „Stocuri" a declarației D406 (SAF-T) nu se depune periodic, ca restul declarației, ci **doar la cererea expresă a organului fiscal**. Pentru o firmă care ține gestiunea de marfă la preț de vânzare, prin metoda global-valorică (adaos comercial pe contul 378, TVA neexigibilă pe 4428), întrebarea reală e ce date poate genera aplicația în secțiunea PhysicalStock a fișierului standard de control fiscal — și, la acest moment, răspunsul onest e că nu poate genera nimic, pentru că motorul global-valoric nu ține evidență pe articol.

## Temeiul legal

::: ghid-temei
„9. Informaţiile privind «stocurile de produse» şi «producţie în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcţie de perioada pentru care se solicită furnizarea informaţiilor privind stocurile prin fişierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declaraţii informative cuprinzând subsecţiunile din fişierul SAF-T relevante pentru «Stocuri» [...]
10. Declaraţiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF 1783/2021, Anexa (Instrucțiuni de completare D406), pct. 9-10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Secțiunea PhysicalStock nu face parte din depunerile lunare/trimestriale obișnuite ale D406 — apare doar când ANAF o cere explicit, pentru o anumită perioadă.
- Structura oficială a unei linii PhysicalStock cere, pentru fiecare produs: depozitul, codul produsului, contul de stoc, unitatea de măsură, cantitatea și valoarea la deschidere, cantitatea și valoarea la închidere.
- Metoda global-valorică din OMFP 1802/2014 (pct. 286) e o metodă **la nivel de gestiune**, nu la nivel de articol: adaosul se repartizează global, printr-un coeficient K, nu se ține o fișă de cantitate/cost pe fiecare produs în parte.

## Ce se greșește în practică

- Se presupune că orice raport SAF-T de stocuri poate fi generat automat, indiferent de metoda de gestiune folosită — de fapt structura oficială PhysicalStock cere date pe produs (cantitate + cost unitar), pe care metoda global-valorică nu le produce prin construcție.
- Se confundă soldul contabil al contului 371 (marfă la preț de vânzare, cu adaos și TVA neexigibilă incluse) cu „valoarea de stoc" cerută de SAF-T, care e gândită pentru gestiuni ținute la cost.
- Se așteaptă ca declarația să fie cerută periodic, ca D300 sau D112, când de fapt secțiunea de stocuri se depune doar la solicitare punctuală a ANAF, cu termen minim de 30 de zile de la cerere.

## Ce face iConta.eu

Verificat direct în cod: generatorul D406 Stocuri (`core/d406_stocuri.py`, funcționalitatea „D406 Stocuri (la cerere)") construiește secțiunea PhysicalStock exclusiv din mișcările de stoc pe articol (tabela `miscari_stoc`, cu cantitate și valoare per intrare/ieșire) — date scrise doar de motorul de gestiune **cantitativ-valorică** (CMP, `core/stocuri_cv_api.py`). Motorul de gestiune **global-valorică** (`core/stocuri.py` + `core/stocuri_api.py`) nu scrie niciodată în `miscari_stoc`: el produce doar note contabile pe conturile 371/378/4428, fără cantitate și fără cost pe articol. Rezultatul, confirmat prin citirea codului: o firmă care ține gestiunea global-valorică **nu are astăzi, în iConta.eu, niciun traseu automat** prin care rulajele ei să ajungă în secțiunea PhysicalStock a D406. Dacă ANAF cere efectiv acest raport unei astfel de firme, generarea lui trebuie făcută manual, în afara aplicației, pe baza evidenței proprii de gestiune.

[iConta.eu](/)
