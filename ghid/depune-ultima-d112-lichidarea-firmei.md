---
title: "Când se depune ultima D112 la lichidarea firmei?"
description: "Legătura dintre radierea înregistrării fiscale a firmei și termenul limită de depunere a ultimei declarații unice privind obligațiile de plată (D112)."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se depune ultima D112 la lichidarea firmei?

D112 se depune lunar, atâta vreme cât firma are calitatea de plătitor de venituri salariale. La lichidare, ultima D112 corespunde ultimei luni în care au existat astfel de venituri de raportat — dar radierea firmei, care închide definitiv obligațiile ei fiscale, are propriul termen legal, distinct de calendarul lunar al D112.

## Temeiul legal

::: ghid-temei
„(2) La încetarea calității de subiect de drept fiscal, persoanele sau entitățile înregistrate fiscal prin declarație de înregistrare fiscală potrivit art. 81 și 82 trebuie să solicite radierea înregistrării fiscale, prin depunerea unei declarații de radiere. Declarația se depune în termen de 30 de zile de la încetarea calității de subiect de drept fiscal și trebuie însoțită de certificatul de înregistrare fiscală în vederea anulării acestuia. [...]"
— Legea 207/2015 (Codul de procedură fiscală), art. 90 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă pentru calendarul concret al ultimei D112:

- D112 se depune pentru **fiecare lună** în care firma a acordat venituri de natură salarială (sau asimilate) — ultima D112 „normală" e cea aferentă ultimei luni cu astfel de venituri, depusă până la termenul lunar obișnuit (25 ale lunii următoare).
- Dacă toate contractele de muncă au fost încetate înainte de finalizarea procedurii de lichidare, ultima D112 cu conținut real (salarii, contribuții) e cea a lunii încetării ultimului contract — lunile ulterioare, fără venituri de raportat, nu mai generează obligație de D112.
- Radierea firmei (retragerea codului de identificare fiscală) e un act separat, care intervine **la finalul** procedurii de lichidare, cu termen propriu de 30 de zile de la încetarea calității de subiect de drept fiscal — nu la fiecare încetare de contract, ci la desființarea juridică a firmei însăși.
- Obligația de a depune declarații rămâne activă până la radiere: o firmă în lichidare, dar neradiată încă, continuă să răspundă pentru declarațiile ei fiscale, chiar dacă nu mai are salariați și nu mai are ce raporta prin D112.

## Ce se greșește în practică

- Se presupune că D112 trebuie depusă „până la radiere", inclusiv pentru lunile fără salariați și fără venituri de raportat — obligația D112 ține de existența venitului de raportat, nu de simpla existență juridică a firmei.
- Se omite ultima D112 aferentă lunii în care contractele au încetat, presupunând că lichidarea „acoperă" automat și raportarea salarială a lunii respective.
- Se confundă termenul de 30 de zile pentru declarația de radiere (art. 90 alin. (2)) cu termenul lunar de depunere a D112 — sunt proceduri și termene distincte.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu am identificat în cod** o legătură automată între procedura de lichidare/radiere a firmei și generarea sau oprirea depunerii D112. Aplicația generează D112 lunar pe baza datelor din statul de plată curent (module `core/d112.py`, `core/stat_plata_api.py`); modulul `core/lichidare.py` acoperă doar motorul contabil al lichidării (valorificarea activelor, partajul, impozitul pe câștigul asociaților), nu coordonarea calendarului declarativ cu radierea firmei. Oprirea corectă a depunerilor D112 și corelarea cu momentul radierii rămân responsabilitatea contabilului.

[iConta.eu](/)
