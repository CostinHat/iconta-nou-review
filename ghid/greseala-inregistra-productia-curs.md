---
title: "Greșeala de a nu înregistra producția în curs"
description: "De ce omiterea înregistrării producției în curs de execuție la închiderea perioadei denaturează rezultatul și stocurile din bilanț."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu înregistra producția în curs

Una dintre cele mai frecvente greșeli la închiderea lunii, în firmele cu activitate de producție, este omiterea constatării producției în curs de execuție. Efectul nu este doar formal — el denaturează atât rezultatul lunii, cât și valoarea stocurilor raportate în bilanț.

## Temeiul legal

::: ghid-temei
„Contul 331 „Produse în curs de execuție" [...] este un cont de activ. În debitul contului 331 [...] se înregistrează: – valoarea la cost de producție a stocului de produse în curs de execuție la sfârșitul perioadei, stabilită pe bază de inventar (711). [...] Soldul contului reprezintă valoarea la cost de producție a produselor aflate în curs de execuție la sfârșitul perioadei."
— OMFP 1802/2014, Reglementările contabile, Cap. 16, funcțiunea contului 331 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

De ce omisiunea are un impact real, nu doar formal:

- Contul 711 „Venituri aferente costurilor stocurilor de produse" se creditează exact cu valoarea producției în curs constatate — dacă nu se face nota, **venitul lunii e subevaluat** cu exact această sumă.
- Soldul contului 331 „reprezintă valoarea la cost de producție a produselor aflate în curs de execuție la sfârșitul perioadei" — dacă nota lipsește, **bilanțul nu reflectă real** stocul de producție neterminată la acea dată.
- Efectul se propagă: dacă luna următoare produsele respective sunt finalizate și trec în 345, iar producția în curs nu a fost niciodată constatată, valoarea muncii/materialelor consumate în luna anterioară „dispare" din rezultatul acelei luni, apărând integral abia la finalizare.

## Ce se greșește în practică

- Se consideră constatarea producției în curs o formalitate de sfârșit de an, nu o obligație lunară — de fapt ea se face la sfârșitul **fiecărei** perioade de raportare, stabilită pe bază de inventar.
- Se omite mai ales la firmele mici, unde nu există un proces formal de inventariere lunară a lucrărilor/produselor neterminate.
- Se înregistrează constatarea, dar nu și reluarea (711 = 331) la începutul lunii următoare, dublând eronat valoarea stocului.

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Imobilizări**, operațiunea „Producție (711/345)" generează corect, cu un singur formular, nota de constatare (`331 = 711`) sau de reluare (`711 = 331`), pe baza sumei introduse de contabil în urma inventarului. Mecanismul, testat unitar, respinge orice sumă invalidă (de exemplu negativă sau zero). Notă onestă: greșeala descrisă în acest ghid rămâne, în esență, o **greșeală de proces**, nu una pe care aplicația o poate preveni singură — iConta.eu nu are astăzi o alertă automată care să semnaleze „ați omis producția în curs pentru luna X"; ea execută corect nota odată ce contabilul decide să o introducă.

[iConta.eu](/)
