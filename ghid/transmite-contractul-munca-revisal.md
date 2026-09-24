---
title: "Cum se transmite contractul de muncă în REVISAL"
description: "Pașii legali pentru transmiterea datelor contractului individual de muncă în registrul general de evidență a salariaților și ce automatizează azi iConta."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se transmite contractul de muncă în REVISAL

Numele „REVISAL" mai circulă des, dar sistemul prin care se transmit azi datele contractului individual de muncă către registrul general de evidență a salariaților se numește **REGES-ONLINE**, sub temeiul HG 295/2025 — actul care a înlocuit vechea HG 905/2017.

## Temeiul legal

::: ghid-temei
„Pentru persoanele care urmează să desfășoare activitate în baza unui contract individual de muncă [...] angajatorii [...] completează și transmit în Registru datele menționate la art. 4 alin. (2), cel târziu în ziua anterioară începerii activității de către aceste persoane."
— HG 295/2025, art. 3 alin. (1) (sursă: anaf_surse/hg_295_2025_reges_online_registru_salariati.txt)
:::

Datele care trebuie completate și transmise sunt enumerate la art. 4 alin. (2): data încheierii contractului, numărul acestuia și data începerii activității (lit. d), funcția/ocupația conform COR (lit. e), durata contractului — nedeterminată/determinată (lit. g), salariul de bază lunar brut, indemnizațiile, sporurile și alte adaosuri (lit. j), printre alte elemente.

Legea permite delegarea operării către un contabil: art. 2 lit. b) include explicit „expertul contabil și contabilul autorizat" în categoria „prestator" care poate efectua completarea și transmiterea. Dar art. 3 alin. (12) este clar că „Răspunderea pentru completarea, transmiterea și corectitudinea datelor transmise în Registru revine în exclusivitate angajatorului", indiferent cine operează efectiv.

## Ce se greșește în practică

- Se caută încă „transmiterea în REVISAL", deși fluxul tehnic actual e prin REGES-ONLINE, cu structură de mesaje și autentificare diferite.
- Se presupune că un singur pas („trimiterea salariatului") acoperă întreg contractul — legea separă datele de identitate a persoanei de elementele propriu-zise ale contractului (număr, dată, salariu, funcție, durată), iar acestea din urmă trebuie completate și transmise separat, conform art. 4 alin. (2).
- Se omite verificarea reală a confirmării din registru înainte de a considera obligația îndeplinită.

## Ce face iConta.eu

Din ecranul **Stat de plată**, pentru fiecare salariat, butonul „REGES" deschide un formular cu un singur câmp suplimentar — adresa salariatului — și trimite către REGES-ONLINE **mesajul de înregistrare a identității salariatului**. Aceasta este, în prezent, singura acțiune pe care aplicația o automatizează efectiv către registru.

Transmiterea propriu-zisă a elementelor contractului (număr, dată, salariu, funcție/COR, durată) **nu este încă cablată** în iConta — codul intern pentru acest tip de mesaj există, dar nu e apelat din niciun buton sau flux vizibil utilizatorului, iar formularul din aplicație nu colectează aceste date. Până la activarea acestei părți, completarea integrală a elementelor contractului în Registru trebuie asigurată prin alte mijloace.

Cheile de acces la REGES-ONLINE (username/parolă per CUI) se obțin din aplicația oficială „REGES Angajator" (Setări → Acces → Chei API), în afara iConta; aplicația doar salvează și folosește chei deja emise, configurabile din același ecran, la butonul „Chei REGES".

Notă: HG 295/2025 a fost contestată în instanță și anulată în primă instanță de Curtea de Apel Constanța; decizia nu e definitivă, iar obligațiile descrise mai sus rămân în vigoare până la o hotărâre finală.

[iConta.eu](/)
