---
title: "Cum dovedesc pregătirea profesională pentru activitatea unui PFA?"
description: "Procedura de dovadă a calificării la înregistrarea unui PFA e reglementată de OUG 44/2008, un act care nu se regăsește în sursele fiscale ale acestui ghid — dar Codul fiscal folosește apartenența la o profesie reglementată drept unul dintre criteriile care disting o activitate independentă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum dovedesc pregătirea profesională pentru activitatea unui PFA?

Procedura exactă de dovadă a calificării — ce documente se depun la registrul comerțului, ce diplome sau atestate sunt acceptate pe fiecare cod CAEN — este reglementată de OUG nr. 44/2008 privind desfășurarea activităților economice de către persoanele fizice autorizate, întreprinderile individuale și întreprinderile familiale. Acest act nu se regăsește în sursele fiscale disponibile pentru acest ghid, așa că nu putem cita din el fără să riscăm o invenție. Vă redirecționăm însă onest spre ce chiar putem documenta din Codul fiscal: felul în care pregătirea profesională intervine ca **element de calificare fiscală** a activității, o dată ce PFA-ul e deja înființat.

## Temeiul legal

::: ghid-temei
„3. activitate independentă - orice activitate desfășurată de către o persoană fizică în scopul obținerii de venituri, care îndeplinește cel puțin 4 dintre următoarele criterii: 3.1. persoana fizică dispune de libertatea de alegere a locului și a modului de desfășurare a activității, precum și a programului de lucru; 3.2. persoana fizică dispune de libertatea de a desfășura activitatea pentru mai mulți clienți; 3.3. riscurile inerente activității sunt asumate de către persoana fizică ce desfășoară activitatea; 3.4. activitatea se realizează prin utilizarea patrimoniului persoanei fizice care o desfășoară; 3.5. activitatea se realizează de persoana fizică prin utilizarea capacității intelectuale și/sau a prestației fizice a acesteia, în funcție de specificul activității; 3.6. persoana fizică face parte dintr-un corp/ordin profesional cu rol de reprezentare, reglementare și supraveghere a profesiei desfășurate, potrivit actelor normative speciale care reglementează organizarea și exercitarea profesiei respective; 3.7. persoana fizică dispune de libertatea de a desfășura activitatea direct, cu personal angajat sau prin colaborare cu terțe persoane în condițiile legii."
— Legea 227/2015 (Codul fiscal), art. 7 pct. 3 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Această definiție nu e procedura de înființare — e criteriul pe care fiscul îl folosește, ulterior, pentru a stabili dacă activitatea se califică drept „independentă" (adică impozitată la titlul IV din Codul fiscal, ca PFA) și nu ca activitate dependentă deghizată:

- Legea cere îndeplinirea a **cel puțin 4 din cele 7 criterii**, nu a unuia singur — pregătirea profesională e doar unul dintre ele.
- Criteriul 3.6 leagă explicit calificarea de **apartenența la un corp/ordin profesional** reglementat prin acte normative speciale ale profesiei respective (de exemplu, o profesie liberală cu ordin propriu) — dar acest criteriu nu se aplică tuturor meseriilor; multe activități PFA (comerț, prestări de servicii tehnice) nu au un corp profesional de acest tip, iar dovada calificării se face atunci prin actele cerute la înregistrare (certificate de calificare, atestate, autorizații de meserie), stabilite de OUG 44/2008 — nu de legea fiscală.
- Restul criteriilor (libertatea programului, asumarea riscului, folosirea patrimoniului propriu, posibilitatea de a angaja personal) sunt independente de pregătirea profesională propriu-zisă și privesc modul de organizare a activității.

## Ce se greșește în practică

- Se confundă dovada calificării cerută la înregistrarea PFA la ONRC (act de studii, certificat de calificare, atestat, potrivit OUG 44/2008) cu criteriile fiscale de la art. 7 pct. 3 din Codul fiscal — cele două servesc scopuri diferite și sunt verificate de instituții diferite.
- Se presupune că un singur criteriu (de exemplu, deținerea unei diplome) e suficient pentru calificarea fiscală drept activitate independentă — legea cere minimum 4 din cele 7.
- Se aplică automat criteriul 3.6 (corp/ordin profesional) la meserii care nu au un astfel de organism, ignorând că celelalte 6 criterii pot fi cele relevante pentru încadrare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu documentează și nu automatizează** procedura de dovadă a pregătirii profesionale la înregistrarea unui PFA — aceasta ține de OUG 44/2008 și de registrul comerțului, în afara sursei de temeiuri fiscale a aplicației. Ce e deja acoperit, o dată PFA-ul înființat: **Registrul de evidență fiscală pentru persoane fizice** (varianta „venituri_pf" din `core/registru_evidenta_fiscala.py`, cu temei la CF art. 68 alin. (8)-(9) și OMFP 3254/2017), care ține evidența anuală a venitului brut și a cheltuielilor deductibile pe fiecare sursă de venit, precum și generarea manuală a declarației D212 (`core/d212.py`), pe baza datelor introduse de contabil.

[iConta.eu](/)
