# Așteptări F1 — ETAPA 8 (Declarații — generare) — scris ÎNAINTE de a rula

**Context:** după fluxul verificat (etapele 3-7), se generează declarațiile lunii septembrie 2026
(D100 trimestrial Q3) și se validează pe **validatorul oficial DUK** (`core/duk.py`, judecătorul final).
Regula bazei nule: o declarație validă cu bază 0 e EROARE — fiecare trebuie să reflecte operațiuni reale.

## Așteptat (generare + DUK, tenant_049)
| declarație | perioadă | DUK | cifre-cheie așteptate (din flux) |
|---|---|---|---|
| D300 (decont TVA) | sept lunar | **valid** | colectat R9 1000/210 (D1) + deductibil R22 1000/210 (D2) → TVA plată **0** |
| D394 (informativă) | sept lunar | **valid** | 1 livrare + 1 achiziție (nrFacturiL=1, nrFacturiA=1) |
| D112 (contribuții) | sept lunar | **valid** | impozit 688 (cod 602), CAS 3475 (412), CASS 1390 (432), CAM 313 (480); total control 5866 |
| D100 (micro) | Q3 trim | **valid** | cod 121 cotă 1%, suma 10 (=1% × venit 1000 din D1); totalPlata_A 20 (checksum R11b = 2×suma) |
| **D406 (SAF-T)** | sept lunar | **valid** | deblocat după reparația reconcilierii SPV↔stoc (finding închis, decizie Costin opțiunea 1) + curățarea F1 (cont 371, cantitate D2). GL 371 = fișă = 5.500, cantitate 110 buc |

**Precondiții completate ca date de test:** salarii ≥ salariul minim 4325 (4500/5000/4400); COR completat
(522102/331302/432101) — obligatoriu la D112.

**Temei:** cotele fiscale (TVA CF art.291, contribuții CF art.138/156/64/220^3, micro CF Titlul II) — din
generatoare, verificate anterior; salariul minim 4325 HG 146/2026. DUK = judecătorul structurii XML.
`totalPlata_A` = checksum de structură ANAF (nu valoare fiscală) — vezi lecția D301.
