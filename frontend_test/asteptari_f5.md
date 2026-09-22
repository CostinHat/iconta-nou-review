# Așteptări F5 — SRL cu salariați (D112, REGES-ONLINE) — scris ÎNAINTE de a rula

**Profil (Sesiunea B):** **SRL cu salariați**, micro, neplătitor TVA. tenant_053, Cabinet A. Testează
ce a fost N/A la F1-F4: **salarizarea → D112** (declarația de contribuții) și **REGES-ONLINE** (registrul
de evidență a salariaților, Inspecția Muncii).

- **CUI:** 40510009 (checksum valid). **tip_firma:** srl. **CAEN:** 6201.
- **Set declarații:** **D112** (CAS/CASS/impozit pe salarii). NU D200/D212 (nu e PFA).

## Etapa 4 — salarizare (2 salariați)
| salariat | brut | CAS 25% | CASS 10% | impozit 10% |
|---|---|---|---|---|
| Ionescu Vasile (COR 817207) | 5.000 | 1.250 | 500 | pe bază după deduceri |
| Popescu Elena (COR 831204) | 6.000 | 1.500 | 600 | pe bază după deduceri |

- **CNP** checksum-valid (algoritm oficial); **COR** din nomenclator (`public.cor_ocupatii`).
- **Stat de plată** din `stat_plata_api.stat_plata` — CAS/CASS/impozit/net per salariat.

## Etapa 8 — D112 + DUK
- **D112** generată din statul de plată (cei 2 asigurați) → **valid** pe DUK.

## REGES-ONLINE — [EXTERN]
- `core/reges_client.py` = client REGES (api.inspectiamuncii.ro), OpenID password grant per CUI.
  **Submit live cere credențiale Inspecția Muncii per firmă** → [EXTERN], confirmat **structural**
  (RegesClient + `mesaj_inregistrare_salariat`/`mesaj_adaugare_contract`/`mesaj_incetare_contract`),
  nu live (ca depunerea SPV la F1 etapa 9).

## Etapele N/A / minime
- **3 documente:** minime (focusul e salarizarea). **5 contabilizare:** nota de salarii din stat.
  **6 mijloace fixe:** N/A. **7 control fiscal:** semafor (D112 datorată).

**Temei:** CAS 25% / CASS 10% CF art. 138/156; impozit 10% CF art. 78; D112 OPANAF; REGES Legea 53/2003
+ HG 905/2017 (registru). Cifrele din generatoare + DUK, confirmate la rulare.
