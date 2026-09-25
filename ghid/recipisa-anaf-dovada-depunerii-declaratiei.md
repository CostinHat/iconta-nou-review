---
title: "Este recipisa ANAF dovada depunerii declarației?"
description: "Ce spune Codul de procedură fiscală despre data depunerii unei declarații transmise electronic și rolul mesajului de confirmare (recipisa) în stabilirea acestei date."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Este recipisa ANAF dovada depunerii declarației?

Da, dar cu o condiție esențială: recipisa nu confirmă doar că ați trimis declarația, ci că ANAF a **validat** conținutul ei. O declarație transmisă, dar respinsă la validare, nu are aceeași dată de depunere ca una acceptată direct — iar diferența poate conta la un termen-limită.

## Temeiul legal

::: ghid-temei
„(3) Data depunerii declarației fiscale este data înregistrării acesteia la organul fiscal sau data depunerii la poștă, după caz. În situația în care declarația fiscală se depune prin mijloace electronice de transmitere la distanță, data depunerii declarației este data înregistrării acesteia pe pagina de internet a organului fiscal, astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației.
(4) Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației. În cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic.
(5) Prin excepție de la prevederile alin. (4), în situația în care declarația fiscală a fost depusă până la termenul legal, iar din mesajul electronic transmis de sistemul de tranzacționare a informațiilor rezultă că aceasta nu a fost validată ca urmare a detectării unor erori în completarea declarației, data depunerii declarației este data din mesajul transmis inițial în cazul în care contribuabilul/plătitorul depune o declarație validă până în ultima zi a lunii în care se împlinește termenul legal de depunere."
— Legea 207/2015 (Codul de procedură fiscală), art. 103 alin. (3)-(5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Trei situații, cu trei date de depunere diferite:

1. **Declarație validată la prima transmitere**: recipisa (mesajul electronic de confirmare) e dovada directă a depunerii, iar data din ea este data legală de depunere — conform alin. (3) și (4).
2. **Declarație respinsă la validare, fără corecție ulterioară**: data depunerii devine data la care declarația e efectiv validată, nu data primei transmiteri — alin. (4), a doua teză.
3. **Declarație respinsă la validare din cauza unor erori, dar corectată și redepusă validă până la sfârșitul lunii în care s-a împlinit termenul legal**: alin. (5) oferă o excepție favorabilă — data depunerii rămâne cea a transmiterii inițiale, deci termenul se consideră respectat, chiar dacă validarea reală a venit ulterior.

Practic, recipisa singură nu spune tot: trebuie citită împreună cu mesajul de validare, iar pentru o declarație respinsă inițial, excepția de la alin. (5) poate salva termenul-limită doar dacă redepunerea validă se face până la sfârșitul lunii respective.

## Ce se greșește în practică

- Se consideră declarația depusă la termen doar pe baza recipisei de transmitere, fără verificarea mesajului de validare — o declarație transmisă dar respinsă nu e, implicit, depusă la acea dată.
- Se ignoră excepția de la alin. (5) și se presupune că orice respingere la validare mută automat data depunerii, chiar și atunci când legea oferă o „plasă de siguranță" până la sfârșitul lunii termenului.
- Se păstrează doar dovada trimiterii (de exemplu, un e-mail de upload), fără mesajul electronic de confirmare/validare propriu-zis, care e elementul relevant din punct de vedere legal.

## Ce face iConta.eu

La data acestui ghid, nu am putut confirma din codul aplicației un mecanism dedicat de arhivare și urmărire automată a mesajelor de confirmare/validare primite de la ANAF pentru declarațiile transmise (dincolo de fluxul specific de e-Factura, unde aplicația gestionează separat starea încărcării — vezi modulul `core/efactura_send.py`). Pentru celelalte declarații fiscale, păstrarea recipisei și verificarea statusului de validare rămân un proces manual al contabilului, în afara aplicației.

[iConta.eu](/)
