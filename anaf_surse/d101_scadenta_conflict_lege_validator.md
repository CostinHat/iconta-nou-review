# D101 scadenta platii - CONFLICT lege vs validator DUKIntegrator (evidenta 03.08.2026)

## Regula in cod (urmeaza validatorul oficial)
core/d101.py: _scadenta_pana_2025? NU - functiile sunt _scadenta_2022 (2022-2025 -> LL+6=iunie) si
_scadenta_2026 (2026+ -> LL+3=martie). Dispecerat prin _VARIANTE_SCADENTA pe anul Data_S.

## Legea (verificat la sursa)
CF art.42(1) - Legea 227/2015, Depunerea declaratiei de impozit pe profit:
- Text ORIGINAR (in vigoare 2016 -> feb.2026): "...pana la data de 25 MARTIE inclusiv a anului urmator".
- Modificat de OUG nr.8/2026 art.6 pct.12 (MO nr.147 din 25 februarie 2026): "...pana la data de 25 IUNIE inclusiv
  a anului urmator". Verbatim art.6 pct.12: "La articolul 42, alineatele (1) si (2) se modifica si vor avea urmatorul
  cuprins: (1) Contribuabilii au obligatia sa depuna o declaratie anuala privind impozitul pe profit pana la data de
  25 iunie inclusiv a anului urmator...".
- Aplicabilitate: OUG 8/2026 art.45 alin.(21^4): "Prevederile art.42 alin.(1) si (2)... se aplica incepand cu
  declaratia anuala privind impozitul pe profit aferenta anului 2026..."; art.10 alin.(2): "...se aplica incepand cu
  anul fiscal 2026". => declaratia pt an fiscal 2025 (depusa 2026) = INCA 25 martie; pt an fiscal 2026 (depusa 2027)
  = 25 iunie.
- Surse: static.anaf.ro/static/10/Anaf/legislatie/OUG_8_2026.pdf ; legislatie.just.ro/Public/DetaliiDocumentAfis/307580
  ; ro.wolterskluwer.ro/art-42-depunerea-declaratiei-de-impozit-pe-profit/ (text "25 martie" pre-modificare).

## Validatorul OFICIAL DUKIntegrator INSTALAT (testat direct 03.08.2026, toti anii)
- Data_S 2023/2024/2025 -> "Err R17 Scadenta platii: ... an Data_S >=2022 si an Data_S <=2025 atunci [LL+6]" -> cere
  IUNIE, respinge martie.
- Data_S 2026 -> "Err R17.1 Scadenta platii: daca Data_l=null si data_b=null atunci LL=LL+3 ... din data_s
  (31.12.2026)" -> cere MARTIE (03), respinge iunie (06).

## Concluzie
Legea si validatorul oficial ANAF sunt EXACT INVERSATE pe scadenta D101. Jar-ul instalat nu are inca OUG 8/2026.
Ramane decizie de produs (DECIZII.md 03.08.2026) + verificare autoritara a termenului 2022-2025.
