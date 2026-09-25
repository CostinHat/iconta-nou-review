---
title: "Se declară facturile simplificate în D394?"
description: "Regimul facturilor simplificate (sub 100 euro sau emise fără CUI-ul cumpărătorului) în declarația 394 și stadiul real al suportului lor în iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară facturile simplificate în D394?

Factura simplificată — cea emisă pentru sume mici sau în situațiile speciale prevăzute de Codul fiscal — nu dispare din D394, dar nici nu se amestecă în aceleași rânduri cu facturile obișnuite. Legea îi rezervă câmpuri separate, distincte de tipurile L/A folosite pentru facturile „normale".

## Temeiul legal

::: ghid-temei
„Persoana impozabilă care are obligaţia de a emite facturi conform prezentului articol, precum şi persoana impozabilă care optează pentru emiterea facturii potrivit alin. (11) pot emite facturi simplificate în oricare dintre următoarele situaţii: a) atunci când valoarea facturilor, inclusiv TVA, nu este mai mare de 100 euro. [...]"
— Legea 227/2015 (Codul fiscal), art. 319 alin. (12) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„L - livrări de bunuri/prestări de servicii pentru care au fost emise facturi, cu excepţia facturilor simplificate; A - achiziţii de bunuri/servicii pentru care au fost primite facturi, cu excepţia facturilor simplificate."
— OPANAF 2194/2025, Anexa 2 (sursă: anaf_surse/opanaf_2194_2025_d394.txt:1168-1169)
:::

- Facturile simplificate **se declară**, dar nu la tipurile L/A din secțiunile C-F ale declarației — acestea le exclud explicit.
- Ele apar în schimb la secțiunea „Alte informații": defalcat pe cotă de TVA, separat după cum au sau nu au înscris CUI-ul beneficiarului (livrări), respectiv după cum furnizorul aplică sistemul normal sau TVA la încasare (achiziții).
- Aceeași separare se aplică bonurilor fiscale care întrunesc condițiile unei facturi simplificate (emise prin case de marcat electronice fiscale).

## Ce se greșește în practică

- Se presupune că facturile simplificate nu intră deloc în D394, pentru că nu apar la rândurile L/A obișnuite — de fapt trebuie raportate separat, pe cotă de TVA.
- Se confundă „factură simplificată" cu „bon fiscal" — legea le tratează asemănător (ambele au reguli similare de raportare defalcată), dar sunt categorii de document distincte.
- Se ignoră distincția „cu CUI beneficiar" / „fără CUI beneficiar", care schimbă rândul pe care trebuie completată valoarea.

## Ce face iConta.eu

Aici trebuie spus cinstit: **iConta.eu nu are încă suport pentru facturi simplificate sau pentru case de marcat electronice fiscale (AMEF)**. Codul generatorului D394 (`core/d394.py`) definește explicit câmpurile cerute de validatorul ANAF pentru aceste categorii (`bazaFSLcod`, `bazaFSL`, `bazaFSA`, `bazaFSAI`, `bazaBFAI` și perechile lor de TVA), dar le populează cu valoarea zero — comentariul din sursă e explicit: „iConta nu are încă facturi simplificate şi AMEF -> rămân 0 până se construiesc". Câmpurile sunt trimise obligatoriu (validatorul cere ca ele să existe chiar și la zero), dar dacă firma ta emite efectiv facturi simplificate sau folosește case de marcat, acele valori nu ajung azi în D394 prin iConta — trebuie completate manual, în afara aplicației, până la extinderea acestei funcționalități.

[iConta.eu](/)
