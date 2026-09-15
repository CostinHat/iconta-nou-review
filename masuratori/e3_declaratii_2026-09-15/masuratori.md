# Lotul „scrierile care ajung în cifre de declarație” — măsurători

Toate duratele sunt **măsurate** pe serverul de lucru (același pe care rulează poarta),
nu estimate. Fiecare are artefactul ei, ca să se poată reface.

| operație | artefact | durată |
|---|---|---|
| derivarea subsetului (rute x tabele x generatoare) | subset_dupa_lot.txt | 22.3 s |
| inventarul rutelor care scriu fără probă | rute_fara_proba_dupa_lot.txt | 1.7 s |
| probele lotului (36 + 1 datorie) | probe_lot.txt | 28.4 s |
| gărzile de clichet (rute probate) | clichete.txt | 24.2 s |

## Cifrele, înainte și după

```
SUBSET_FISCAL (rute care scriu in tabele citite de generatoare)   49  ->   8
RUTE_CARE_SCRIU_FARA_PROBA_IN_SUITA                              131  ->  88
RUTE_NENUMITE_NICAIERI                                             3  ->   3
```

Derivarea subsetului: `scripts/scan_scrieri_declaratii.py` — tabelele scrise de fiecare
rută (corpul ei real + depozitul nominal + un nivel de apeluri către module din `core/`)
∩ tabelele citite de generatoarele de declarații (`core/d*.py`, `core/bilant.py`).
