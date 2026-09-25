---
title: "Penalizarea pentru plata cu întârziere a impozitului pe profit"
description: "Ce dobânzi și penalități de întârziere se calculează atunci când impozitul pe profit nu este plătit la scadență."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Penalizarea pentru plata cu întârziere a impozitului pe profit

Impozitul pe profit neplătit la termenul legal nu generează o singură „penalizare", ci două obligații accesorii distincte, cu niveluri diferite: dobânda și penalitatea de întârziere. Ambele curg zi de zi, de la scadență până la data stingerii efective a debitului.

## Temeiul legal

::: ghid-temei
„ART. 174 Dobânzi
(1) Dobânzile se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...]
(5) Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere.
ART. 176 Penalități de întârziere
(1) Penalitățile de întârziere se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv. [...]
(2) Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere.
(3) Penalitatea de întârziere nu înlătură obligația de plată a dobânzilor."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 174 alin. (1), (5) și art. 176 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- **Dobânda**: 0,02% pe zi de întârziere, calculată din ziua următoare scadenței (25 ale lunii, pentru trimestrul aferent, la impozitul pe profit) și până la data plății efective, inclusiv.
- **Penalitatea de întârziere**: 0,01% pe zi de întârziere, calculată în paralel cu dobânda, pe același interval.
- Cele două obligații se cumulează — plata dobânzii nu scutește de penalitate și invers (art. 176 alin. (3)).
- Dacă impozitul nedeclarat corect este stabilit ulterior de organul fiscal printr-o decizie de impunere (nu doar plătit cu întârziere, ci nedeclarat), se aplică suplimentar penalitatea de nedeclarare de 0,08% pe zi (art. 181), care nu se cumulează cu penalitatea de întârziere de la art. 176 pentru aceleași sume.

## Ce se greșește în practică

- Se calculează doar dobânda, ignorând penalitatea de întârziere de 0,01%/zi, care se aplică separat și simultan.
- Se confundă penalitatea de întârziere (0,01%/zi, pentru plata cu întârziere a unei sume corect declarate) cu penalitatea de nedeclarare (0,08%/zi, pentru sume nedeclarate sau declarate greșit și stabilite ulterior de ANAF) — sunt regimuri diferite, cu baze legale și niveluri diferite.
- Se oprește calculul la data plății, fără a include și ziua stingerii, deși legea prevede „până la data stingerii sumei datorate, inclusiv".
- Se ignoră faptul că nivelul dobânzii și al penalității poate fi actualizat prin hotărâre de Guvern, în funcție de rata dobânzii de referință BNR (art. 173 alin. (6)) — valorile curente trebuie verificate, nu presupuse fixe pe termen nelimitat.

## Ce face iConta.eu

iConta.eu calculează și urmărește scadențele fiscale (inclusiv cea a impozitului pe profit) prin modulul de scadențar, care avertizează contabilul înainte de termenul legal. La data acestui ghid, aplicația **nu calculează automat dobânzile și penalitățile de întârziere** pentru sumele plătite după scadență — acest calcul rămâne o operațiune manuală sau se preia din decizia emisă de ANAF, pe baza nivelurilor de mai sus.

[iConta.eu](/)
