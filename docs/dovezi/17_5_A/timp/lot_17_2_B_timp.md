# Raport de timp — lotul 17.2-B

## (a) Fazele lotului

| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |
|---|---|---|---|---|---|
| pornire | 1 | 0 | 0 | 0.0 | 0 |
| pytest | 31 | 0 | 5 | 23.2 | 472 |
| hook | 5 | 0 | 0 | 7.5 | 92 |
| proba_contract | 1 | 0 | 0 | 0.0 | 0 |
| poarta_verificator | 1 | 0 | 0 | 1.4 | 83 |
| poarta_pytest | 1 | 0 | 0 | 9.1 | 543 |
| poarta_plasa | 1 | 0 | 0 | 19.1 | 1143 |
| publicare | 1 | 0 | 0 | 0.4 | 26 |
| restart | 1 | 0 | 0 | 0.2 | 13 |
| lucru_pana_la_commit | 1 | 0 | 0 | 38.8 | 2327 |
| lucru_pana_la_poarta | 1 | 0 | 0 | 62.9 | 3771 |
| asteptare_poarta | 1 | 0 | 0 | 29.5 | 1769 |
| pana_la_publicare | 1 | 0 | 0 | 1.8 | 106 |
| pytest_intre_commituri | 6 | 0 | 0 | 101.6 | 2676 |

## (b) Totaluri

- timp total (primul → ultimul rând al lotului): 133.3 min
- pornire → publicare: 132.9 min
- pytest, toate sesiunile: 31 sesiuni, 23.2 min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)
  - din care întrerupte: 0, 0.0 min
  - început fără sfârșit (ignorate în minute): 0
- fără dublă numărătoare (reuniune de intervale): poartă 29.5 min; pytest Code 14.7 min; restul 89.2 min (= timp total − reuniunea poartă ∪ pytest Code)
- sesiuni pytest: colectări 18; pornite în hook 5; pornite în poartă 1; ale lui Code 7

## (c) Timpul de lucru al lui Code

Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).
| fază | număr | minute |
|---|---|---|
| lucru_pana_la_commit | 1 | 38.8 |
| lucru_pana_la_poarta | 1 | 62.9 |
| asteptare_poarta | 1 | 29.5 |
| reparatie_dupa_rosu | 0 | 0.0 |
| dupa_verde | 0 | 0.0 |
| pana_la_publicare | 1 | 1.8 |

descriptiv, nu se adună (se suprapune cu celelalte faze):

| fază | număr | minute |
|---|---|---|
| pytest_intre_commituri | 6 | 101.6 |

## (d) Timpul arhitectului

fără jurnal arhitect
