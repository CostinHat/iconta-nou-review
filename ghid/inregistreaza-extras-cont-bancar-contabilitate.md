---
title: "Cum se înregistrează un extras de cont bancar în contabilitate?"
description: "Extrasul de cont bancar ca document justificativ, și cum se traduce fiecare linie a lui într-o notă contabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează un extras de cont bancar în contabilitate?

Extrasul de cont e unul dintre puținele documente pe care legea îl acceptă direct ca document justificativ, chiar și pentru operațiuni pentru care Codul fiscal nu cere factură. Fiecare linie a lui — o încasare sau o plată — devine o notă contabilă, în funcție de natura operațiunii.

## Temeiul legal

::: ghid-temei
„Factura este document justificativ care stă la baza înregistrării în contabilitate a operațiunilor economice. Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, extras de cont bancar, notă de contabilitate etc., după caz."
— OMFP nr. 2.634/2015, Norme generale, pct. 25 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Câteva puncte practice pentru înregistrare:

- **Direcția extrasului dă direcția notei**: o linie de credit pe extras (bani intră) devine o încasare; o linie de debit (bani ies) devine o plată.
- **Natura operațiunii determină contul corespondent**: încasare de la un client → 4111; plată către un furnizor → 401; comision bancar → 627; dobândă plătită → 666, dobândă încasată → 766; rambursare credit → 519x.
- Documentele justificative, inclusiv extrasul de cont, **angajează răspunderea** persoanelor care le-au înregistrat în contabilitate (art. 6 alin. (2), Legea nr. 82/1991).
- Contul bancar folosit diferă după valută: 5121 pentru lei, 5124 pentru conturi în valută.

## Ce se greșește în practică

- Se înregistrează toate liniile extrasului direct pe 4111/401, fără să se identifice separat comisioanele, dobânzile sau rambursările de credit, care au conturi corespondente diferite.
- Se confundă sensul „credit"/„debit" al extrasului bancar cu sensul contabil al conturilor — pe extras, „credit" înseamnă bani intrați, nu neapărat creditarea unui cont contabil anume.
- Se așteaptă o factură pentru fiecare operațiune bancară, deși legea acceptă extrasul de cont ca document justificativ suficient, fără factură, pentru operațiunile la care Codul fiscal nu o cere.

## Ce face iConta.eu

iConta.eu detectează automat tipul operațiunii dintr-o linie de extras bancar importat (comision, dobândă, rambursare credit, salarii, TVA, impozit pe profit, transfer intern), pe baza cuvintelor-cheie din descriere, și generează nota contabilă corespunzătoare (de exemplu 627 = 5121 pentru comision, sau 5121 = 4111 pentru o încasare de la client). Când tipul nu poate fi determinat automat, aplicația tratează linia implicit ca operațiune cu un client (la încasare) sau furnizor (la plată), rămânând la latitudinea contabilului să reclasifice dacă e cazul.

[iConta.eu](/)
