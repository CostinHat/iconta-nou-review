# Raport de timp — lotul 17.3

## (a) Fazele lotului

| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |
|---|---|---|---|---|---|
| pornire | 1 | 0 | 0 | 0.0 | 0 |
| pytest | 43 | 0 | 5 | 23.1 | 470 |
| parcurs_code | 3 | 0 | 0 | 1.5 | 31 |
| hook | 8 | 0 | 2 | 12.3 | 94 |
| proba_contract | 1 | 0 | 0 | 0.0 | 0 |
| verificator | 1 | 0 | 0 | 0.9 | 54 |
| poarta_verificator | 1 | 0 | 0 | 1.4 | 84 |
| poarta_pytest | 1 | 0 | 0 | 9.2 | 550 |
| poarta_plasa | 1 | 0 | 1 | 18.3 | 1096 |
| lucru_pana_la_commit | 1 | 0 | 0 | 32.9 | 1972 |
| lucru_pana_la_poarta | 1 | 0 | 0 | 417.5 | 25048 |
| asteptare_poarta | 1 | 0 | 1 | 28.8 | 1730 |
| pytest_intre_commituri | 9 | 0 | 0 | 450.3 | 8098 |

## (b) Totaluri

- timp total (primul → ultimul rând al lotului): 479.2 min
- pornire → publicare: lipsă (nu există rând «inceput» al fazei «publicare» după ultimul verdict)
- pytest, toate sesiunile: 43 sesiuni, 23.1 min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)
  - din care întrerupte: 0, 0.0 min
  - început fără sfârșit (ignorate în minute): 0
- fără dublă numărătoare (reuniune de intervale): poartă 28.8 min; pytest Code 14.2 min; restul 436.2 min (= timp total − reuniunea poartă ∪ pytest Code)
- sesiuni pytest: colectări 18; pornite în hook 8; pornite în poartă 1; ale lui Code 16

## (c) Timpul de lucru al lui Code

Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).
| fază | număr | minute |
|---|---|---|
| lucru_pana_la_commit | 1 | 32.9 |
| lucru_pana_la_poarta | 1 | 417.5 |
| asteptare_poarta | 1 | 28.8 |
| reparatie_dupa_rosu | 0 | 0.0 |
| dupa_verde | 0 | 0.0 |
| pana_la_publicare | 0 | 0.0 |

descriptiv, nu se adună (se suprapune cu celelalte faze):

| fază | număr | minute |
|---|---|---|
| pytest_intre_commituri | 9 | 450.3 |

## (d) Timpul arhitectului

fără jurnal arhitect
