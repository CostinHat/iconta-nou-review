---
title: "Cum verifică ANAF e-Factura cu D300 și D394?"
description: "Ce spune legea despre corelarea declarațiilor de TVA cu obligația de depunere D394, ce nu e documentat public despre matching-ul e-Factura, și ce verificări face efectiv iConta.eu, ca aplicație, înainte de depunere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verifică ANAF e-Factura cu D300 și D394?

Aici trebuie separate două lucruri diferite: ce spune legea, explicit, despre corelarea declarațiilor de TVA ale unei firme, și ce anume face ANAF, tehnic, cu datele din sistemul RO e-Factura. Primul e documentat; al doilea, în sursele disponibile pentru acest ghid, nu e detaliat public ca procedură normativă.

## Temeiul legal

::: ghid-temei
„3.1. După primirea declaraţiei, organul fiscal va verifica îndeplinirea obligaţiei de depunere a declaraţiei, prin corelarea informaţiilor referitoare la persoanele impozabile care sunt înregistrate în scopuri de TVA şi au declarat în decontul de TVA numai operaţiuni efectuate pe teritoriul naţional cu informaţiile referitoare la persoanele impozabile care au depus declaraţii informative. 3.2. Pentru persoanele impozabile care nu au depus declaraţiile informative conform pct. 3.1 se emit de către organul fiscal notificări."
— OPANAF 3769/2015, Anexa 3 pct.3.1-3.2 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt:1281-1286)
:::

- Legea confirmă explicit doar corelarea dintre **decontul de TVA (D300)** și **obligația de depunere a D394**: dacă o firmă a declarat în D300 operațiuni exclusiv pe teritoriul național, dar nu a depus și D394, organul fiscal emite notificare.
- Sistemul RO e-Factura (OUG 120/2021) definește, la nivel de principiu, rolul Ministerului Finanțelor de a crea, dezvolta și administra sistemul, inclusiv stocarea electronică a facturilor transmise — ceea ce face posibilă, tehnic, o comparație ulterioară cu alte declarații, dar sursele disponibile nu conțin un text normativ care să descrie explicit metodologia prin care ANAF confruntă datele din e-Factura cu D300 sau D394.
- Concluzie onestă: pentru partea „D300 ↔ obligația de depunere D394", există text de lege citabil verbatim. Pentru partea „e-Factura ↔ D300/D394", nu am găsit în sursele disponibile o procedură publicată — orice afirmație mai detaliată ar fi speculație, nu citat de lege.

## Ce se greșește în practică

- Se presupune că orice diferență între factura transmisă prin e-Factura și cifrele din D300/D394 e detectată și sancționată automat de ANAF în timp real — procedura publicată descrie doar corelarea obligației de depunere D300↔D394, nu un matching linie cu linie al e-Factura.
- Se ignoră riscul notificării automate atunci când firma a raportat în D300 operațiuni interne, dar a omis complet depunerea D394 — acest control e documentat explicit și e cel mai concret risc verificabil din text.
- Se confundă „factura a fost acceptată de sistemul e-Factura" cu „operațiunea a fost validată fiscal în raport cu declarațiile de TVA" — sunt procese diferite.

## Ce face iConta.eu

iConta.eu nu poate replica, și nu pretinde că replică, algoritmul intern de control al ANAF — acela nu e o funcționalitate de aplicație, ci un proces al autorității fiscale. Ce face efectiv aplicația, pe partea ei, sunt trei verificări interne, distincte:

1. **Paritatea D300 ↔ D394**: un test intern (`core/test_d300_d394_paritate.py`) confirmă că TVA colectată pe fiecare cotă coincide între cele două declarații, pentru că ambele se calculează din aceeași sursă — liniile facturilor.
2. **Validare pe validatorul oficial ANAF**, rulată local înainte de a considera fișierul gata de depus (`core/duk.py`).
3. **Corelarea structurală cu e-Factura**: D394 se generează din aceeași tabelă de facturi populată de importul e-Factura (`core/efactura_import.py`) — dar **nu există un modul dedicat** care compară explicit ce a plecat/venit prin e-Factura cu ce a intrat în D394; potrivirea rezultă din sursa comună de date, nu dintr-o funcție separată de „matching".

Depunerea efectivă a D300 și D394 la ANAF rămâne manuală, prin SPV — aplicația nu are vizibilitate asupra propriului proces intern de control al ANAF asupra e-Factura, și nu ar trebui prezentată ca atare.

[iConta.eu](/)
