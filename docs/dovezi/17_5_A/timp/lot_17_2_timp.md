# Raport de timp — lotul 17.2

## (a) Fazele lotului

| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |
|---|---|---|---|---|---|
| parcurs_code | 3 | 0 | 0 | 5.5 | 116 |
| pytest | 40 | 0 | 2 | 86.7 | 1899 |
| hook | 7 | 0 | 0 | 10.6 | 94 |
| proba_contract | 1 | 0 | 0 | 0.0 | 0 |
| poarta_verificator | 2 | 0 | 0 | 2.8 | 83 |
| poarta_pytest | 2 | 0 | 0 | 18.1 | 545 |
| poarta_plasa | 2 | 0 | 0 | 38.1 | 1147 |
| pornire | 1 | 0 | 0 | 0.0 | 0 |
| verificator | 1 | 0 | 0 | 3.3 | 199 |
| publicare | 1 | 0 | 0 | 0.5 | 30 |
| restart | 1 | 0 | 0 | 0.2 | 14 |
| lucru_pana_la_commit | 1 | 0 | 0 | 30.2 | 1814 |
| lucru_pana_la_poarta | 1 | 0 | 0 | 112.8 | 6771 |
| asteptare_poarta | 2 | 0 | 0 | 59.0 | 1775 |
| dupa_verde | 1 | 0 | 0 | 87.9 | 5273 |
| pana_la_publicare | 1 | 0 | 0 | 12.5 | 752 |
| pytest_intre_commituri | 7 | 0 | 0 | 299.6 | 6142 |

## (b) Totaluri

- timp total (primul → ultimul rând al lotului): 303.0 min
- pornire → publicare: 82.2 min
- pytest, toate sesiunile: 40 sesiuni, 86.7 min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)
  - din care întrerupte: 0, 0.0 min
  - început fără sfârșit (ignorate în minute): 0
- fără dublă numărătoare (reuniune de intervale): poartă 59.0 min; pytest Code 70.4 min; restul 173.6 min (= timp total − reuniunea poartă ∪ pytest Code)
- sesiuni pytest: colectări 27; pornite în hook 7; pornite în poartă 2; ale lui Code 4

## (c) Timpul de lucru al lui Code

Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).
| fază | număr | minute |
|---|---|---|
| lucru_pana_la_commit | 1 | 30.2 |
| lucru_pana_la_poarta | 1 | 112.8 |
| asteptare_poarta | 2 | 59.0 |
| reparatie_dupa_rosu | 0 | 0.0 |
| dupa_verde | 1 | 87.9 |
| pana_la_publicare | 1 | 12.5 |

descriptiv, nu se adună (se suprapune cu celelalte faze):

| fază | număr | minute |
|---|---|---|
| pytest_intre_commituri | 7 | 299.6 |

## (d) Timpul arhitectului

fără jurnal arhitect
