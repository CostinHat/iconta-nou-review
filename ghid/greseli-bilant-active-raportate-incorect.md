---
title: "Greșeli la bilanț: active raportate incorect"
description: Sistemul blochează generarea bilanțului fără CUI, denumire sau nr. Registrul Comerțului, dar nu verifică azi dacă valorile activelor mapate din balanță sunt plauzibile.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeli la bilanț: active raportate incorect

Un bilanț se poate genera „cu succes" din punct de vedere tehnic și, în același timp, să conțină valori greșite la active — cele două lucruri nu sunt verificate în același loc.

## Temeiul legal

::: ghid-temei
Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.
— Legea contabilității nr. 82/1991, republicată, art. 28 alin. (1)
:::

Obligația de imagine fidelă cade în sarcina firmei care întocmește și depune bilanțul — legea nu prevede o validare tehnică automată a plauzibilității fiecărei valori din formular; responsabilitatea rămâne a persoanei care întocmește și semnează situațiile financiare.

## Ce se greșește în practică

- Se raportează în bilanț valori mapate direct din balanța de verificare, fără o verificare prealabilă a plauzibilității lor (de exemplu, un sold creditor pe un cont de imobilizări, care ar trebui să aibă în mod normal sold debitor).
- Se confundă „bilanțul generat fără erori" (adică fără blocaje tehnice la generare) cu „bilanțul corect din punct de vedere economic" — sunt lucruri diferite.

## Ce face iConta.eu

Trebuie spus deschis unde e granița: funcția `erori_generare()` din `core/bilant_api.py` este o poartă de blocare **la nivel de date de identificare** — dacă lipsesc CUI-ul, denumirea firmei sau numărul de înregistrare la Registrul Comerțului, generarea bilanțului nu pornește (validatorul ANAF respinge XML-ul fără atributul `regCom`). Această verificare **nu include** o validare a plauzibilității valorilor economice mapate din balanță — de exemplu, un sold creditor pe un cont de activ nu declanșează niciun avertisment specific de conținut. Singura verificare de coerență numerică implementată azi este cea dintre activul net și totalul capitalurilor proprii (rd. 15 vs. rd. 49); pentru orice altă anomalie la nivel de active individuale, verificarea rămâne, la acest moment, în sarcina contabilului, direct pe balanța de verificare, înainte de generare.

[iConta.eu](/)
