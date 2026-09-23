---
title: "Cum deleg accesul la e-Factura către contabil"
description: „Delegarea" accesului la e-Factura nu e un buton într-o aplicație de facturare — e o împuternicire generală, înregistrată la ANAF, prin care contabilul capătă drept SPV pe firma ta. Fără ea, nicio aplicație nu poate transmite facturi în numele tău.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum deleg accesul la e-Factura către contabil

Termenul „deleg" descrie bine ce se întâmplă, dar procedura nu se petrece într-o aplicație de facturare — se petrece la ANAF, prin SPV, și are reguli stricte de conținut, nu doar de formă.

## Temeiul legal

::: ghid-temei
„Utilizarea SPV prin împuternicit sau prin reprezentantul desemnat este posibilă dacă îndeplinește, cumulativ, următoarele condiții: a) împuternicirea sau mandatul de reprezentare este generală/general pentru toate operațiunile din SPV; b) împuternicirea sau mandatul de reprezentare conține acordul cu privire la accesul la informațiile referitoare la istoricul acțiunilor anterioare din SPV al persoanei reprezentate; c) sunt acceptați termenii și condițiile de utilizare a SPV." — OMFP nr. 660/2017 privind aprobarea Procedurii de comunicare prin mijloace electronice de transmitere la distanță, art. 15 alin. (9)
:::

„Delegarea" către contabil pentru e-Factura nu poate fi parțială — legea nu permite o împuternicire limitată doar la facturi, ci cere caracter general, pentru toate operațiunile din SPV, plus acordul explicit de acces la istoricul acțiunilor anterioare ale firmei.

## Cum se face, în practică

1. Cererea de împuternicire se depune prin aplicația SPV (art. 16 din OMFP 660/2017), cu datele contabilului, calitatea lui (împuternicit sau reprezentant desemnat, dacă e angajat al firmei), telefon mobil valid și acceptul termenilor de utilizare.
2. ANAF verifică cererea — automat, dacă datele se pot valida în sistem, sau la ghișeu, cu prezentare fizică și verificarea semnăturii olografe, dacă nu (art. 17). Termenele legale sunt 2 zile lucrătoare (documente autentice) sau 5 zile lucrătoare (documente neautentice) de la prezentare/înregistrare.
3. Rezultatul (aprobare sau respingere) se comunică prin SPV, atât solicitantului, cât și firmei reprezentate.
4. Odată aprobată, împuternicirea rămâne valabilă până la revocare — o cerere similară, depusă tot prin SPV (art. 18-19).

Distincția importantă: împuternicirea de mai sus dă contabilului **dreptul legal** de a acționa în SPV pentru firma ta. Ea nu configurează, singură, nicio aplicație de facturare — aplicațiile care folosesc conexiunea contabilului la SPV (inclusiv iConta.eu) verifică ulterior, tehnic, dacă acest drept chiar există pe CIF-ul tău, prin cereri directe către ANAF.

## Ce se greșește în practică

- Se caută opțiunea de „delegare" într-o aplicație de facturare — nu există, pentru că delegarea e o procedură legală ANAF, nu o setare de produs.
- Se scrie o împuternicire restrânsă („doar pentru e-Factura" sau „doar pentru anumite luni"), crezând că e mai sigură — de fapt, o astfel de împuternicire se respinge, pentru că legea cere caracter general.
- Se presupune că, odată împuternicit contabilul pe firma A, dreptul se extinde automat și pe orice altă firmă a aceluiași contabil — dreptul e legat de firma pentru care a fost aprobată cererea, nu de contabil în general.

## Ce face iConta.eu

Procedura de împuternicire propriu-zisă are loc integral la ANAF, prin SPV — iConta.eu nu o inițiază și nu o poate finaliza. Ce face iConta.eu este partea de după: odată recunoscut dreptul de către ANAF pe certificatul contabilului, conexiunea SPV a cabinetului (autorizată o singură dată, cu certificatul contabilului) acoperă automat orice firmă-client pentru care acest drept există — fără o „delegare" tehnică suplimentară în aplicație. Aplicația verifică existența dreptului empiric, per CIF, direct din răspunsul ANAF.

[iConta.eu](/)
