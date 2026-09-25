---
title: "Cum calculez salariul pentru salariatul cu mai multe contracte"
description: "Ce prevede Codul muncii despre cumulul de funcții pe baza mai multor contracte individuale de muncă și cum se calculează salariul pentru fiecare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum calculez salariul pentru salariatul cu mai multe contracte

Un salariat poate avea, legal, mai multe contracte individuale de muncă simultan — la același angajator sau la angajatori diferiți. Întrebarea practică pentru cel care întocmește statele de plată e cum se calculează salariul în această situație: separat, pentru fiecare contract, sau cumulat.

## Temeiul legal

::: ghid-temei
„(1) Orice salariat are dreptul de a cumula mai multe funcții, în baza unor contracte individuale de muncă, beneficiind de salariul corespunzător pentru fiecare dintre acestea.
(2) Fac excepție de la prevederile alin. (1) situațiile în care prin lege sunt prevăzute incompatibilități pentru cumulul unor funcții.
(3) Salariații care cumulează mai multe funcții sunt obligați sa declare fiecărui angajator locul unde exercita funcția pe care o considera de baza."
— Legea nr. 53/2003 (Codul muncii), art. 35 (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Mecanismul rezultă direct din text:

- **Fiecare contract individual de muncă se calculează separat**, cu propriul salariu — legea vorbește explicit despre „salariul corespunzător pentru fiecare dintre acestea", nu despre un calcul unic, cumulat, la nivel de persoană.
- Salariatul are **obligația** să declare fiecărui angajator care este locul de muncă pe care îl consideră de bază — declarația e relevantă pentru anumite calcule fiscale și sociale (de exemplu, deducerile personale sau plafoanele legate de locul de muncă de bază se aplică o singură dată, la angajatorul declarat ca atare).
- Excepția de la dreptul de cumul o reprezintă incompatibilitățile prevăzute expres prin lege pentru anumite funcții (de exemplu, funcții publice cu regim de incompatibilitate) — în absența unei astfel de interdicții exprese, cumulul e permis.

## Ce se greșește în practică

- Se calculează un singur salariu „cumulat" la nivelul persoanei, împărțit apoi pe cele două contracte — legea cere calcul separat, pe fiecare contract individual, nu o singură bază comună.
- Se aplică deducerile personale sau alte facilități legate de locul de muncă de bază la ambii angajatori simultan, deși ele se aplică o singură dată, la angajatorul declarat de salariat ca loc de muncă de bază.
- Se omite solicitarea declarației scrise privind locul de muncă de bază de la salariatul nou-angajat care are deja alt contract activ — fără ea, angajatorul nu poate ști cum să trateze corect anumite calcule dependente de acest statut.

## Ce face iConta.eu

Verificat în cod: modulele `core/contracte_api.py`, `core/salariu_istoric.py` și `core/stat_plata_api.py` gestionează contractele individuale de muncă și calculul statelor de plată pe fiecare contract. Nu am găsit în aceste module o logică explicită legată de declarația „loc de muncă de bază" în cazul cumulului de funcții pe mai multe contracte — aplicația calculează salariul pe fiecare contract introdus, dar aplicarea corectă a facilităților care depind de statutul de loc de muncă de bază, în cazul unui salariat cu contracte multiple, rămâne o verificare a contabilului.

[iConta.eu](/)
