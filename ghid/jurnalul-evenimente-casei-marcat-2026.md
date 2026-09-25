---
title: "Jurnalul de evenimente al casei de marcat 2026"
description: "Termenul tehnic-fiscal corect nu e «jurnal de evenimente», ci «jurnal electronic» — componenta AMEF care stochează istoricul bonurilor fiscale, distinctă de raportul Z folosit efectiv în contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Jurnalul de evenimente al casei de marcat 2026

Termenul care circulă în practică — „jurnal de evenimente" — nu e cel folosit de legislația română pentru casele de marcat electronice fiscale (AMEF). Legea vorbește despre „jurnal electronic", o componentă tehnică internă a aparatului. Pentru contabilitate, documentul care contează efectiv e altul: raportul fiscal de închidere zilnică (raportul Z), nu jurnalul electronic în sine.

## Temeiul legal

::: ghid-temei
„Aparate de marcat electronice fiscale sunt considerate și casele de marcat electronice fiscale și alte sisteme ce includ dispozitive cu funcții de case de marcat, echipate cu dispozitiv de memorare a jurnalului electronic, care înglobează constructiv un modul fiscal, prin intermediul căruia controlează memoria fiscală, dispozitivul de imprimare, dispozitivul de memorare, afișajul client, dispozitivul de salvare externă și dispozitivul de comunicație externă care permite integrarea într-un sistem informatic;"
— OUG 28/1999 (republicată), art. 3 alin. (2) (sursă: anaf_surse/oug_28_1999.html)

„[Aparatele de marcat electronice fiscale trebuie să îndeplinească cumulativ] [...] c) imprimarea, memorarea și emiterea electronică de: bonuri fiscale, rapoarte fiscale de închidere zilnică, jurnale electronice, rapoarte de sinteză și rapoarte memorie fiscală, pentru aparatele de marcat electronice fiscale definite la alin. (2); [...]"
— OUG 28/1999 (republicată), art. 3 alin. (3) lit. c) (sursă: anaf_surse/oug_28_1999.html)
:::

- Jurnalul electronic e componenta AMEF care stochează detaliat fiecare bon fiscal emis, distinctă de memoria fiscală (care reține datele de sinteză ale rapoartelor de închidere zilnică).
- Termenul „jurnal de evenimente" nu apare în OUG 28/1999 — legea folosește exclusiv „jurnal electronic"; confuzia de termeni nu schimbă faptul că e vorba de o componentă internă a aparatului, nu de un registru ținut de contabil.
- Raportul fiscal de închidere zilnică (raportul Z) e documentul relevant pentru înregistrarea contabilă: conține totalurile pe cote de TVA și pe modalități de plată ale unei zile, extrase din memoria fiscală și din jurnalul electronic al aparatului.

## Ce se greșește în practică

- Se caută un „jurnal de evenimente" separat, de ținut la firmă — nu există o asemenea obligație pentru contribuabil; jurnalul electronic e o componentă internă a aparatului, gestionată tehnic de producător/distribuitor, nu un registru completat de contabil.
- Se confundă jurnalul electronic (istoricul detaliat al bonurilor) cu raportul Z (sinteza zilei) — pentru înregistrarea contabilă zilnică contează raportul Z, nu jurnalul electronic în sine.
- Se ignoră obligația de recuperare a jurnalului electronic la înlocuirea memoriei fiscale sau a dispozitivului de memorare (când acestea sunt defecte sau capacitatea de stocare a fost epuizată) — datele trebuie păstrate, în caz de control.

## Ce face iConta.eu

iConta.eu nu implementează niciun concept propriu de „jurnal de evenimente" al casei de marcat — căutarea termenului în tot codul aplicației (`core/`) nu are niciun rezultat, nici sub acest nume, nici ca funcționalitate tehnică echivalentă. Aplicația are însă o funcție conexă reală: modulul `core/amef_import.py` importă Raportul Z exportat de o casă de marcat electronică fiscală (fișier XML sau p7b semnat electronic), conform structurii oficiale din OPANAF 146/2018, anexa 2, secțiunea II.7 — extrage identificatorul (NUI) casei de marcat, numărul raportului, totalurile pe cote de TVA și pe modalități de plată (card, numerar, tichete de masă etc.), pentru înregistrarea contabilă a zilei. Această funcție preia rezultatul sintetic al zilei — raportul de închidere zilnică — nu jurnalul electronic propriu-zis al aparatului, care rămâne exclusiv în interiorul AMEF-ului și în responsabilitatea producătorului/distribuitorului autorizat.

[iConta.eu](/)
