# Raport de timp — lotul 17.2-A

## (a) Fazele lotului

| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |
|---|---|---|---|---|---|
| pornire | 1 | 0 | 0 | 0.0 | 0 |
| pytest | 38 | 0 | 11 | 21.0 | 476 |
| hook | 4 | 0 | 0 | 6.1 | 94 |
| proba_contract | 1 | 0 | 0 | 0.0 | 0 |
| poarta_verificator | 1 | 0 | 0 | 1.4 | 83 |
| poarta_pytest | 1 | 0 | 0 | 8.9 | 536 |
| poarta_plasa | 1 | 0 | 0 | 19.0 | 1138 |
| publicare | 1 | 0 | 0 | 0.5 | 27 |
| restart | 1 | 0 | 0 | 0.2 | 14 |
| lucru_pana_la_commit | 1 | 0 | 0 | 67.5 | 4051 |
| lucru_pana_la_poarta | 1 | 0 | 0 | 28.9 | 1732 |
| asteptare_poarta | 1 | 0 | 0 | 29.3 | 1757 |
| pana_la_publicare | 1 | 0 | 0 | 3.1 | 184 |
| pytest_intre_commituri | 4 | 0 | 0 | 127.0 | 4051 |

## (b) Totaluri

- timp total (primul → ultimul rând al lotului): 129.2 min
- pornire → publicare: 128.7 min
- pytest, toate sesiunile: 38 sesiuni, 21.0 min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)
  - din care întrerupte: 0, 0.0 min
  - început fără sfârșit (ignorate în minute): 0
- fără dublă numărătoare (reuniune de intervale): poartă 29.3 min; pytest Code 12.9 min; restul 87.0 min (= timp total − reuniunea poartă ∪ pytest Code)
- sesiuni pytest: colectări 18; pornite în hook 4; pornite în poartă 1; ale lui Code 15

## (c) Timpul de lucru al lui Code

Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).
| fază | număr | minute |
|---|---|---|
| lucru_pana_la_commit | 1 | 67.5 |
| lucru_pana_la_poarta | 1 | 28.9 |
| asteptare_poarta | 1 | 29.3 |
| reparatie_dupa_rosu | 0 | 0.0 |
| dupa_verde | 0 | 0.0 |
| pana_la_publicare | 1 | 3.1 |

descriptiv, nu se adună (se suprapune cu celelalte faze):

| fază | număr | minute |
|---|---|---|
| pytest_intre_commituri | 4 | 127.0 |

## (d) Timpul arhitectului

fără jurnal arhitect
