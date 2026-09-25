---
title: "Cum se calculează norma de venit pentru o întreprindere individuală?"
description: "Regulile Codului fiscal privind stabilirea venitului net anual pe baza normelor de venit pentru activități independente, inclusiv pentru întreprinderi individuale."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează norma de venit pentru o întreprindere individuală?

Pentru anumite activități independente — inclusiv cele desfășurate printr-o întreprindere individuală — legea permite stabilirea venitului net anual impozabil pe o bază forfetară, „norma de venit", și nu prin evidența reală a veniturilor și cheltuielilor. Practic, contribuabilul plătește impozit la o sumă fixă stabilită de fisc pentru activitatea respectivă, indiferent de rezultatul economic real.

## Temeiul legal

::: ghid-temei
„(1) În cazul contribuabililor care realizează venituri din activități independente, altele decât venituri din profesii liberale definite la art. 67 alin. (2), venitul net anual se determină pe baza normelor de venit de la locul desfășurării activității. [...]
(3) Norma de venit pentru fiecare activitate desfășurată de contribuabil nu poate fi mai mică decât nivelul a 12 salarii de bază minime brute pe țară garantate în plată, în vigoare la data de 1 ianuarie a anului de realizare a venitului. Prevederile prezentului alineat se aplică și în cazul în care activitatea se desfășoară în cadrul unei asocieri fără personalitate juridică, norma de venit fiind stabilită pentru fiecare membru asociat."
— Codul fiscal (Legea 227/2015), art. 69 alin. (1) și (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Norma de venit se aplică veniturilor din activități independente, altele decât profesiile liberale (avocați, notari, medici cu cabinet propriu etc., care au regim distinct) — inclusiv activităților desfășurate printr-o întreprindere individuală atunci când legea permite acest sistem pentru CAEN-ul respectiv.
- Nivelul normelor de venit este stabilit anual de direcțiile generale regionale ale finanțelor publice, în cursul trimestrului IV al anului anterior celui de aplicare, pe baza nomenclatorului de activități aprobat prin ordin al ministrului finanțelor (art. 69 alin. (2)).
- Legea impune un plafon minim: norma de venit pentru orice activitate nu poate fi sub echivalentul a 12 salarii de bază minime brute pe țară în vigoare la 1 ianuarie a anului de realizare a venitului — practic un „prag minim" indiferent cât de mică este activitatea.
- Dacă activitatea se desfășoară doar o parte din an (mai puțin decât anul calendaristic), norma de venit se reduce proporțional cu perioada efectiv lucrată (art. 69 alin. (5)).
- Dacă un contribuabil desfășoară două sau mai multe activități pe bază de normă de venit, venitul net total se stabilește prin însumarea normelor corespunzătoare fiecărei activități (art. 69 alin. (6)).

## Ce se greșește în practică

- Se aplică norma de venit unei activități care, de fapt, se încadrează la profesii liberale (art. 67 alin. (2)) — acestea nu intră sub incidența art. 69, ci au regim propriu de determinare a venitului net.
- Se ignoră plafonul minim de 12 salarii minime brute și se raportează o normă de venit publicată eronat sau neactualizată de la un an la altul.
- Se uită reducerea proporțională a normei atunci când activitatea a fost desfășurată doar câteva luni din an (de exemplu firma s-a înființat în cursul anului) — norma anuală întreagă se aplică greșit ca și cum activitatea ar fi durat 12 luni.

## Ce face iConta.eu

iConta.eu susține regimul de determinare a venitului pe bază de normă de venit: în modulul de registru de evidență fiscală (`registru_evidenta_fiscala.py`) și în generatorul Declarației Unice (`d212.py`), norma de venit este unul dintre modurile recunoscute de stabilire a venitului net („sistem real", „cote forfetare", „norma de venit"), cu regula specifică potrivit căreia la norma de venit nu se înscriu cheltuieli în registru (conform art. 1 alin. (2) din normele metodologice ale registrului). Aplicația nu calculează însă ea însăși nivelul normei de venit publicat de administrația județeană — acesta rămâne o dată introdusă de utilizator, conform publicării anuale a ANAF.

[iConta.eu](/)
