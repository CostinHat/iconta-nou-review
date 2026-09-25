---
title: "Cum transmit o factură către un client din UE în e-Factura"
description: "Regimul obligatoriu RO e-Factura vizează operațiunile dintre firme stabilite în România; pentru un client din alt stat membru UE, transmiterea prin sistem rămâne, pe baza textului legii, opțională."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum transmit o factură către un client din UE în e-Factura

Întrebarea pornește de la o premisă care merită verificată întâi: regimul **obligatoriu** RO e-Factura vizează, conform Codului fiscal, operațiunile dintre persoane impozabile stabilite în România — nu orice factură emisă de o firmă românească, indiferent de țara clientului.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 [...]"
— Legea 227/2015 (Codul fiscal), art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Obligativitatea descrisă de acest text e legată explicit de operațiuni **între persoane impozabile stabilite în România** — un client stabilit într-un alt stat membru UE nu pare să intre în acest domeniu de aplicare obligatorie, pe baza textului citat.
- Pentru relațiile comerciale B2B care nu intră sub obligativitate, OUG 120/2021 lasă folosirea sistemului RO e-Factura la alegerea emitentului, nu ca obligație:

> „În relația comercială B2B emitentul facturii electronice poate opta pentru transmiterea acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura cu respectarea prevederilor art. 4 alin. (1)."
> — OUG 120/2021, art. 10 alin. (1) (sursă: anaf_surse/oug_120_2021.txt)
- Condiția tehnică pentru a folosi această opțiune: atât emitentul, cât și destinatarul trebuie să fie înregistrați în Registrul RO e-Factura (OUG 120/2021, art. 10 alin. (4)) — altfel, transmiterea nu produce efectele de „acceptare automată" descrise de lege pentru operatorii înregistrați.

Această concluzie e o deducție directă din faptul că legea leagă obligativitatea explicit de „persoane impozabile stabilite în România", nu o afirmație care spune literal „pentru clienți UE e opțional" — merită tratată cu precauție, mai ales dacă operațiunea concretă are particularități (de exemplu sediu fix în România al clientului UE).

## Ce se greșește în practică

- Se presupune că orice factură emisă de o firmă românească trebuie transmisă obligatoriu prin RO e-Factura, indiferent de țara în care e stabilit clientul.
- Se încearcă transmiterea opțională prin RO e-Factura fără ca partenerul să fie înregistrat în Registrul RO e-Factura, așteptând totuși efectul de „acceptare automată" rezervat operatorilor înregistrați.
- Se confundă regimul de TVA al operațiunii (livrare intracomunitară, prestare de servicii B2B) cu obligația de transmitere prin RO e-Factura — sunt reguli distincte, din acte normative diferite.

## Ce face iConta.eu

Subiectul acestui titlu — transmiterea propriu-zisă a facturii, ca XML, către sistemul RO e-Factura — ține de o altă funcționalitate a aplicației decât cea descrisă în acest ghid. Funcționalitatea „PDF factură" (`core/factura_pdf.py`) doar randează factura ca document vizual, cu logo/culoare/font personalizabile; ea **nu transmite nimic** către SPV și nu are nicio legătură de cod cu generarea sau trimiterea XML-ului. Generarea XML-ului și transmiterea lui se fac printr-un modul separat (`core/efactura_send.py` / `core/efactura_trimitere.py`), pe care acest dosar l-a verificat doar comparativ, nu în detaliu — pentru pașii exacți din interfață la trimiterea unei facturi către un client din alt stat membru UE, verifică ghidurile dedicate acelei funcționalități.

[iConta.eu](/)
