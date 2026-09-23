---
title: Cum ies din TVA la încasare dacă am operațiuni intra-UE
description: Operațiunile intracomunitare nu te obligă să ieși din TVA la încasare — doar aceste operațiuni specifice urmează regulile generale de exigibilitate, restul rămân la încasare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum ies din TVA la încasare dacă am operațiuni intra-UE

Titlul întrebării presupune o obligație de ieșire care nu există în lege — a avea operațiuni intracomunitare nu te scoate din sistemul TVA la încasare, doar schimbă regula de exigibilitate pentru acele operațiuni punctuale.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3^1) CF** (condiții de eligibilitate pentru TVA la încasare): eligibile sunt persoanele impozabile înregistrate TVA conform art. 316, cu sediul activității economice în România, a căror cifră de afaceri anul precedent nu a depășit plafonul aplicabil. Nicio condiție de la alin. (3^1) sau de la alin. (4) (neeligibili) nu exclude firmele cu operațiuni intracomunitare. Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17649-17693.

**Art. 282 alin. (6) lit. b) CF**: livrările scutite de TVA (inclusiv livrările intracomunitare scutite, art. 294 alin. 2) nu urmează mecanismul de încasare, ci regulile generale (art. 283 pentru livrări intracomunitare). Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17694-17701.

**Art. 282 alin. (5) CF**: ieșirea voluntară din sistem se face „prin depunerea unei notificări la organul fiscal competent între datele de 1 și 20 ale lunii, cu excepția primului an în care a optat pentru aplicarea sistemului" — condiție generală de ieșire, independentă de tipul operațiunilor derulate. Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17706-17712.
:::

Nu există în Codul fiscal o regulă care să oblige o firmă înscrisă în TVA la încasare să iasă din sistem pentru că a început să facă livrări sau achiziții intracomunitare. Condițiile de eligibilitate și cele de excludere sunt legate strict de înregistrarea TVA, sediul din România și cifra de afaceri față de plafon — nu de tipul operațiunilor.

Ce se schimbă efectiv: livrările intracomunitare scutite de TVA nu mai urmează regula exigibilității la încasare (sunt excluse la alin. 6 lit. b), ci regula proprie de la art. 283 (exigibilitate la data facturii). Restul operațiunilor firmei — vânzările interne, achizițiile locale — continuă normal pe TVA la încasare.

Dacă totuși vrei să ieși voluntar din sistem, indiferent de motiv, procedura e generală: notificare la organul fiscal, depusă între 1 și 20 ale lunii (cu excepția primului an de aplicare), radierea din Registru producându-se din prima zi a perioadei fiscale următoare depunerii notificării.

Atenție să nu confunzi această situație cu o regulă complet diferită: periodicitatea decontului de TVA (lunar/trimestrial, art. 322 din Codul fiscal) chiar este afectată de achizițiile intracomunitare — o firmă cu decont trimestrial care face o achiziție intracomunitară taxabilă trece obligatoriu la decont lunar. Aceasta e însă o regulă separată de TVA la încasare, cu temei legal diferit (art. 322, nu art. 282).

## Ce se greșește în practică

- Se crede, greșit, că apariția unor operațiuni intracomunitare obligă firma să iasă din TVA la încasare — nu există un asemenea temei legal.
- Se confundă regula de periodicitate a decontului TVA (art. 322 — afectată de achizițiile intracomunitare) cu eligibilitatea pentru TVA la încasare (art. 282 — neafectată de operațiuni intracomunitare).
- Se depune o notificare de ieșire inutilă, cu efecte adverse (pierderea opțiunii pentru restul anului calendaristic, conform art. 282 alin. 5), pentru o problemă care nu cerea ieșirea din sistem.

## Ce face iConta.eu

Flagul „operațiuni intracomunitare" (`operatiuni_ic`) e unul dintre cele patru atribute ale vectorului fiscal al firmei (alături de regim fiscal, plătitor TVA și periodicitate), iar flagul „TVA la încasare" (`tva_la_incasare`) e un câmp separat pe profilul firmei, în afara vectorului fiscal propriu-zis — cele două sunt independente, iar activarea unuia nu dezactivează automat celălalt. `core/d300.py` calculează exigibilitatea corect pe fiecare tip de operațiune, aplicând excepția de la alin. (6) doar acolo unde se aplică legal, fără să scoată firma din sistemul TVA la încasare per ansamblu.

[iConta.eu](/)
