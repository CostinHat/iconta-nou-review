# Raport de timp — lotul 16.7

## (a) Fazele lotului

| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |
|---|---|---|---|---|---|
| pornire | 1 | 0 | 0 | 0.0 | 0 |
| pytest | 38 | 0 | 5 | 39.4 | 746 |
| hook | 6 | 1 | 0 | 15.8 | 160 |
| proba_contract | 1 | 0 | 0 | 0.0 | 0 |
| poarta_verificator | 2 | 0 | 0 | 4.9 | 148 |
| poarta_pytest | 2 | 0 | 0 | 27.4 | 830 |
| poarta_plasa | 1 | 1 | 0 | 15.2 | 909 |
| publicare | 1 | 0 | 0 | 0.5 | 31 |
| restart | 1 | 0 | 0 | 0.2 | 15 |
| lucru_pana_la_commit | 1 | 0 | 0 | 32.7 | 1961 |
| lucru_pana_la_poarta | 1 | 0 | 0 | 65.9 | 3956 |
| asteptare_poarta | 2 | 0 | 1 | 48.9 | 1867 |
| reparatie_dupa_rosu | 1 | 0 | 0 | 3.8 | 227 |
| pana_la_publicare | 1 | 0 | 0 | 5.2 | 312 |
| pytest_intre_commituri | 7 | 0 | 0 | 153.8 | 2403 |

## (b) Totaluri

- timp total (primul → ultimul rând al lotului): 157.0 min
- pornire → publicare: 156.5 min
- pytest, toate sesiunile: 38 sesiuni, 39.4 min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)
  - din care întrerupte: 0, 0.0 min
  - început fără sfârșit (ignorate în minute): 0
- fără dublă numărătoare (reuniune de intervale): poartă 48.9 min; pytest Code 13.1 min; restul 95.0 min (= timp total − reuniunea poartă ∪ pytest Code)
- sesiuni pytest: colectări 19; pornite în hook 7; pornite în poartă 2; ale lui Code 10

## (c) Timpul de lucru al lui Code

Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).
| fază | număr | minute |
|---|---|---|
| lucru_pana_la_commit | 1 | 32.7 |
| lucru_pana_la_poarta | 1 | 65.9 |
| asteptare_poarta | 2 | 48.9 |
| reparatie_dupa_rosu | 1 | 3.8 |
| dupa_verde | 0 | 0.0 |
| pana_la_publicare | 1 | 5.2 |

descriptiv, nu se adună (se suprapune cu celelalte faze):

| fază | număr | minute |
|---|---|---|
| pytest_intre_commituri | 7 | 153.8 |

## (d) Timpul arhitectului

fără jurnal arhitect
