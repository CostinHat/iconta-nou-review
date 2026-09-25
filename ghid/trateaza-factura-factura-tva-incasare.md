---
title: "Cum se tratează o factură din e-Factura la TVA la încasare?"
description: "Ce trebuie să verifice și să decidă contabilul când primește prin e-Factura o factură de la un furnizor înscris la TVA la încasare, și cum se amână dreptul de deducere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se tratează o factură din e-Factura la TVA la încasare?

Din perspectiva cumpărătorului, o factură primită prin RO e-Factura de la un furnizor care aplică TVA la încasare are o singură consecință practică majoră: dreptul de deducere a TVA nu se exercită la primirea facturii, ci abia atunci când furnizorul e plătit. Recunoașterea corectă a acestei situații depinde de o informație pe care XML-ul facturii, singur, nu o garantează întotdeauna.

## Temeiul legal

::: ghid-temei
„Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare conform prevederilor art. 282 alin. (3)-(8) [...] este amânat până în momentul în care taxa aferentă bunurilor și serviciilor care i-au fost livrate/prestate a fost plătită furnizorului/prestatorului său, chiar dacă o parte din operațiunile realizate de persoana impozabilă sunt excluse de la aplicarea sistemului TVA la încasare conform art. 282 alin. (6)."
— Codul fiscal, art. 297 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Amânarea deducerii se aplică indiferent dacă firma cumpărătoare aplică ea însăși TVA la încasare sau nu — ce contează e regimul **furnizorului**.
- Regula are efect chiar și pentru operațiunile pe care furnizorul le exclude altfel din sistemul TVA la încasare (art. 282 alin. 6 — taxare inversă, scutiri, regimuri speciale) — excluderea furnizorului nu anulează automat amânarea la beneficiar.
- Marcajul legal pe care ar trebui să se bazeze această verificare e mențiunea "TVA la încasare" de pe factură (art. 319 alin. 20 lit. p)); în lipsa ei, cumpărătorul poate verifica statutul furnizorului direct în Registrul public al persoanelor care aplică sistemul TVA la încasare, organizat de ANAF (art. 324 alin. 16).
- Deducerea amânată nu se pierde — se exercită pur și simplu mai târziu, la data plății, nu la data facturii.

## Ce se greșește în practică

- Se deduce TVA imediat la primirea facturii prin e-Factura, pentru că sistemul a validat structura XML — validarea tehnică a facturii nu confirmă și regimul de TVA al furnizorului, care e o informație separată.
- Se presupune că absența mențiunii "TVA la încasare" pe factură înseamnă cu certitudine că furnizorul nu e în acest regim — mențiunea poate lipsi din eroare, mai ales dacă furnizorul folosește un generator de facturi care omite mențiunea (o situație reală, nu ipotetică).
- Se aplică regula de amânare doar facturilor mari, considerând-o "prea complicată" pentru sume mici — legea nu prevede niciun prag valoric pentru art. 297 alin. (2).
- Se contabilizează factura automat, fără cont de cheltuială ales explicit și fără decizie asupra regimului furnizorului, riscând o notă contabilă care nu reflectă corect nici cheltuiala, nici TVA-ul deductibil.

## Ce face iConta.eu

Facturile primite prin RO e-Factura (funcționalitatea F126) intră mai întâi ca ciorne (`efactura_primite`), cu datele extrase automat din XML (număr, dată, părți, total, TVA, linii) — parserul (`core/efactura_import.py`) nu citește însă nicio mențiune de "TVA la încasare" din document, pentru simplul motiv că standardul UBL folosit de aplicație nu prevede un câmp dedicat pentru ea și generatorul iConta.eu însuși nu o scrie (vezi ghidul despre transmiterea facturilor la TVA la încasare în e-Factura).

Validarea unei facturi primite e un pas separat, de tip "patru ochi": mașina propune datele parsate, iar contabilul confirmă — și la acest pas, aplicația **cere explicit** contul de cheltuială (obligatoriu, fără implicit) și clasificarea "furnizor cu TVA la încasare" (checkbox `furnizor_tva_incasare`), care declanșează în `core/d300.py` amânarea deducerii conform art. 297 alin. (2). Verificat direct în cod: pentru facturile create manual (nu prin e-Factura), aplicația verifică automat statutul furnizorului la ANAF (`core/anaf_api.py`, funcția `furnizor_incasare_freeze`, folosind serviciul public RTVAI) la momentul introducerii facturii, cu fallback pe bifa contabilului dacă interogarea eșuează — dar pe calea de validare a facturilor primite prin e-Factura, bifa e cea pe care o confirmă contabilul manual în ecranul de validare, fără acest apel automat la ANAF. E o diferență reală, la nivel de cod, între cele două fluxuri de introducere a facturii, pe care contabilul care lucrează cu e-Factura trebuie s-o cunoască: verificarea la Registrul ANAF, pentru facturile primite prin e-Factura, rămâne responsabilitatea lui, nu a aplicației. Dacă situația e ambiguă, iConta.eu refuză să scrie automat nota contabilă (mai degrabă decât să ghicească), lăsând contarea manuală pentru acel caz.

[iConta.eu](/)
