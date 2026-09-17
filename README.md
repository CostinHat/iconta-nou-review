# PACHET DE AUDIT INDEPENDENT — iConta, 2026-09-17

Ramura asta NU e cod. E **materialul pentru un audit independent** asupra aplicatiei, asezat
langa codul pe care il descrie. Nu intra in `main` si nu participa la four-way.

**Commitul descris:** `d8034c54d62cc7ca8a82c2f1d6136ab87db86b69` (pe `main`)

## Ce e aici

| | |
|---|---|
| `pachet/` | pachetul despachetat, rasfoibil direct din browser |
| `iconta_AUDIT_2026-09-17.zip` | acelasi lucru, intr-un singur fisier |
| `pachet/INDEX.md` | **incepe de aici** — ce raspuns da fiecare piesa, si ce intrebare ramane fara raspuns |
| `pachet/MANIFEST.sha256` | amprenta fiecarui fisier; `sha256sum -c MANIFEST.sha256` |

**SHA-256 al arhivei:**

    d9cf701be44526f7027c533f47b27ebb463e8387104ead377dde2603948de0c8

## Inainte de publicare

Continutul a fost scanat mecanic pentru chei, parole, siruri de conexiune si continut de
baza, cu `audit/scan_secrete.py` din depozit. Raportul, integral, e in
`pachet/04_NEVERIFICAT/SCAN_SECRETE.txt` — cu ce s-a cautat, ce s-a gasit si unde, plus
impartirea pachetului in "deja public" si "nou" dupa amprenta de obiect git.

*Scanul nu spune "curat". Spune, pentru fiecare tipar, cate potriviri are si unde.*

## Cum reconstruiesti pachetul singur

    git checkout d8034c54d62cc7ca8a82c2f1d6136ab87db86b69
    bash audit/pachet.sh

Scriptul e in depozit tocmai ca afirmatia "pachetul e reproductibil" sa poata fi verificata.
