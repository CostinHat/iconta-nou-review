# Raport de timp — lotul 17.1

## (a) Fazele lotului

| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |
|---|---|---|---|---|---|
| parcurs_code | 4 | 0 | 0 | 7.7 | 125 |
| pytest | 40 | 1 | 5 | 97.2 | 2339 |
| hook | 8 | 0 | 0 | 12.2 | 92 |
| proba_contract | 1 | 0 | 0 | 0.0 | 0 |
| poarta_verificator | 2 | 0 | 0 | 2.8 | 84 |
| poarta_pytest | 2 | 0 | 1 | 19.1 | 602 |
| poarta_plasa | 2 | 0 | 0 | 34.0 | 1024 |
| pornire | 1 | 0 | 0 | 0.0 | 0 |
| verificator | 1 | 0 | 0 | 4.0 | 239 |
| publicare | 1 | 0 | 0 | 0.5 | 29 |
| restart | 1 | 0 | 0 | 0.2 | 13 |
| lucru_pana_la_commit | 1 | 0 | 0 | 30.8 | 1845 |
| lucru_pana_la_poarta | 1 | 0 | 0 | 179.6 | 10773 |
| asteptare_poarta | 2 | 0 | 1 | 55.9 | 1710 |
| reparatie_dupa_rosu | 1 | 0 | 0 | 224.2 | 13455 |
| pana_la_publicare | 1 | 0 | 0 | 18.8 | 1128 |
| pytest_intre_commituri | 8 | 0 | 0 | 506.4 | 15182 |

## (b) Totaluri

- timp total (primul → ultimul rând al lotului): 602.0 min
- pornire → publicare: 53.4 min
- pytest, toate sesiunile: 41 sesiuni, 154.2 min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)
  - din care întrerupte: 1, 57.0 min
  - început fără sfârșit (ignorate în minute): 0
- fără dublă numărătoare (reuniune de intervale): poartă 55.9 min; pytest Code 136.8 min; restul 409.3 min (= timp total − reuniunea poartă ∪ pytest Code)
- sesiuni pytest: colectări 23; pornite în hook 8; pornite în poartă 2; ale lui Code 8

## (c) Timpul de lucru al lui Code

Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).
| fază | număr | minute |
|---|---|---|
| lucru_pana_la_commit | 1 | 30.8 |
| lucru_pana_la_poarta | 1 | 179.6 |
| asteptare_poarta | 2 | 55.9 |
| reparatie_dupa_rosu | 1 | 224.2 |
| dupa_verde | 0 | 0.0 |
| pana_la_publicare | 1 | 18.8 |

descriptiv, nu se adună (se suprapune cu celelalte faze):

| fază | număr | minute |
|---|---|---|
| pytest_intre_commituri | 8 | 506.4 |

## (d) Timpul arhitectului

fără jurnal arhitect
