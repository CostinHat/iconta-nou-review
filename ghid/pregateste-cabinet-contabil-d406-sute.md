---
title: "Cum pregătește un cabinet contabil D406 pentru sute de clienți?"
description: "Structura obligației D406 (SAF-T) pe fiecare contribuabil în parte, conform OPANAF 1783/2021, și ce înseamnă asta pentru un cabinet care administrează mulți clienți."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum pregătește un cabinet contabil D406 pentru sute de clienți?

D406 (SAF-T) nu e o declarație „de cabinet" — e o obligație individuală a fiecărui contribuabil, cu propria dată de referință și propriul fișier standard de control fiscal. Pentru un cabinet cu sute de clienți, asta înseamnă sute de obligații paralele, nu una singură multiplicată.

## Temeiul legal

::: ghid-temei
„Obligația de transmitere a fișierului standard de control fiscal prin intermediul Declarației informative D406 devine efectivă pentru fiecare categorie de contribuabili, astfel: [...] pentru contribuabilii încadrați în categoria de contribuabili mici la data de 31 decembrie 2021, obligația de depunere a Declarației informative D406 începe de la data de 1 ianuarie 2025 [...]; pentru contribuabilii nou-înregistrați/încadrați după data de referință pentru fiecare categorie în parte, obligația de depunere a Declarației informative D406 începe de la data efectivă a înregistrării."
— OPANAF 1783/2021 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă pentru un cabinet cu mulți clienți:

- Fiecare client e un **contribuabil distinct**, cu propria categorie (mare/mijlociu/mic) și propria dată de referință de la care obligația devine efectivă — nu există o dată unică valabilă pentru „toți clienții cabinetului".
- Depunerea se face **per CUI**, cu fișierul standard de control fiscal generat din datele contabile ale fiecărei entități în parte — nu se poate consolida sau grupa raportarea mai multor firme într-un singur fișier D406.
- Pentru clienți nou-înregistrați după data de referință a categoriei lor, obligația pornește **de la data efectivă a înregistrării**, cu prima depunere „în ultima zi a lunii care urmează perioadei pentru care se face raportarea" — fiecare client nou intrat în portofoliu poate avea un calendar propriu de pornire.

Pentru un cabinet cu sute de clienți, gestionarea practică e deci în esență o problemă de **planificare și urmărire a datelor de referință individuale**, nu una de interpretare legală suplimentară — legea nu oferă o „procedură de grup", pentru că obligația însăși nu e de grup.

## Ce se greșește în practică

- Se presupune că toți clienții cabinetului au aceeași dată de pornire a obligației D406 — de fapt fiecare categorie (mare/mijlociu/mic) are propria dată de referință, iar clienții nou-înregistrați au propriul calendar.
- Se încearcă o raportare agregată sau simplificată pentru mai mulți clienți mici deodată — legea cere depunere per contribuabil, indiferent de numărul de clienți administrați de același cabinet.
- Se pierde din vedere un client nou-înregistrat, presupunând că data de referință generală a categoriei sale (ex. 1 ianuarie 2025 pentru contribuabilii mici deja existenți) i se aplică și lui — de fapt, pentru el, obligația pornește de la data efectivă a înregistrării.

## Ce face iConta.eu

iConta.eu generează Declarația informativă D406 per firmă (per CUI), separat pentru fiecare tenant configurat în aplicație, verificată pe validatorul oficial DUK. Pentru un cabinet cu mai mulți clienți, fiecare firmă administrată în iConta.eu are propriul flux de generare D406, dar aplicația **nu urmărește automat** datele de referință individuale (mare/mijlociu/mic) pentru a semnala când începe obligația pentru fiecare client în parte — această verificare rămâne a cabinetului.

[iConta.eu](/)
