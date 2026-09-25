---
title: "Cum verific dacă ANAF consideră o declarație depusă la termen?"
description: "Regula legală care stabilește data depunerii unei declarații fiscale, în funcție de canalul de transmitere folosit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific dacă ANAF consideră o declarație depusă la termen?

„Am trimis-o la timp” nu înseamnă mereu același lucru cu „ANAF o consideră depusă la timp” — legea leagă data depunerii de momentul înregistrării la organul fiscal sau de confirmarea electronică, nu de momentul la care contribuabilul apasă „trimite”.

## Temeiul legal

::: ghid-temei
„Data depunerii declarației fiscale este data înregistrării acesteia la organul fiscal sau data depunerii la poștă, după caz. în situația în care declarația fiscală se depune prin mijloace electronice de transmitere la distanță, data depunerii declarației este data înregistrării acesteia pe pagina de internet a organului fiscal, astfel cum rezultă din mesajul electronic de confirmare transmis ca urmare a primirii declarației."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 103 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Cum se stabilește, practic, dacă o declarație a fost depusă la termen:

- Pentru declarațiile depuse **electronic** (SPV), data depunerii este data **înregistrării pe portal**, confirmată prin **mesajul electronic de confirmare** — nu data la care contribuabilul a încărcat fișierul, dacă acesta nu a fost validat.
- Dacă declarația **nu este validată** din cauza erorilor, data depunerii este data **validării**, nu data transmiterii inițiale — cu o excepție: dacă declarația inițială a fost transmisă până la termenul legal, iar contribuabilul depune o declarație validă până la sfârșitul lunii în care se împlinește termenul, se păstrează data din mesajul transmis inițial (art. 103 alin. (5)).
- Pentru declarațiile depuse **la poștă**, data depunerii este **data poștei**, nu data la care ajunge fizic la organul fiscal.

## Ce se greșește în practică

- Se consideră declarația depusă la termen doar pentru că a fost încărcată în SPV înainte de scadență, fără verificarea mesajului de confirmare a validării — o declarație respinsă/nevalidată nu are, implicit, data transmiterii inițiale.
- Se ignoră excepția de la art. 103 alin. (5): dacă declarația inițială a picat la validare, dar se depune o versiune corectă până la sfârșitul lunii scadenței, data rămâne cea inițială — contribuabilii renunță uneori inutil la această „plasă de siguranță” și consideră declarația depusă târziu.
- Se confundă data confirmării de primire (generată automat) cu data validării conținutului — pot fi momente diferite, conform art. 103 alin. (4).

## Ce face iConta.eu

iConta.eu generează și transmite declarațiile fiscale suportate către SPV, dar confirmarea validării declarației și verificarea mesajului electronic de primire rămân un pas pe care utilizatorul îl urmărește în contul său SPV, în afara aplicației.

[iConta.eu](/)
