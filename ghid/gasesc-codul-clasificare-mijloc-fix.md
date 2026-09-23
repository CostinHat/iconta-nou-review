---
title: Cum găsesc codul de clasificare al unui mijloc fix?
description: Codul de clasificare vine din Catalogul HG 2139/2004, căutat succesiv grupă → subgrupă → clasă → subclasă → familie. E un proces manual — nu ține de TVA, ci de stabilirea duratei de amortizare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum găsesc codul de clasificare al unui mijloc fix?

Înainte de precizare: căutarea codului de clasificare nu are legătură cu TVA-ul facturii de achiziție — ține de amortizare, adică de impozitul pe profit și de contabilitate. Codul stabilește plaja de ani (minimă-maximă) din care alegi durata normală de funcționare a activului.

## Temeiul legal

::: ghid-temei
**HG nr. 2139/2004, Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe, cap. I pct. 3**: mijloacele fixe amortizabile sunt clasificate în trei grupe principale: Grupa 1 — Construcții; Grupa 2 — Instalații tehnice, mijloace de transport, animale și plantații; Grupa 3 — Mobilier, aparatură birotică, echipamente de protecție a valorilor umane și materiale și alte active corporale.
:::

## Cum se caută efectiv codul

Catalogul e organizat ierarhic, iar codul de clasificare (de forma „2.2.9" sau „2.3.2.1.1") se citește de sus în jos:

1. **Grupa** — una dintre cele trei de mai sus.
2. **Subgrupa** — subdiviziune tematică în interiorul grupei (ex. în Grupa 2: mașini, utilaje, instalații / mijloace de transport / animale și plantații).
3. **Clasa**, **subclasa** și, unde există, **familia** — nivelurile fine, până ajungi la categoria exactă a activului tău.

Fiecare nivel din catalog are asociată o plajă minim-maximă de ani, valabilă pentru durata normală de funcționare a acelui tip de activ. De exemplu: calculatoarele și echipamentele periferice au 2-4 ani, autoturismele (exceptând taxiurile) 4-6 ani, taxiurile 3-5 ani.

Cel mai sigur mod de a găsi codul e să pornești de la categoria funcțională a activului (ce face, nu cum arată) și să cobori nivel cu nivel, nu să cauți direct un exemplu identic — catalogul are sute de poziții, iar activele noi (tehnologie recentă, de exemplu) nu au întotdeauna un corespondent exact, caz în care se alege cea mai apropiată categorie funcțională.

## Ce se greșește în practică

Se alege o categorie apropiată vizual, dar greșită funcțional — de exemplu un echipament electronic specializat clasificat la „mobilier, aparatură birotică" doar pentru că stă pe un birou, în loc de categoria tehnică reală din Grupa 2. Diferența contează, pentru că plajele de ani diferă semnificativ între grupe.

## Ce face iConta.eu

De precizat clar: acest subiect ține de **registrul de mijloace fixe** (funcționalitatea F247), nu de clasificarea TVA a facturii. Câmpul cu codul de inventar al fiecărui mijloc fix este **text liber**, introdus prin importul de fișier CSV/XLSX — singura cale prin care intră un mijloc fix în aplicație, nu există un formular de adăugare individuală în interfață. Aplicația nu are cablat catalogul HG 2139/2004: nu caută, nu sugerează și nu validează codul introdus față de catalogul oficial, și nici nu avertizează dacă durata aleasă e în afara plajei legale pentru categoria activului. Găsirea codului corect rămâne, la acest moment, un proces complet manual, făcut de contabil direct în catalog, înainte de completarea fișierului de import.

[iConta.eu](/)
