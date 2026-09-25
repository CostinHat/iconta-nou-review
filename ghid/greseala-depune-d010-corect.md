---
title: "Greșeala de a nu depune D010 corect"
description: "Formularul vechi D010 a fost înlocuit de D700, dar obligația de fond — declararea la termen a modificărilor din datele de identificare fiscală — rămâne aceeași."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a nu depune D010 corect

D010 era, sub vechea denumire, formularul de declarație de mențiuni prin care o firmă aducea la cunoștința ANAF orice schimbare a datelor din certificatul de înregistrare fiscală. Formularul a fost între timp înlocuit de D700, dar greșelile de fond — completarea greșită sau depunerea cu întârziere a modificărilor — rămân aceleași, pentru că obligația legală care le impune nu s-a schimbat.

## Temeiul legal

::: ghid-temei
„(1) Modificările ulterioare ale datelor din declarația de înregistrare fiscală trebuie aduse la cunoștință organului fiscal central, în termen de 15 zile de la data producerii acestora, prin completarea și depunerea declarației de mențiuni. (2) În cazul modificărilor intervenite în datele declarate inițial și înscrise în certificatul de înregistrare fiscală, contribuabilul/plătitorul depune, odată cu declarația de mențiuni, și certificatul de înregistrare fiscală, în vederea anulării acestuia și eliberării unui nou certificat. (3) Declarația de mențiuni este însoțită de documente care atestă modificările intervenite. (4) Prevederile prezentului articol se aplică în mod corespunzător ori de câte ori contribuabilul/plătitorul constată erori în declarația de înregistrare fiscală."
— Legea 207/2015 (Codul de procedură fiscală), art. 88 alin. (1)-(4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

**Limitare declarată**: legea nu numește formularul „D010" — numărul formularului și denumirea lui exactă (D010, D700) sunt stabilite prin ordin al președintelui ANAF, nu prin Codul de procedură fiscală. Textul de mai sus e temeiul legal de fond al obligației de declarare a modificărilor și a erorilor din datele de înregistrare fiscală — cel pe care orice formular (vechi sau nou) îl pune în practică.

Ce rezultă din text pentru greșelile frecvente legate de acest formular:

- **Termenul e de 15 zile de la data producerii modificării** — nu de la data la care firma „își aduce aminte" să declare, ci de la momentul real al schimbării (ex. schimbarea sediului, a administratorului, a activității principale).
- **Alin. (4) acoperă explicit corectarea erorilor** — dacă firma constată o eroare în propria declarație de înregistrare fiscală inițială, procedura de corectare e aceeași ca la o modificare de date: se depune o nouă declarație de mențiuni.
- **Modificarea datelor înscrise în certificatul de înregistrare fiscală cere, suplimentar, depunerea certificatului vechi**, pentru anulare și eliberarea unuia nou — o etapă administrativă ușor de omis dacă firma tratează depunerea electronică drept singurul pas necesar.
- **Declarația trebuie însoțită de documente justificative** pentru modificările declarate — o declarație depusă fără documentele aferente e incompletă față de cerința alin. (3).

## Ce se greșește în practică

- Se declară modificarea abia când apare nevoia practică de a o folosi (ex. la o cerere de finanțare), nu în termenul legal de 15 zile de la producerea ei.
- Se presupune că o eroare din declarația inițială de înregistrare „rămâne așa" până la o eventuală inspecție, deși alin. (4) obligă explicit la corectare prin declarație de mențiuni, de îndată ce eroarea e constatată.
- Se depune declarația electronic, fără certificatul de înregistrare fiscală vechi, când modificarea privește date înscrise chiar în certificat — pasul de anulare/reeliberare a certificatului nu se declanșează automat.
- Se depune declarația fără documentele justificative ale modificării, ceea ce poate întârzia procesarea ei de către organul fiscal.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate de generare sau depunere a declarației de mențiuni** (indiferent dacă e vorba de vechiul D010 sau de actualul D700). Investigația tehnică asupra formularului D700 (documentată intern) arată că acesta nu are structură XML de tip declarativ standard, ca D100/D112/D300 — e o declarație de tip formular electronic (SmartPDF), iar validatorul oficial DUK nu o validează ca pe declarațiile obișnuite. Din acest motiv, generarea automată a declarației de mențiuni nu a putut fi construită și verificată conform metodei de lucru a echipei, care cere confirmare pe validatorul oficial înainte de publicare. Modificările datelor de identificare ale firmei se depun, la acest moment, direct prin mijloacele puse la dispoziție de ANAF.

[iConta.eu](/)
