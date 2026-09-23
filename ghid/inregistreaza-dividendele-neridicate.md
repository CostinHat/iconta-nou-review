---
title: "Cum se înregistrează dividendele neridicate?"
description: "Cum se contabilizează dividendul aprobat, dar neîncă plătit asociatului, și când devine oricum scadent impozitul pe dividende."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează dividendele neridicate?

Acest ghid tratează situația în care dividendul a fost aprobat, dar asociatul nu a încasat efectiv suma până la finalul anului — nu situația unui dividend rămas neridicat ani de zile, pentru care regimul fiscal specific nu este documentat aici (vezi mai jos).

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata. În cazul dividendelor [...] distribuite, dar care nu au fost plătite acționarilor/asociaților [...] până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii." — Codul fiscal, art. 97 alin. (7), în forma dată de Legea 141/2025, art. II pct. 5
:::

Legea este explicită: chiar dacă dividendul aprobat nu a fost efectiv plătit asociatului până la finalul anului, impozitul pe dividende tot devine scadent — cel târziu pe 25 ianuarie anul următor. Practic, dividendul trebuie înregistrat ca obligație (repartizare + impozit reținut), indiferent dacă plata efectivă a mai fost sau nu făcută.

## Ce se greșește în practică

Greșeala tipică este amânarea înregistrării impozitului pe dividende până la data plății efective către asociat, motivând că „nu s-a plătit încă". Legea nu condiționează scadența impozitului de plata efectivă: dacă dividendul a fost aprobat și nu a fost plătit până la finalul anului, impozitul devine oricum scadent pe 25 ianuarie anul următor.

Atenție și la sensul termenului: „dividende neridicate" poate însemna fie „aprobat, dar neîncasat încă de asociat" (situația tratată aici), fie „neridicat de mult timp, posibil prescris" — un subiect diferit, de prescripție și eventuală reîncadrare, pentru care nu am găsit un temei legal explicit verificat; recomandăm tratarea separată a acestui al doilea caz, cu verificare legală dedicată.

## Ce face iConta.eu

Funcția din modulul de decontări asociați care generează nota de dividend acceptă un parametru explicit pentru „cu plată" sau nu. Când operațiunea este marcată ca neplătită, aplicația generează doar liniile de repartizare și de impozit (1171=457 și 457=446 pentru dividendul anual, respectiv 463=456 și 456=446 pentru cel interimar), fără linia de virament net către bancă — exact situația unui dividend aprobat, dar neîncasat încă. Linia de plată netă (457=5121, respectiv 456=5121) se adaugă ulterior, separat, în momentul în care asociatul încasează efectiv suma.

[iConta.eu](/)
