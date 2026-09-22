---
title: Ce reprezintă bilanțul de deschidere și cel de închidere la lichidare?
description: Bilanțul de deschidere marchează preluarea patrimoniului de către lichidatori, iar situația financiară finală propune repartizarea activului rămas — între cele două, lichidarea trebuie terminată în maximum un an, cu posibile prelungiri.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce reprezintă bilanțul de deschidere și cel de închidere la lichidare?

Lichidarea unei firme este delimitată de două momente contabile obligatorii: bilanțul de deschidere, întocmit când lichidatorii preiau patrimoniul, și situația financiară finală, întocmită la terminarea lichidării. Între cele două, legea impune și un termen limită.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art.253 alin.(3):**
"Lichidatorii sunt datori, îndată după preluarea funcției, ca împreună cu directorii și administratorii... să facă un inventar și să încheie un bilanț, care să constate situația exactă a activului și pasivului societății, și să le semneze."

**Legea 31/1990, art.263 alin.(1):**
"După terminarea lichidării societății în nume colectiv, în comandită simplă sau cu răspundere limitată, lichidatorii trebuie să întocmească situația financiară și să propună repartizarea activului între asociați."

**Legea 31/1990, art.260 alin.(1):**
"Lichidarea societății trebuie terminată în cel mult un an de la data înregistrării în registrul comerțului a mențiunii de dizolvare." (prelungibil de max. 3 ori, cu câte un an, pentru motive temeinice)
:::

## Cele două puncte fixe ale lichidării

**Bilanțul de deschidere** se întocmește imediat după ce lichidatorii preiau funcția — un inventar complet, făcut împreună cu administratorii/directorii aflați încă în funcție, care constată situația exactă a activului și pasivului la acel moment. Este linia de start: de aici încolo, lichidatorii răspund de gestionarea patrimoniului.

**Situația financiară finală** se întocmește după terminarea operațiunilor de lichidare (vânzare active, încasare creanțe, plată datorii) și trebuie să propună explicit modul de repartizare a activului net rămas între asociați. Nu este doar o listă de solduri — legea cere ca lichidatorii să "propună repartizarea activului", adică documentul trebuie să conțină efectiv această propunere.

Între cele două momente, legea impune un termen: lichidarea trebuie terminată în cel mult un an de la înregistrarea mențiunii de dizolvare, cu posibilitatea a maximum trei prelungiri, de câte un an fiecare, pentru motive temeinice.

## Ce se greșește în practică

- Se confundă bilanțul de deschidere al lichidării cu bilanțul contabil anual obișnuit al firmei — sunt documente diferite, cu scop și conținut diferite.
- Se lasă lichidarea "deschisă" fără să se urmărească termenul de un an (și eventualele prelungiri), riscând probleme la Registrul Comerțului.
- Situația financiară finală se întocmește ca un simplu tabel de solduri, fără propunerea explicită de repartizare a activului între asociați, deși legea o cere.

## Ce face iConta.eu

Modulul general de bilanț al aplicației (`core/bilant.py` / `core/bilant_api.py`) nu conține nicio mențiune legată de lichidare, radiere sau dizolvare — nu există un generator dedicat, nici pentru bilanțul de deschidere, nici pentru situația financiară finală a lichidării. iConta.eu produce doar notele contabile individuale ale operațiunilor din lichidare — vânzarea unui activ și partajul final către asociați — care alimentează soldurile din care contabilul trebuie să întocmească manual, în afara aplicației, cele două situații financiare cerute de lege, respectând și termenul legal de finalizare.

[iConta.eu](/)
