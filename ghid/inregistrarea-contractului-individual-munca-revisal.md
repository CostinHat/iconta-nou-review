---
title: "Înregistrarea contractului individual de muncă în REVISAL"
description: "Ce înseamnă azi înregistrarea contractului de muncă în registrul general de evidență a salariaților și cine are obligația să o facă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Înregistrarea contractului individual de muncă în REVISAL

„REVISAL" e numele cu care mulți angajatori și contabili încă recunosc registrul general de evidență a salariaților. Sistemul curent, care a înlocuit vechea platformă REVISAL, se numește **REGES-ONLINE**, iar temeiul legal s-a schimbat odată cu el. Păstrăm „REVISAL" în titlu doar ca termen de căutare — în text vorbim despre sistemul și legea în vigoare azi.

## Temeiul legal

::: ghid-temei
„Prezenta hotărâre stabilește condițiile de întocmire și accesare a Registrului general de evidență a salariaților, denumit în continuare Registru, de completare și transmitere în acesta a elementelor contractului individual de muncă, privind încheierea, modificarea, suspendarea și încetarea acestuia, de către următoarele categorii de angajatori: a) persoane fizice sau juridice de drept privat; ... b) instituții/autorități publice/alte entități juridice care angajează personal în baza unui contract individual de muncă [...]"
— HG 295/2025, art. 1 (sursă: anaf_surse/hg_295_2025_reges_online_registru_salariati.txt)
:::

Vechea Hotărâre de Guvern nr. 905/2017, cea care a dat naștere numelui „REVISAL", este abrogată: art. 15 din HG 295/2025 prevede expres abrogarea ei, cu termenul prelungit ulterior până la 31 decembrie 2025 prin OUG 46/2025. Practic, de la acea dată, obligația de „înregistrare a contractului individual de muncă" se împlinește prin transmiterea datelor în REGES-ONLINE, conform HG 295/2025.

Ce anume se transmite este stabilit tot prin HG 295/2025:

::: ghid-temei
„Angajatorii [...] completează și transmit în Registru următoarele date, fără a avea caracter limitativ: [...] d) data încheierii contractului individual de muncă, numărul acestuia și data începerii activității; ... e) funcția/ocupația, conform specificației Clasificării ocupațiilor din România [...]; ... g) durata contractului individual de muncă, respectiv nedeterminată/determinată; ... j) salariul de bază lunar brut, indemnizațiile, sporurile, precum și alte adaosuri [...]"
— HG 295/2025, art. 4 alin. (2) (sursă: anaf_surse/hg_295_2025_reges_online_registru_salariati.txt)
:::

Termenul pentru transmiterea inițială, la angajare, este stabilit de art. 3 alin. (1): datele se completează și se transmit „cel târziu în ziua anterioară începerii activității" de către persoana angajată.

De reținut și cine poate face efectiv transmiterea: pe lângă angajator, legea recunoaște explicit rolul contabilului sau societății de contabilitate ca „prestator", dar răspunderea rămâne a angajatorului — art. 3 alin. (12): „Răspunderea pentru completarea, transmiterea și corectitudinea datelor transmise în Registru revine în exclusivitate angajatorului", chiar și atunci când operarea e delegată contabilului.

## Ce se greșește în practică

- Se folosește în continuare termenul „REVISAL" ca și cum ar fi sistemul activ — legea și API-ul curent poartă numele REGES-ONLINE.
- Se crede că „înregistrarea contractului" înseamnă transmiterea tuturor elementelor contractului (număr, dată, salariu, COR, normă) într-un singur pas automat — de fapt, legea impune transmiterea datelor, dar cine și cum le transmite tehnic depinde de instrumentul folosit, iar nu orice instrument acoperă azi toate câmpurile.
- Se presupune că delegarea către contabil (art. 2 lit. b) scutește firma de răspundere — art. 3 alin. (12) spune explicit contrariul.

## Ce face iConta.eu

Astăzi, iConta.eu trimite către REGES-ONLINE **doar mesajul de înregistrare a identității salariatului** (nume, prenume, CNP etc.), din ecranul **Stat de plată**, de la butonul „REGES" aflat pe rândul fiecărui salariat — unde se completează un singur câmp suplimentar, adresa salariatului.

Transmiterea automată a elementelor propriu-zise ale contractului (numărul contractului, data, salariul, funcția/COR, norma) **nu este încă activă** în aplicație, deși motorul de mesaje pentru acest tip de transmitere există în codul intern al iConta — pur și simplu nu este conectat la niciun buton sau flux vizibil utilizatorului. Până la activarea sa, completarea integrală a elementelor contractului în Registru rămâne responsabilitatea directă a angajatorului sau a contabilului care operează, prin celelalte canale disponibile.

Notă: HG 295/2025 a fost contestată în instanță și anulată în primă instanță de Curtea de Apel Constanța; decizia nu este definitivă, iar obligațiile descrise mai sus rămân în vigoare până la o hotărâre finală.

Accesul tehnic la REGES-ONLINE (username/parolă per CUI) se obține din aplicația oficială „REGES Angajator" (Setări → Acces → Chei API), în afara iConta; iConta doar preia și folosește aceste chei deja emise.

[iConta.eu](/)
