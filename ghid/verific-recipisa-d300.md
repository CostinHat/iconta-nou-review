---
title: "Cum verific recipisa pentru D300?"
description: "Ce înseamnă legal mesajul electronic de confirmare a unei declarații depuse prin mijloace electronice și unde se verifică, pentru D300, dacă declarația a fost efectiv validată de ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific recipisa pentru D300?

„Recipisa" e denumirea uzuală pentru mesajul electronic pe care Spațiul Privat Virtual (SPV) îl emite după încărcarea unei declarații — el confirmă (sau infirmă) validarea conținutului și fixează data legală a depunerii. Pentru D300, ca pentru orice declarație transmisă electronic, acest mesaj e singura dovadă oficială că decontul a ajuns, a fost validat și e considerat depus la data respectivă.

## Temeiul legal

::: ghid-temei
„(4) Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației. în cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic."
— Legea 207/2015 (Codul de procedură fiscală), art. 103 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Alte elemente utile, din același articol:

- Alin. (3) precizează regula generală: pentru depunerea electronică, data depunerii e „data înregistrării... pe pagina de internet a organului fiscal, astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației" — mesajul electronic (recipisa) e chiar dovada legală a datei.
- Alin. (5) tratează cazul unei declarații respinse din cauza unor erori: dacă a fost depusă în termen dar respinsă, iar contribuabilul depune o versiune validă până la sfârșitul lunii în care se împlinește termenul legal, data depunerii rămâne cea inițială, nu cea a corectării — deci verificarea recipisei nu e doar formalitate, poate conta direct pentru încadrarea în termen.

## Ce se greșește în practică

- Se consideră declarația depusă doar pentru că a fost „trimisă" din aplicația de la care s-a generat XML-ul — dovada legală e mesajul electronic al SPV, nu confirmarea internă a aplicației folosite pentru generare.
- Se ignoră cazul unei declarații respinse ca invalidă — dacă mesajul primit arată erori, decontul nu e considerat depus până la validare (sau, cu condițiile de la alin. (5), până la o versiune corectă depusă în aceeași lună).
- Se șterge sau se pierde recipisa după depunere — ea rămâne dovada oficială a datei și a validării, utilă în orice discuție ulterioară cu ANAF sau într-o eventuală contestație.

## Ce face iConta.eu

iConta.eu nu are, în cod, o funcție de verificare a stării de validare a unei declarații direct din SPV — motorul de control fiscal semnalează explicit acest lucru ca o limită cunoscută: nu există niciun modul care să confirme dacă D300 (sau D390) depuse efectiv la ANAF coincid cu ce calculează aplicația, pentru că o asemenea confirmare ar necesita conectare directă la Spațiul Privat Virtual.

Ce face efectiv aplicația, prin funcționalitatea **F251 — panoul de rânduri manuale D300** (`core/d300_manual_api.py`), e o verificare internă diferită: garantează **paritatea între ce se vede în preview și ce se depune** — rândurile introduse manual (regularizări, ajustări care nu rezultă din facturi) sunt persistate în tabelul `d300_manual` și recitite identic la generarea XML-ului final, indiferent dacă acesta vine din previzualizare sau din coada efectivă de depunere. Aceasta e o garanție de consistență a conținutului declarației înainte de trimitere, nu o confirmare a recipisei primite de la ANAF după trimitere — verificarea propriu-zisă a recipisei/statusului de validare rămâne, azi, o operațiune făcută direct în SPV.

[iConta.eu](/)
