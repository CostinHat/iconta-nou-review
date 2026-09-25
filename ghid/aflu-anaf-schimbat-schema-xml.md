---
title: "Cum aflu dacă ANAF a schimbat schema XML pentru e-Factura?"
description: "Specificațiile tehnice ale facturii electronice RO e-Factura se stabilesc prin ordin al ministrului finanțelor — o schimbare de schemă e mereu ancorată într-un act publicat oficial."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum aflu dacă ANAF a schimbat schema XML pentru e-Factura?

Structura XML a facturii electronice nu e o convenție tehnică informală a ANAF, ci un element reglementat prin acte normative — ceea ce înseamnă că orice schimbare de schemă trebuie să aibă, undeva, un ordin al ministrului finanțelor publicat în Monitorul Oficial. Verificarea "automată" pornește tocmai de aici.

## Temeiul legal

::: ghid-temei
„(1) Structura facturii electronice respectă:
a) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, care sunt aplicabile la nivel naţional;
b) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - şi regulile operaţionale specifice aplicabile la nivel naţional; [...]
(11) Prin ordin al ministrului finanţelor se reglementează specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice RO_CIUS [...] în termen de 15 zile de la data publicării prezentei ordonanţe de urgenţă în Monitorul Oficial al României, Partea I."
— OUG nr. 120/2021 privind Sistemul naţional privind factura electronică RO e-Factura, art. 4 alin. (1) și (11) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce rezultă din text pentru verificarea unei eventuale schimbări de schemă:

- Structura RO_CIUS **nu se schimbă discreționar** de ANAF — ea e reglementată prin ordin al ministrului finanțelor, publicat în Monitorul Oficial. Orice modificare de schemă trebuie, deci, să aibă la bază un ordin nou sau o modificare a celui existent.
- Practic, singura verificare "automată" fiabilă e compararea versiunii curente a documentului de specificații tehnice (RO_CIUS) și a fișierului XSD oficial publicat de ANAF cu cea folosită de softul de facturare — o schimbare de schemă se traduce, tehnic, într-un XSD nou sau într-un mesaj de eroare de validare la trimiterea unei facturi pe structura veche.
- Sistemul RO e-Factura validează structural fiecare factură la transmitere (art. 4 alin. (4)-(5)): dacă o factură care trecea validarea începe brusc să fie respinsă cu erori de structură, e un indiciu direct că schema s-a schimbat.

## Ce se greșește în practică

- Se presupune că un mesaj de eroare punctual la o factură e o problemă de date proprii, fără să se verifice dacă eroarea apare sistematic pe toate facturile trimise după o anumită dată — semn tipic al unei schimbări de schemă, nu al unei greșeli izolate.
- Se folosește un XSD/validator local nesincronizat cu ultima versiune publicată de ANAF, ceea ce dă fals-pozitive sau fals-negative față de validarea reală din sistemul RO e-Factura.
- Se ignoră publicarea ordinelor ministrului finanțelor care actualizează specificațiile RO_CIUS, bazându-se doar pe anunțuri informale sau presă fiscală.

## Ce face iConta.eu

La fiecare trimitere de factură prin RO e-Factura, iConta.eu validează structura XML generată pe validatorul oficial ANAF **înainte** de upload — dacă schema s-a schimbat și structura nu mai corespunde, factura nu trece de această poartă și trimiterea e blocată cu mesajele de eroare primite, nu trimisă "pe risc". Această verificare se face per factură, în timp real; aplicația nu are un mecanism separat de monitorizare/notificare proactivă a publicării unui ordin nou de modificare a schemei RO_CIUS.

[iConta.eu](/)
