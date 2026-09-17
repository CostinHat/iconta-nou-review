# OGLINDA PUBLICĂ

Depozitul se publică automat, de hook-ul `post-commit`, la FIECARE commit, cu contract
fast-forward (niciodată `--force`). Pentru audit se folosește oglinda **publică**:

    https://github.com/CostinHat/iconta-nou-review.git

(`origin` e depozitul PRIVAT; nu-l poți clona și nu e nevoie.)

**Commitul de referință al pachetului:**

    d8034c54d62cc7ca8a82c2f1d6136ab87db86b69

## Verifică singur, fără să ne crezi

    git ls-remote https://github.com/CostinHat/iconta-nou-review.git refs/heads/main

Rulat ANONIM (fără chei, `GIT_TERMINAL_PROMPT=0`) la data pachetului, a răspuns:

    d8034c54d62cc7ca8a82c2f1d6136ab87db86b69	refs/heads/main

## Cele patru referințe, pe același commit

Four-way-ul închis de `post-commit` cere ca HEAD, `origin/main`, copia de siguranță a zilei
și **toate** procesele vii de producție să poarte același commit. La data pachetului:

    HEAD                                         d8034c54d62cc7ca8a82c2f1d6136ab87db86b69
    origin/main                                  d8034c54d62cc7ca8a82c2f1d6136ab87db86b69
    public/main                                  d8034c54d62cc7ca8a82c2f1d6136ab87db86b69
    origin/backup/lant-2026-09-17                d8034c54d62cc7ca8a82c2f1d6136ab87db86b69

Ultimele rânduri ale porții care a produs commitul — inclusiv `FOUR-WAY INCHIS` — sunt în
`06_ARTEFACTE/`.
