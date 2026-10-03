---
title: "DAC8: ce raportează la ANAF platformele de criptomonede despre clienți?"
description: "Datele de identificare ale clientului (nume, adresă, rezidență, NIF, data și locul nașterii) și, pe fiecare criptoactiv, totalurile anuale: sume, unități și număr de tranzacții."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# DAC8: ce raportează la ANAF platformele de criptomonede despre clienți?

Furnizorii de servicii de criptoactive cu obligație de raportare transmit la ANAF, pentru fiecare an calendaristic, două categorii de informații despre clienții lor raportabili. Prima categorie este identitatea: nume, adresă, statul sau statele de rezidență, numărul de identificare fiscală și, pentru persoane fizice, data și locul nașterii. A doua categorie sunt tranzacțiile, raportate agregat pe fiecare tip de criptoactiv, nu tranzacție cu tranzacție: sume totale, număr de unități și număr de tranzacții, separat pe categorii de operațiuni.

Pentru un client, asta înseamnă că vânzările de criptomonede contra lei sau euro, schimburile între criptomonede și transferurile ajung într-o raportare anuală. ANAF o comunică statului de rezidență, potrivit art. 291^6. Primele informații privesc anul 2026.

## Temeiul legal

::: ghid-temei
„1. în cazul unei persoane fizice care este un utilizator care face obiectul raportării: numele, adresa, statul membru (statele membre)/jurisdicția (jurisdicțiile) de rezidență, numărul (numerele) de identificare fiscală (NIF), data și locul nașterii."
— Codul de procedură fiscală (Legea 207/2015), anexa nr. 6, secțiunea II, subsecțiunea B pct. 1 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„2. suma brută agregată plătită, numărul agregat de unități și numărul de Tranzacții care fac obiectul raportării în contextul achizițiilor în schimbul monedei fiduciare; 3. suma brută agregată încasată, numărul agregat de unități și numărul de Tranzacții care fac obiectul raportării în contextul vânzărilor în schimbul monedei fiduciare;"
— Codul de procedură fiscală (Legea 207/2015), art. 291^6 alin. (3) lit. c) pct. 2 și 3 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Lista completă, pe fiecare tip de criptoactiv cu care furnizorul a lucrat pentru client în anul respectiv (anexa nr. 6, secțiunea II, subsecțiunea B pct. 3):

1. **denumirea completă** a criptoactivului;
2. **cumpărări contra monedă fiduciară**: suma brută agregată plătită, unitățile și numărul de tranzacții;
3. **vânzări contra monedă fiduciară**: suma brută agregată încasată, unitățile și numărul de tranzacții;
4. **cumpărări contra altor criptoactive**: valoarea justă de piață agregată, unitățile și numărul de tranzacții;
5. **vânzări contra altor criptoactive**: aceleași elemente;
6. **plăți cu amănuntul** în criptoactive: valoarea justă de piață agregată, unitățile și numărul de tranzacții;
7. **transferuri către client și transferuri de la client** care nu intră în categoriile de mai sus, defalcate pe tipuri de transfer, dacă furnizorul le cunoaște;
8. **transferuri către adrese de portofel** despre care nu se știe că ar fi asociate cu un furnizor de servicii de active virtuale sau cu o instituție financiară.

Reguli de calcul de reținut:

- **Fără comisioane.** La tranzacțiile contra monedă fiduciară se raportează suma plătită sau încasată de client, fără comisioanele de tranzacție (anexa nr. 6, secțiunea II, B.1 pct. 4).
- **Moneda.** Sumele în monedă fiduciară se raportează în moneda în care au fost plătite sau încasate. Dacă au fost folosite mai multe monede, se raportează într-una singură, convertită la momentul fiecărei tranzacții. Pentru fiecare sumă se indică moneda folosită.
- **Valoarea justă.** La operațiunile criptoactiv contra criptoactiv, plăți și transferuri, valoarea justă de piață se determină într-o singură monedă fiduciară, la momentul fiecărei tranzacții.
- **Entități.** Pentru o entitate client cu persoane care exercită controlul și care sunt raportabile se raportează datele entității și datele fiecărei astfel de persoane, inclusiv rolul ei (anexa nr. 6, secțiunea II, B pct. 1).
- **NIF.** Raportarea NIF nu este obligatorie dacă jurisdicția de rezidență nu emite NIF sau dacă dreptul ei intern nu impune colectarea lui (anexa nr. 6, secțiunea II, B pct. 4).

Raportabil este clientul rezident într-un stat membru sau într-o jurisdicție calificată din afara Uniunii Europene (anexa nr. 6, secțiunea IV).

::: ghid-exemplu
Ion Popescu, client persoană fizică al unei platforme care raportează la ANAF, face în 2026 următoarele operațiuni cu bitcoin:

- 3 cumpărări contra lei, pentru 30.000 lei în total, plus comisioane de 300 lei;
- 2 vânzări contra lei, pentru 42.000 lei încasați în total;
- 1 schimb de bitcoin contra ether, cu o valoare justă de 8.000 lei.

Pentru bitcoin, platforma raportează: cumpărări contra monedă fiduciară, 30.000 lei, 3 tranzacții și numărul de unități (comisioanele de 300 lei nu se includ); vânzări contra monedă fiduciară, 42.000 lei, 2 tranzacții și numărul de unități; vânzări contra alte criptoactive, 8.000 lei, 1 tranzacție. Pentru ether apare, separat, o cumpărare contra alte criptoactive de 8.000 lei. La toate se adaugă datele de identificare ale lui Ion Popescu.
:::

## Ce se greșește în practică

- Se presupune că raportarea DAC8 cuprinde fiecare tranzacție în parte. Legea cere totaluri agregate pe tip de criptoactiv și pe categorii.
- Schimburile criptoactiv contra criptoactiv sunt considerate „invizibile" pentru că nu implică lei. Ele se raportează la valoarea justă de piață.
- Clientul presupune că doar vânzările contra lei contează. Se raportează și cumpărările, plățile cu amănuntul și transferurile.
- Comisioanele sunt incluse în suma raportată, deși regula este raportarea fără comisioanele de tranzacție.

## Ce face iConta.eu

iConta.eu nu întocmește raportarea DAC8 a furnizorilor. Importul de extrase din aplicație acoperă extrasele bancare (fișiere de la bancă), nu rapoartele platformelor de criptoactive. Operațiunile cu criptoactive se înregistrează de contabil, pe baza documentelor primite de la platformă.

[iConta.eu](/)
