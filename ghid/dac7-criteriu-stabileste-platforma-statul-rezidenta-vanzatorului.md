---
title: "DAC7: după ce criteriu stabilește platforma statul de rezidență al vânzătorului?"
description: "Criteriul principal e adresa principală. Vânzătorul e considerat rezident și în statul care i-a emis NIF-ul, și în statele unde are sediu permanent declarat, iar un serviciu de identificare poate decide rezidența."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# DAC7: după ce criteriu stabilește platforma statul de rezidență al vânzătorului?

Platforma stabilește rezidența DAC7 în primul rând după adresa principală: vânzătorul e rezident în statul în care se află reședința lui principală, iar o firmă în statul sediului social. La acest criteriu se adaugă alte trei. Vânzătorul e considerat rezident și în statul care i-a emis NIF-ul, dacă acesta diferă de statul adresei, și în statele în care a declarat un sediu permanent. Când identitatea e confirmată printr-un serviciu de identificare al unui stat membru sau al UE, contează statele confirmate de acel serviciu.

Rezidența stabilită de platformă decide unde ajung datele. ANAF le transmite autorității fiecărui stat de rezidență, iar la închirieri și statului în care se află imobilul. Un vânzător poate avea, pentru DAC7, mai multe rezidențe, chiar dacă fiscal se consideră rezident într-un singur stat.

## Temeiul legal

::: ghid-temei
„1. Un Operator de platformă care are obligația de raportare consideră că un Vânzător este rezident în România sau într-un stat membru dacă Adresa Principală a Vânzătorului se află în România sau în statul membru respectiv. 2. În cazul în care Adresa principală a Vânzătorului se află într-un alt stat membru, un Operator de platformă care are obligația de raportare consideră că Vânzătorul este rezident și în România în cazul în care NIF-ul i-a fost emis în România în conformitate cu normele legale în vigoare."
— Codul de procedură fiscală (Legea 207/2015), Anexa nr. 5, secț. II lit. D pct. 1 și 2 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„5. Adresă Principală înseamnă adresa la care se află reședința principală a Vânzătorului care este o persoană fizică, respectiv adresa la care se află sediul social al Vânzătorului care este o Entitate."
— Codul de procedură fiscală (Legea 207/2015), Anexa nr. 5, secț. I lit. C pct. 5 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Cele patru reguli, în ordinea din lege:

1. **Adresa principală (pct. 1).** Pentru persoane fizice, reședința principală. Pentru entități, sediul social. E criteriul de bază.
2. **Statul emitent al NIF-ului (pct. 2).** Dacă adresa e în alt stat membru, dar NIF-ul e emis în România, vânzătorul e rezident și în România. La fel, e rezident și în orice alt stat membru care i-a emis NIF-ul, dacă acesta diferă de statul adresei.
3. **Sediul permanent declarat (pct. 3).** Dacă o entitate a declarat un sediu permanent în România sau în alt stat membru, e considerată rezidentă și acolo, „astfel cum a precizat Vânzătorul”.
4. **Serviciul de identificare (pct. 4).** Prin excepție de la primul criteriu, dacă un serviciu de identificare electronică pus la dispoziție de un stat membru sau de UE confirmă rezidența, vânzătorul e considerat rezident în fiecare stat confirmat.

De reținut:

- **Regulile se cumulează.** Cuvântul „și” din pct. 2 și 3 arată că rezidențele se adaugă una la alta, nu se înlocuiesc.
- **Rezidența DAC7 nu e rezidența fiscală din impozitul pe venit.** Criteriile din anexa nr. 5 servesc raportării și schimbului de informații. Rezidența fiscală a unei persoane se stabilește după regulile proprii din legislația fiscală.
- **Rezidența contează în raport.** Platforma raportează fiecare stat membru în care vânzătorul are rezidență (secț. III lit. B pct. 2 lit. d)). Fiecare dintre acele state primește datele.

::: ghid-exemplu
Trei vânzători pe aceeași platformă:
- Ion Popescu locuiește în Spania, dar are NIF emis în România, declarat pe platformă: rezident DAC7 în Spania, după adresă, și în România, după NIF. Datele lui merg la ambele autorități.
- SC Exemplu SRL are sediul social la Timișoara și un sediu permanent declarat în Ungaria: rezidentă în România și în Ungaria.
- Maria, cu domiciliul la Oradea și doar CNP românesc: rezidentă numai în România.
:::

## Ce se greșește în practică

- Vânzătorul își lasă pe platformă o adresă din străinătate, de la o ședere temporară. Raportarea pleacă spre alt stat, care poate cere clarificări.
- Se crede că rezidența DAC7 decide unde se plătește impozitul. Ea decide doar cine primește informațiile.
- Firma declară un sediu permanent fără să aibă unul, „pentru siguranță”. Declarația produce o rezidență DAC7 suplimentară.
- Se declară pe platformă NIF-uri vechi din alte state, care generează rezidențe pe care vânzătorul nu le mai are.

## Ce face iConta.eu

iConta.eu nu stabilește rezidența DAC7 și nu vede datele declarate de clienți pe platforme. Fișa fiecărei firme din aplicație păstrează datele de identificare (CUI, adresă, număr de la registrul comerțului), care pot fi precompletate din serviciul public ANAF pe baza CUI-ului. Contabilul le poate folosi pentru a verifica dacă datele declarate pe platformă corespund. Pentru partenerii din UE, aplicația verifică în VIES codul de TVA.

[iConta.eu](/)
