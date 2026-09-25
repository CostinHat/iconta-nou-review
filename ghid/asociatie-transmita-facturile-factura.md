---
title: "O asociație trebuie să transmită facturile în e-Factura?"
description: "Definiția largă a operatorului economic din OUG 120/2021 și de ce statutul non-profit al unei asociații nu o exclude automat de la obligațiile RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# O asociație trebuie să transmită facturile în e-Factura?

Depinde — nu de forma juridică (asociație, fundație), ci de faptul dacă desfășoară sau nu o activitate economică. Legea nu scutește asociațiile ca atare de la sistemul RO e-Factura; scutirea, dacă există, vine din natura activității, nu din statutul non-profit.

## Temeiul legal

::: ghid-temei
„b) operator economic - orice entitate care desfășoară o activitate economică constând în executarea de lucrări, livrarea de bunuri/produse și/sau prestarea de servicii."
— OUG 120/2021, art. 2 alin. (1) lit. b) (sursă: anaf_surse/oug_120_2021.txt)

„n) relația comercială dintre doi operatori economici - B2B - tranzacția având ca obiect execuția de lucrări, livrarea de bunuri/produse și/sau prestarea de servicii dintre doi operatori economici."
— OUG 120/2021, art. 2 alin. (1) lit. n) (sursă: anaf_surse/oug_120_2021.txt)
:::

Din definiția legii rezultă testul relevant pentru o asociație:

- **„Operator economic" nu înseamnă „societate comercială"** — legea definește noțiunea prin ce face entitatea (execută lucrări, livrează bunuri, prestează servicii cu caracter economic), nu prin forma ei juridică sau scopul patrimonial/non-patrimonial declarat la înființare.
- O asociație care **emite facturi** pentru bunuri livrate sau servicii prestate — de exemplu, venituri din activități economice accesorii scopului non-profit, chirii, evenimente cu plată, vânzare de produse — se încadrează, pentru acele operațiuni, în definiția „operatorului economic" de la lit. b) și devine parte a unei relații B2B în sensul lit. n), atunci când emite facturi către alți operatori economici.
- O asociație care **nu emite facturi** pentru activitate economică (funcționează exclusiv din cotizații, donații sau sponsorizări, fără operațiuni supuse facturării) nu intră în sfera acestei obligații, pentru simplul motiv că nu există o relație comercială de facturat.
- Concluzia: statutul de asociație nu e, prin el însuși, o scutire — verificarea corectă se face operațiune cu operațiune, nu la nivelul întregii entități.

## Ce se greșește în practică

- Se presupune că orice asociație sau fundație e automat exclusă din sistemul RO e-Factura, invocând scopul non-patrimonial — definiția legală nu face această distincție, ci una bazată pe natura operațiunii facturate.
- Se ignoră facturile emise pentru activități economice accesorii (chirii, servicii, vânzări ocazionale), tratându-le informal, fără verificarea obligațiilor care decurg din calitatea de „operator economic" pentru acele operațiuni specifice.
- Se confundă regimul fiscal al veniturilor asociației (adesea scutite de impozit pe profit pentru activitatea non-economică) cu obligațiile de facturare electronică, care sunt reglementate separat, prin OUG 120/2021.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu verifică automat** dacă o entitate înregistrată în aplicație (inclusiv o asociație) se încadrează, pentru o factură anume, în definiția „operatorului economic" de la art. 2 alin. (1) lit. b) din OUG 120/2021 — aplicația transmite facturile prin sistemul RO e-Factura (`core/efactura_send.py`) pe baza configurării firmei/entității făcute de contabil, fără o evaluare separată a naturii economice sau non-economice a fiecărei operațiuni facturate.

[iConta.eu](/)
