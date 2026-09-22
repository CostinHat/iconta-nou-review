# Așteptări F4 — PFA sistem real — scris ÎNAINTE de a rula

**Profil (Sesiunea B):** **PFA sistem real** (partidă simplă, impozit pe venit), **neplătitor TVA**.
tenant_052, Cabinet A. Prioritate: validează **familia de declarații D2xx** (PF/venituri), confirmate
funcționale în cod (`test_declaratii_lot2-6_duk.py`), dar cu **Stare stale în FUNCTIONALITATI.csv**.

- **CUI:** 40410000 (cifra de control verificată offline).
- **Denumire:** F4 PFA Sistem Real.
- **Regim:** `tip_firma='pfa'` (partidă simplă) → ascunde cardurile de partidă dublă, arată **Încasări/plăți (RIP)**.
- **Vector:** neplătitor TVA, sistem real, impozit pe venit. CAEN 6201.
- **Set declarații (PFA sistem real):** **D212** (Declarația unică — venit net + CAS/CASS pe plafoane,
  din RIP), **D200** (venituri realizate din RO). NU D300/D394/D112/D406 (partidă dublă / plătitor TVA / salariați).

## Etapa 1-2 — creare + vector (partidă simplă)
| ce | valoare |
|---|---|
| tip_firma | **pfa** |
| platitor_tva | **false** |
| CUI | 40410000 (checksum valid) |
| CAEN | 6201 |

## Planul F4 (etapele 3-8)
- **3 documente:** operațiuni RIP (registru încasări/plăți) — încasări (venituri) + plăți (cheltuieli deductibile).
- **4 salariați:** N/A (fără salariați).
- **5 contabilizare:** partidă simplă (RIP e evidența; nu note de partidă dublă).
- **6 mijloace fixe:** N/A (fără mijloace fixe la profilul de bază).
- **7 control fiscal:** semafor parțial acceptat la PFA (verifică coerența RIP).
- **8 declarații:** D212 (Fișa din RIP) + D200 + validare DUK; **plus validarea familiei D2xx** și
  actualizarea Stare în FUNCTIONALITATI.csv pentru cele confirmate.

## Capcane / temei
- **Confuzia partidă simplă (PFA) ↔ partidă dublă (SRL)** — F189: PFA nu are Declarații/Registru jurnal/
  Balanță/Bilanț; are RIP → D212.
- **Temei:** D212 sistem real CF art. 148-149, 154, 170; RIP OMFP 170/2015; D200 CF art. 122.
  Cifrele din generatoare + DUK, confirmate la rulare.
