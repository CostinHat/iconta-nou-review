---
title: "Cum transmit factura către instituții publice"
description: "Procedura RO e-Factura pentru relația B2G, obligațiile destinatarului-instituție publică și rolul facturii electronice ca document justificativ în execuția bugetară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum transmit factura către instituții publice

Facturarea către o autoritate contractantă (o instituție publică, în calitate de client) se face prin același sistem național RO e-Factura folosit pentru relația dintre firme, dar cu un set de obligații suplimentare pentru instituția care primește factura — obligații pe care OUG 120/2021 le detaliază separat, în secțiunea dedicată achizițiilor publice.

## Temeiul legal

::: ghid-temei
„ART. 7 (1) În situaţia în care operatorul economic a optat pentru utilizarea sistemului naţional privind factura electronică RO e-Factura în conformitate cu prevederile art. 5, acesta are obligaţia de a emite doar facturi electronice şi de a utiliza acest sistem pentru transmiterea acestora către toţi destinatarii definiţi la art. 2 alin. (1) lit. p), cu excepţia facturilor electronice prevăzute la art. 6.
(2) În situaţia în care operatorul economic transmite factura electronică în sistemul naţional privind factura electronică RO e-Factura, destinatarul facturii electronice emise în relaţia B2G are următoarele obligaţii:
a) să primească şi să descarce factura electronică prin intermediul sistemului naţional privind factura electronică RO e-Factura;
b) să prelucreze factura electronică;
c) să verifice legalitatea, conformitatea şi regularitatea facturii electronice, în conformitate cu prevederile legale în vigoare."
— OUG nr. 120/2021 privind Sistemul naţional privind factura electronică RO e-Factura, art. 7 alin. (1)-(2) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce trebuie reținut pentru transmiterea efectivă:

- Odată ce un operator economic optează pentru RO e-Factura într-o relație B2G (art. 5), trebuie să emită **doar** facturi electronice către toți destinatarii-instituții publice, prin sistemul național — nu poate alege selectiv, factură cu factură, un alt canal.
- Instituția publică destinatară are, la rândul ei, obligații procedurale clare: primire și descărcare din sistem, prelucrare, verificarea legalității și conformității facturii — ceea ce înseamnă că factura corect transmisă prin RO e-Factura devine automat vizibilă și "procesabilă" pentru autoritate, fără demersuri suplimentare din partea furnizorului.
- Factura electronică (sau documentul de conversie a acesteia, dacă instituția nu poate procesa electronic) capătă calitatea de document justificativ pentru execuția bugetară a instituției publice — un rol formal, prevăzut explicit de OUG 120/2021.

## Ce se greșește în practică

- Se trimite factura către o instituție publică prin e-mail sau pe hârtie, în paralel cu sau în locul transmiterii prin RO e-Factura, generând confuzie asupra documentului "oficial" pentru decontare.
- Se presupune că simpla generare a XML-ului e suficientă, fără confirmarea că factura a fost efectiv comunicată destinatarului prin sistem (art. 4 alin. (7) — data comunicării e data la care factura devine disponibilă pentru descărcare, nu data trimiterii).
- Se ignoră excepțiile de la art. 6 (contracte clasificate sau cu măsuri speciale de securitate), care exclud anumite facturi din obligația de transmitere prin sistemul RO e-Factura.

## Ce face iConta.eu

iConta.eu emite și trimite facturi prin RO e-Factura folosind aceleași rute către infrastructura ANAF (upload, verificare stare, descărcare) indiferent dacă destinatarul e o firmă (B2B) sau o instituție publică (B2G) — sistemul național tratează transmiterea unitar odată ce factura respectă structura CIUS-RO. Aplicația nu are, la acest moment, un câmp separat care să marcheze explicit o factură ca fiind emisă în relația B2G sau să urmărească distinct obligațiile specifice de prelucrare ale destinatarului-instituție publică, dincolo de fluxul standard de trimitere și confirmare a facturii electronice.

[iConta.eu](/)
