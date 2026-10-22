# PILOT — criteriile de pornire (comanda Costin 11.2 pct.5, verbatim în DECIZII „Comanda 11.2”)

> „până la pilot nu intră funcții noi, doar reparații. Pilotul pornește când o lună completă de contabil merge cap-coadă pe o firmă fără
> deficiențe grave: facturi, bancă, casă, stoc, salarii, închidere, D300, D394, D112, D100, balanță.”

Un domeniu e „probat” când luna completă a trecut prin el pe aceeași firmă, cap-coadă, fără deficiență gravă deschisă; rândul numește
atunci firma, luna și dovada (capturile din `dovezi/`, ca la DEFICIENTE, comanda 11.2 pct.3). Stările: `neprobat` / `în probă` / `probat`.
Pilotul pornește numai când toate cele 11 sunt „probat” pe aceeași firmă și aceeași lună — decizia de pornire e a lui Costin. Până
atunci, garda `core/test_fara_functii_noi.py` oprește orice funcție nouă (rută, funcționalitate, trecere în LIVE) care nu repară o
deficiență numită. Forma tabelului e păzită de aceeași gardă (`test_criteriile_pilotului_sunt_cele_11_domenii_cu_stare`).

| # | domeniu | stare | probă (firma: … · luna: … · dovadă: …) |
|---|---|---|---|
| 1 | facturi | neprobat | |
| 2 | bancă | neprobat | |
| 3 | casă | neprobat | |
| 4 | stoc | neprobat | |
| 5 | salarii | neprobat | |
| 6 | închidere | neprobat | |
| 7 | D300 | neprobat | |
| 8 | D394 | neprobat | |
| 9 | D112 | neprobat | |
| 10 | D100 | neprobat | |
| 11 | balanță | neprobat | |
