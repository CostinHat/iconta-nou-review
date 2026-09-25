---
title: "Cum se contabilizează veniturile unei firme IT din proiecte cu preț fix?"
description: "Mecanismul contului 332 „Servicii în curs de execuție" din OMFP 1802/2014 — cum se evidențiază, la final de perioadă, un proiect IT facturat la preț fix, dar nefinalizat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează veniturile unei firme IT din proiecte cu preț fix?

Un proiect IT cu preț fix se întinde adesea pe mai multe luni sau chiar peste sfârșitul unui exercițiu financiar, iar factura finală se emite abia la livrare sau la recepție. Între timp, firma a suportat costuri (salarii, subcontractare) fără să fi recunoscut încă venitul corespunzător — situație pentru care reglementările contabile prevăd un cont dedicat.

## Temeiul legal

::: ghid-temei
„Contul 332 «Servicii în curs de execuție». Cu ajutorul acestui cont se ține evidența serviciilor în curs de execuție existente la sfârșitul perioadei. Contul 332 «Servicii în curs de execuție» este un cont de activ. În debitul contului 332 «Servicii în curs de execuție» se înregistrează: – valoarea la cost de producție a serviciilor în curs de execuție la sfârșitul perioadei (712). [...] În creditul contului 332 «Servicii în curs de execuție» se înregistrează: – scăderea din gestiune a valorii serviciilor în curs de execuție la începutul perioadei următoare (712). [...] Soldul contului reprezintă valoarea la cost de producție a serviciilor în curs de execuție la sfârșitul perioadei."
— OMFP 1802/2014 (Reglementări contabile), Funcțiunea conturilor, Grupa 33 „Producție în curs de execuție", contul 332 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

**Notă de onestitate:** reglementările contabile consultate nu conțin un articol dedicat, cu titlul „proiecte IT" sau „preț fix", și nici o metodă explicită de recunoaștere a veniturilor „pe stadiu de execuție" (percentage of completion) pentru servicii. Ce prevede efectiv OMFP 1802/2014, și care e cel mai apropiat temei real aplicabil, e mecanismul general al contului 332, valabil pentru orice serviciu aflat în curs la finalul unei perioade — inclusiv, prin extensie, un proiect IT cu preț fix nefinalizat:

- La sfârșitul perioadei (lună, trimestru sau an), dacă proiectul nu e finalizat și nu s-a emis factura convenită, costurile deja suportate (manopera dezvoltatorilor, subcontractare, licențe alocate proiectului) **nu se recunosc drept cheltuială a perioadei fără contrapartidă** — ele se reflectă la activ, în contul 332, prin creditarea contului de venit 712 „Venituri din producția de servicii în curs de execuție".
- La începutul perioadei următoare, soldul din 332 se **scade din gestiune** (tot prin 712), pentru a nu dubla evidența — iar ciclul se reia dacă proiectul rămâne nefinalizat și la finalul acelei perioade.
- Când proiectul se **finalizează și se facturează** clientului, se face înregistrarea obișnuită de vânzare a unui serviciu — de regulă **4111 = 704 + 4427** (client = venituri din servicii prestate + TVA colectată) — moment în care venitul „real", generator de TVA și de rezultat fiscal, se recunoaște efectiv.
- Contul 332 e, deci, un instrument de **evidențiere internă la cost**, între perioade contabile, nu un substitut al facturii — el nu generează TVA și nu ține loc de venit impozabil; rolul lui e să evite ca o perioadă contabilă cu muncă depusă, dar nefacturată, să arate cheltuieli fără nicio contrapartidă de venit.

## Ce se greșește în practică

- Se lasă costurile unui proiect IT nefinalizat direct pe cheltuieli de perioadă (salarii, subcontractare), fără nicio recunoaștere a contravalorii muncii deja prestate prin contul 332 — rezultatul lunii/trimestrului arată artificial mai slab decât realitatea economică a proiectului.
- Se confundă înregistrarea prin contul 332 (evidență internă, la cost de producție, fără TVA) cu emiterea unei facturi parțiale către client — sunt operațiuni complet diferite, iar prima nu înlocuiește niciodată obligația de facturare la momentul convenit contractual.
- Se uită scăderea din gestiune a soldului din 332 la începutul perioadei următoare, ceea ce duce la dublarea valorii serviciilor în curs atunci când proiectul continuă și se reface înregistrarea pentru noua perioadă.

## Ce face iConta.eu

iConta.eu oferă contabilitate generală pentru firme, inclusiv posibilitatea de a înregistra note contabile manuale prin contul 332, dacă firma alege să evidențieze la final de lună costurile unui proiect nefinalizat. Aplicația nu are un motor dedicat de „project accounting" care să calculeze automat, pe baza orelor lucrate sau a stadiului de livrare al unui proiect IT, valoarea de trecut în contul 332 — stabilirea costului de producție al serviciilor în curs și decizia de a le evidenția astfel rămân în sarcina contabilului, pe baza documentelor interne ale proiectului.

[iConta.eu](/)
