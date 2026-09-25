---
title: "Cheltuieli cu garanțiile de bună execuție: deductibile"
description: "Condițiile în care provizionul pentru garanții de bună execuție acordate clienților este deductibil la calculul impozitului pe profit, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cheltuieli cu garanțiile de bună execuție: deductibile

Când o firmă acordă clienților o garanție de bună execuție pentru lucrări sau servicii, provizionul constituit pentru eventualele remedieri ulterioare nu este automat deductibil fiscal — legea îl leagă strict de nivelul prevăzut în contract, nu de o estimare liberă.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] b) provizioanele pentru garanții de bună execuție acordate clienților. Provizioanele pentru garanții de bună execuție acordate clienților se deduc trimestrial/anual numai pentru bunurile livrate, lucrările executate și serviciile prestate în cursul trimestrului/anului respectiv pentru care se acordă garanție în perioadele următoare, la nivelul cotelor prevăzute în convențiile încheiate sau la nivelul procentelor de garantare prevăzut în tariful lucrărilor executate ori serviciilor prestate."
— Legea nr. 227/2015 (Codul fiscal), art. 26 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condițiile de deductibilitate, punctate de text:

- Provizionul se deduce doar pentru bunurile livrate, lucrările executate sau serviciile prestate **în perioada de referință** (trimestru/an) pentru care se acordă garanție ulterior — nu retroactiv, pentru lucrări din perioade anterioare nereflectate corespunzător.
- Nivelul deductibil este strict **cota prevăzută în convenția încheiată cu clientul** sau, în lipsă, procentul de garantare din tariful lucrărilor/serviciilor — o cotă estimată discreționar de contabilitate nu are acoperire legală.
- Normele de aplicare cer condiția suplimentară a reflectării integrale la venituri a valorii lucrărilor executate și confirmate de beneficiar (pe bază de situații de lucrări), înainte de a constitui provizionul.

## Ce se greșește în practică

- Se constituie provizionul la o cotă rotunjită sau estimată, fără susținere într-o clauză contractuală sau într-un tarif care să justifice procentul respectiv.
- Se provizionează garanția pentru lucrări facturate, dar neconfirmate încă de beneficiar prin situații de lucrări — condiție cerută explicit de normele metodologice pentru deductibilitate.
- Se uită reluarea la venituri a provizionului pe măsura efectuării cheltuielilor de remediere sau la expirarea perioadei de garanție, lăsând sume provizionate nejustificat pe termen lung.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are o notă de provizion dedicată (`core/provizioane.py`, expusă prin ruta `/tenants/{tenant_id}/nota-provizion`) care, la constituirea unui provizion de tip „garanții" (contul 1512), marchează automat operațiunea ca deductibilă fiscal, spre deosebire de celelalte tipuri de provizioane (litigii, dezafectare, restructurare, altele), pe care le marchează nedeductibile — distincție aplicată conform art. 26 alin. (1) lit. b) din Codul fiscal. Aplicația **nu calculează însă suma provizionului** pornind din cota contractuală sau din tariful lucrărilor — suma se introduce de contabil — și nu verifică dacă procentul aplicat corespunde clauzei contractuale. Constituirea la cota corectă, precum și reluarea provizionului la venituri conform termenelor din contract, rămân operațiuni introduse și urmărite manual de contabil.

[iConta.eu](/)
