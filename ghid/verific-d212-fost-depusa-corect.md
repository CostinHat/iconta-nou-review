---
title: "Cum verific dacă D212 a fost depusă corect?"
description: "Ce arată legea despre validarea declarației fiscale transmise electronic și cum se stabilește dacă D212 a fost depusă corect, la termen."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific dacă D212 a fost depusă corect?

Confirmarea legală a depunerii corecte a D212 este mesajul electronic transmis de sistemul ANAF în urma **validării** conținutului declarației, nu simplul fapt că fișierul a fost încărcat în Spațiul Privat Virtual. Dacă declarația nu este validată (are erori), nu se consideră depusă corect — și, dacă termenul legal s-a scurs, doar depunerea unei declarații valide până la sfârșitul lunii respective mai poate salva data inițială.

## Temeiul legal

::: ghid-temei
„(4) Data depunerii declarației fiscale prin mijloace electronice de transmitere la distanță este data înregistrării acesteia pe portal, astfel cum rezultă din mesajul electronic transmis de sistemul de tranzacționare a informațiilor, cu condiția validării conținutului declarației. în cazul în care declarația nu este validată, data depunerii declarației este data validării astfel cum rezultă din mesajul electronic.
(5) Prin excepție de la prevederile alin. (4), în situația în care declarația fiscală a fost depusă până la termenul legal, iar din mesajul electronic transmis de sistemul de tranzacționare a informațiilor rezultă că aceasta nu a fost validată ca urmare a detectării unor erori în completarea declarației, data depunerii declarației este data din mesajul transmis inițial în cazul în care contribuabilul/plătitorul depune o declarație validă până în ultima zi a lunii în care se împlinește termenul legal de depunere."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 103 alin. (4), (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Practic, verificarea corectitudinii depunerii înseamnă:

- Verificarea **mesajului electronic** primit de la sistemul de tranzacționare al ANAF (nu doar confirmarea de încărcare a fișierului) — acest mesaj spune explicit dacă declarația a fost validată sau respinsă, și din ce motiv.
- Dacă mesajul arată erori, declarația **nu s-a depus corect**, iar contribuabilul trebuie să corecteze și să retransmită. Termenul se salvează totuși (art. 103 alin. (5)) dacă varianta corectă se depune până la sfârșitul lunii în care s-a împlinit termenul legal.
- Dacă mesajul confirmă validarea, data depunerii corecte este data înregistrării pe portal — aceasta este data care contează pentru calculul eventualelor penalități de întârziere.

## Ce se greșește în practică

- Se consideră declarația depusă corect doar pe baza faptului că fișierul „s-a încărcat" în SPV, fără a citi mesajul de validare care urmează încărcării.
- Se ignoră o eroare de validare semnalată în mesaj, presupunând că declarația a intrat oricum în sistem — o declarație nevalidată nu produce efecte juridice ca declarație depusă la acea dată.
- Se pierde termenul de „ultima zi a lunii" (art. 103 alin. (5)) pentru retransmiterea corectată, considerând greșit că orice corecție ulterioară termenului legal duce automat la penalizare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu validează structural fișierul XML al D212 pe care îl generează, pe baza structurii oficiale a validatorului ANAF (D212Validator), pentru a produce un fișier conform cerințelor de format (`core/d212.py`). Aplicația nu are însă acces la sistemul de tranzacționare al ANAF și nu poate confirma ea însăși dacă declarația a fost efectiv validată și înregistrată pe portal — acea confirmare vine exclusiv din mesajul electronic primit de la ANAF, în contul SPV al contribuabilului, după încărcare.

[iConta.eu](/)
