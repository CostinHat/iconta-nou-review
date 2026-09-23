---
title: "Greșeli specifice firmelor cu TVA la încasare"
description: "Cele mai frecvente confuzii legale și practice ale firmelor înscrise în sistemul TVA la încasare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeli specifice firmelor cu TVA la încasare

Sistemul TVA la încasare pare simplu — „plătesc TVA când sunt plătit" — dar în practică apar câteva confuzii recurente, unele cu consecințe fiscale directe.

## Temeiul legal

::: ghid-temei
Art. 291 alin. (5) Cod fiscal: „În cazul operațiunilor supuse sistemului TVA la încasare, cota aplicabilă este cea în vigoare la data la care intervine faptul generator, cu excepția situațiilor în care este emisă o factură sau este încasat un avans, înainte de data livrării/prestării, pentru care se aplică cota în vigoare la data la care a fost emisă factura ori la data la care a fost încasat avansul." (`cod_fiscal_227_2015_consolidat.txt`, liniile 18151-18159)
:::

**1. Confuzia dintre exigibilitate și cota aplicabilă.** Art. 282 stabilește CÂND devine exigibilă TVA (la încasare), iar art. 291 alin. (5) stabilește CE COTĂ se aplică — două reguli distincte. Cota nu e neapărat cea de la data încasării, ci cea de la faptul generator, cu excepție pentru facturi/avansuri emise anterior livrării.

**2. Tratarea taxării inverse ca fiind sub TVA la încasare.** Art. 282 alin. (6) exclude explicit taxarea inversă (art. 307 alin. 2-6 sau art. 331), livrările scutite, regimurile speciale (art. 311-313) și livrările către afiliați din mecanismul de încasare — chiar dacă firma e înscrisă în sistem. Pentru aceste operațiuni, exigibilitatea rămâne la faptul generator.

**3. Mitul celor „90 de zile".** Circulă afirmația că TVA devine exigibilă forțat la 90 de zile de la emiterea facturii, chiar fără încasare. Textul integral al art. 282 (alin. 1-11), verificat direct în `cod_fiscal_227_2015_consolidat.txt`, **nu conține nicio regulă de exigibilitate forțată la 90 de zile** — acea regulă a existat în legislația anterioară anului 2013, dar nu mai apare în forma consolidată actuală. Această afirmație, dacă e întâlnită, nu ar trebui luată ca temei fără verificare suplimentară la sursă oficială.

**4. Presupunerea unei verificări automate a Registrului ANAF.** Faptul că un furnizor aplică TVA la încasare se verifică oficial în Registrul public organizat de ANAF (art. 324 alin. 16), nu doar pe baza declarației furnizorului de pe factură.

## Ce se greșește în practică

Pe lângă cele de mai sus, o greșeală practică frecventă la introducerea unei facturi/avans e alegerea greșită sau omisă a ramurii prevăzute de art. 291 alin. (5) — adică nu se stabilește dacă factura/avansul a fost emis(ă) înainte de livrare sau după. Consecința e o cotă de TVA calculată greșit.

## Ce face iConta.eu

Modulul `core/cota_tva_incasare.py` **nu deduce automat** care document (factură/avans sau livrare) a fost primul — contabilul trebuie să aleagă manual ramura (`ramura_291_5`), decizie de produs explicită pentru că „a ghici ar produce o cifră validă și falsă". Modulul refuză explicit patru situații: lipsă dată fapt generator, ramură nealeasă, lipsă dată document pe ramura excepție, document ulterior livrării. Ecranul „TVA la încasare (art. 282)" afișează un text de ajutor care citează direct art. 291 alin. (5). Pe factura de achiziție, bifa „furnizor TVA la încasare" e însă complet manuală — aplicația nu verifică live Registrul public ANAF, bifa fiind pe răspunderea contabilului.

[iConta.eu](/)
