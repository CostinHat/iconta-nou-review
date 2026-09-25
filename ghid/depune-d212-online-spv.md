---
title: "Pot depune D212 online prin SPV?"
description: "Obligația persoanelor fizice cu activitate independentă de a transmite Declarația unică (D212) exclusiv prin mijloace electronice, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Pot depune D212 online prin SPV?

Nu doar poți — dacă ești persoană fizică ce desfășoară o activitate economică în mod independent (PFA, întreprindere individuală, întreprindere familială) sau exerciți o profesie liberală, ești **obligat** să depui Declarația unică (D212) prin mijloace electronice de transmitere la distanță, adică prin Spațiul Privat Virtual (SPV). Depunerea pe hârtie nu este luată în considerare pentru această categorie de contribuabili.

## Temeiul legal

::: ghid-temei
„Prin excepție de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri și alte entități fără personalitate juridică, precum și persoane fizice care desfășoară o profesie liberală sau exercită o activitate economică în mod independent în una dintre formele prevăzute de Ordonanța de urgență a Guvernului nr. 44/2008 privind desfășurarea activităților economice de către persoanele fizice autorizate, întreprinderile individuale și întreprinderile familiale [...] sunt obligați să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanță în condițiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanțelor/A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Consecințele practice ale acestei obligații:

- O PFA/II/IF sau un profesionist liberal (avocat, medic, notar etc.) nu are opțiunea de a alege între depunerea pe hârtie și cea electronică pentru D212 — legea impune direct forma electronică.
- Alin. (1^2) al aceluiași articol este explicit: dacă documentele sunt totuși depuse în format letric la organul fiscal central, **nu vor fi luate în considerare**, iar organul fiscal notifică obligativitatea transmiterii electronice.
- Canalul prin care se realizează transmiterea este sistemul de comunicare electronică al Ministerului Finanțelor/A.N.A.F., adică Spațiul Privat Virtual (SPV), la care contribuabilul trebuie să fie înrolat în prealabil.

## Ce se greșește în practică

- Contribuabili nou-înregistrați ca PFA încearcă să depună D212 la ghișeul administrației fiscale, fără să știe că, pentru categoria lor, depunerea pe hârtie nu este validă.
- Se confundă „poate" cu „trebuie": D212 nu e opțional electronic pentru persoanele cu activitate independentă, spre deosebire de alte categorii de persoane fizice, cărora legea le permite și alte mijloace de identificare (art. 80 alin. (1) lit. b)).
- Se amână înrolarea în SPV până aproape de termenul de depunere (25 mai), ceea ce poate întârzia efectiv transmiterea declarației dacă apar probleme la înregistrare sau la obținerea certificatului digital.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul XML al Declarației unice (D212) pe baza datelor introduse manual de contabil, prin modulul `core/d212.py` (funcția `genereaza`/`build_xml`). Aplicația nu transmite însă declarația către SPV și nu are integrare cu portalul ANAF pentru depunerea D212 — fișierul XML generat trebuie încărcat manual de contribuabil sau de contabil în Spațiul Privat Virtual.

[iConta.eu](/)
