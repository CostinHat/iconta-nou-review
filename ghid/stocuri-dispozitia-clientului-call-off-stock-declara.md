---
title: "Stocuri la dispoziția clientului (call-off stock): cine declară transportul în RO e-Transport?"
description: "Depinde de sens: dacă bunurile vin în România, declară clientul din România; dacă pleacă din România, declară furnizorul din România, inclusiv pentru retururile stocului."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Stocuri la dispoziția clientului (call-off stock): cine declară transportul în RO e-Transport?

În regimul de stocuri la dispoziția clientului, declarantul se stabilește după **sensul transportului**:

- **România este statul de destinație**: declară **clientul din România**. Obligația acoperă bunurile descărcate în țară, bunurile livrate ulterior către altă persoană impozabilă din România și bunurile returnate în statul de origine.
- **România este statul de expediere**: declară **furnizorul din România**. Obligația acoperă bunurile expediate din țară și bunurile returnate în România.

Regula e practică: declară întotdeauna partea stabilită în România, deoarece partenerul din celălalt stat nu are acces la sistem. Codul UIT are o valabilitate extinsă, de 15 zile, pentru că transportul acestor stocuri intră la operațiunile de la art. 2 pct. 9 lit. j).

## Temeiul legal

::: ghid-temei
„Obligația declarării în Sistemul RO e-Transport a datelor prevăzute la art. 4 alin. (1) lit. a) referitoare la transportul internațional de bunuri revine următorilor utilizatori: [...] g) clientului din România, în cazul unor operațiuni comerciale ce se subscriu regimului de stocuri la dispoziția clientului în situația în care România este statul membru către care au fost expediate sau transportate bunurile atât pentru bunurile descărcate pe teritoriul României, cât și pentru bunurile livrate într-un stadiu ulterior după sosire, către altă persoană impozabilă din România sau în cazul în care bunurile respective sunt returnate în statul membru din care au fost expediate sau transportate inițial;"
— OUG 41/2022, art. 8^1 lit. g) (sursă: anaf_surse/oug_41_2022.txt)

„h) furnizorului din România, în cazul unor operațiuni comerciale ce se subscriu regimului de stocuri la dispoziția clientului în situația în care România este statul membru din care au fost expediate sau transportate bunurile atât pentru bunurile expediate din România, cât și în cazul în care bunurile respective sunt returnate în România."
— OUG 41/2022, art. 8^1 lit. h) (sursă: anaf_surse/oug_41_2022.txt)
:::

::: ghid-temei
„(1) Transferul de către o persoană impozabilă de bunuri care fac parte din activele activității sale economice către un alt stat membru în cadrul regimului de stocuri la dispoziția clientului nu este tratat ca o livrare de bunuri efectuată cu titlu oneros."
— Codul fiscal (Legea 227/2015), art. 270^1 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce reține contabilul:

- **Încadrarea în regim** se face după condițiile din art. 270^1 din Codul fiscal: bunurile sunt trimise către un client cunoscut, pe baza unui acord, iar furnizorul nu e stabilit în statul de destinație. RO e-Transport preia această încadrare, nu o stabilește.
- **Fiecare transport rutier se declară separat**: sosirea stocului, livrarea ulterioară către altă persoană impozabilă din țară, dacă presupune un transport rutier, și returul.
- **Valabilitate de 15 zile** pentru codul UIT (art. 11 alin. (2), prin trimitere la art. 2 pct. 9 lit. j)).
- **Orice bunuri**, nu doar cele cu risc fiscal ridicat.

::: ghid-exemplu
Un furnizor din Germania ține la SC Exemplu SRL din Sibiu un stoc de rulmenți în regim de call-off stock. SC Exemplu SRL preia din stoc pe măsura producției.

- Sosirea a 5.000 de rulmenți cu camionul din Germania: SC Exemplu SRL, clientul din România, declară segmentul de la punctul de frontieră Nădlac la depozitul din Sibiu. Codul UIT e valabil 15 zile.
- După 3 luni, 500 de rulmenți nefolosiți se trimit înapoi în Germania: tot SC Exemplu SRL declară returul, pe segmentul Sibiu → Nădlac.

În sens invers, dacă SC Exemplu SRL ar ține un stoc de produse proprii la un client din Ungaria, ea ar declara, ca furnizor din România, expedierea și eventualele retururi.
:::

## Ce se greșește în practică

- **Se așteaptă declarația de la furnizorul străin** al stocului. Când România e statul de destinație, declară clientul român.
- **Se declară doar sosirea stocului.** Retururile se declară și ele, de aceeași parte română.
- **Se tratează sosirea stocului ca achiziție intracomunitară obișnuită.** Declarantul ar ieși la fel, clientul român, dar regimul TVA și evidențele diferă. În plus, livrarea către altă persoană impozabilă din România are regulă proprie.
- **Se aplică valabilitatea de 5 zile.** Pentru stocurile la dispoziția clientului, termenul este de 15 zile.

## Ce face iConta.eu

Pe cardul e-Transport, iConta.eu generează XML-ul notificării, cu tipul de operațiune și scopul aleși de contabil, cu bunurile, partenerul extern, vehiculul și traseul. Aplicația calculează valabilitatea de 15 zile doar pentru operațiunile marcate ca achiziție intracomunitară. Pentru celelalte tipuri calculează prudent 5 zile. Încadrarea în regimul de call-off stock și alegerea tipului de operațiune rămân decizia contabilului.

[iConta.eu](/)
