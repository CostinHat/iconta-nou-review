---
title: Cum închid un SRL cu numerar în casierie?
description: Ce se întâmplă cu numerarul rămas în casierie la lichidare și de ce nota contabilă standard din iConta.eu presupune plata netului prin bancă, nu în numerar.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL cu numerar în casierie?

Un sold rămas în casierie (contul 5311) la data lichidării face parte, ca orice altă valoare din patrimoniu, din activele care trebuie fie valorificate, fie predate asociaților la partajul final.

## Temeiul legal

::: ghid-temei
„În termen de 15 zile de la terminarea lichidării, lichidatorii vor depune la registrul comerțului cererea de radiere a societății [...], pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase, [...] inclusiv [...] dovada îndeplinirii obligației de calculare, reținere și plată a impozitului pe venit din lichidarea societății, prevăzută la art. 97 alin. (5) din [Codul fiscal] [...]."
— L31/1990, art. 260 alin. (6)
:::

Legea nu face distincție, la nivelul situației patrimoniale finale, între activele bănești aflate în bancă și cele aflate în casierie — ambele sunt parte din „situația patrimoniului" care trebuie prezentată la închiderea lichidării.

## Ce se greșește în practică

O eroare tehnică de reținut: nota contabilă generată de funcția de partaj din motorul de lichidare al iConta.eu (`core/lichidare.py`) creditează, pentru netul plătit către asociat, contul **5121 (bancă)** — `456=5121`. Dosarul de cercetare pentru F057 nu confirmă o variantă a acestei operațiuni care să crediteze contul **5311 (casă)**. Dacă plata efectivă a netului către asociați se face în numerar, nota contabilă generată automat de aplicație pentru operația de partaj nu va reflecta corect realitatea — trebuie corectată manual, prin înlocuirea contului 5121 cu 5311 în nota generată, sau printr-o notă manuală separată.

## Ce face iConta.eu

Ecranul de lichidare (categoria „Diverse" → „Lichidare / radiere firmă", operația „Partaj către asociați") calculează baza impozabilă și impozitul reținut la fel, indiferent de modul de plată efectiv al netului. Doar linia de credit a notei contabile presupune implicit plata prin bancă. Recomandarea practică: dacă lichidarea se finalizează cu plată în numerar, verificați și ajustați manual contul de trezorerie din nota contabilă generată înainte de a o valida.

Rețineți totodată, ca la orice partaj, verificarea cotei de impozit aplicate rezervelor și profiturilor distribuite — vezi ghidul dedicat pentru situația soldului bancar, unde este detaliată diferența dintre cota de 10% prevăzută la art. 97 alin. (5) din Codul fiscal și cota de 16% aplicată în prezent de aplicație.

[iConta.eu](/)
