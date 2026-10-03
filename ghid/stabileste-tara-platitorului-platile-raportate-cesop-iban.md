---
title: "Cum se stabilește țara plătitorului la plățile raportate în CESOP: IBAN sau BIC?"
description: "Întâi după IBAN-ul contului plătitorului sau alt identificator care îi arată locația. Doar în lipsa acestora se folosește BIC-ul prestatorului de plăți care acționează în numele plătitorului."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Cum se stabilește țara plătitorului la plățile raportate în CESOP: IBAN sau BIC?

Țara plătitorului se stabilește **mai întâi după IBAN-ul contului de plăți al plătitorului** sau după orice alt identificator care arată fără echivoc locația acestuia. **Numai în lipsa unor astfel de identificatori** se folosește **codul BIC**, sau alt cod comercial, al prestatorului de servicii de plată care acționează în numele plătitorului. Ordinea este fixă: BIC-ul e o soluție de rezervă, nu o alternativă la alegere.

Locația plătitorului decide dacă o plată este transfrontalieră. Transfrontalieră înseamnă că plătitorul se află într-un stat membru, iar beneficiarul în altul sau în afara UE. Același criteriu stabilește statul de origine care apare în evidență.

## Temeiul legal

::: ghid-temei
„(9) În aplicarea alin. (3) și fără a aduce atingere prevederilor capitolului V din prezentul titlu, locația plătitorului se consideră a fi în statul membru care corespunde: a) codului IBAN al contului de plăți al plătitorului sau oricărui alt identificator care identifică fără echivoc și furnizează locația plătitorului sau în absența unor astfel de identificatori; ... b) codului BIC sau oricărui alt cod de identificare comercială care identifică fără echivoc și furnizează locația prestatorului de servicii de plată care acționează în numele plătitorului."
— Codul fiscal (Legea 227/2015), art. 321^2 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(10) În aplicarea alin. (3) , locația beneficiarului plății se consideră a fi în statul membru, în teritoriul terț sau în țara terță care corespunde: a) codului IBAN al contului de plăți al beneficiarului plății sau oricărui alt identificator care identifică fără echivoc și furnizează locația beneficiarului plății sau în absența unor astfel de identificatori; ... b) codului BIC sau oricărui alt cod de identificare comercială care identifică fără echivoc și furnizează locația prestatorului de servicii de plată care acționează în numele beneficiarului plății."
— Codul fiscal (Legea 227/2015), art. 321^2 alin. (10) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă:

- **Regula principală:** IBAN-ul plătitorului sau alt identificator care îi arată fără echivoc locația. Codul de țară din IBAN indică statul membru.
- **Regula de rezervă:** BIC-ul prestatorului care acționează pentru plătitor, folosit doar când primul criteriu lipsește.
- **Aceeași logică pentru beneficiar:** IBAN-ul beneficiarului, apoi BIC-ul prestatorului său (alin. (10)). Pentru beneficiar, locația poate fi și un teritoriu terț sau o țară terță.
- **Domeniul de aplicare:** criteriul servește alin. (3), adică stabilirii caracterului transfrontalier al plății, și se aplică „fără a aduce atingere prevederilor capitolului V", care privesc locul operațiunilor.
- **Ce se raportează:** statul de origine al plății și informațiile folosite pentru a-l stabili fac parte din detaliile fiecărei plăți (alin. (12) lit. c)).

Consecință practică: locația plătitorului din evidența băncii nu stabilește locul livrării sau al prestării în sens TVA. Locul operațiunii se stabilește după regulile din capitolul V al titlului VII din Codul fiscal (Legea 227/2015). Dacă cele două diferă, firma își justifică tratamentul fiscal cu documentele tranzacției.

::: ghid-exemplu
SC Exemplu SRL, cu cont în România, primește în octombrie 2026 trei plăți:

1. un transfer din contul unui client cu IBAN care începe cu „AT": plătitorul este localizat în Austria, iar plata este transfrontalieră;
2. o plată cu cardul, pentru care prestatorul nu are IBAN-ul plătitorului sau alt identificator al locației, dar BIC-ul prestatorului plătitorului indică Italia: plătitorul este localizat în Italia;
3. un transfer de la un client cu IBAN care începe cu „RO", deși clientul locuiește în Spania: după IBAN, plătitorul este localizat în România, deci plata nu este transfrontalieră pentru o firmă din România.

Dacă în cazul 3 SC Exemplu SRL vinde de fapt la distanță în Spania, locul livrării se stabilește după capitolul V din Codul fiscal, nu după IBAN-ul clientului.
:::

## Ce se greșește în practică

- Se presupune că banca localizează plătitorul după adresa de livrare din comandă, nu după IBAN.
- BIC-ul se folosește înaintea IBAN-ului, deși este doar criteriu de rezervă.
- Locația plătitorului din evidența băncii se confundă cu locul operațiunii pentru TVA.
- Plățile clienților străini cu conturi românești sunt tratate automat ca transfrontaliere.

## Ce face iConta.eu

iConta.eu importă extrasele bancare ale firmei, inclusiv în format MT940, și propune contări pentru încasările de la parteneri. Aplicația nu stabilește locația plătitorului după IBAN sau BIC în sensul art. 321^2 și nu are acces la evidențele transmise de prestatorii de plăți. Pe factura emisă se completează țara clientului și tipul operațiunii, care dirijează rândul din decontul D300. Contabilul verifică această clasificare pe documentele tranzacției, nu pe datele de plată.

[iConta.eu](/)
