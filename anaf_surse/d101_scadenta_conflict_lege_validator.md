# D101 scadenta platii - lege vs validator DUKIntegrator: REZOLVAT (03.08.2026)

## Concluzie (dupa verificare autoritara)
Valorile din cod (2022-2025 -> 25 iunie; 2026 -> 25 martie) urmeaza validatorul oficial DUKIntegrator SI sunt
legal corecte. Nu exista conflict de fond - prima cercetare ratase actul care a mutat termenul la iunie.

## Temei 2022-2025 = 25 IUNIE: OUG nr.153/2020
Ordonanta de urgenta a Guvernului nr.153/2020 pentru instituirea unor masuri fiscale de stimulare a mentinerii/
cresterii capitalurilor proprii. Publicata in MONITORUL OFICIAL nr.817 din 4 septembrie 2020 (rectificare MO 861/
21.09.2020, nu atinge termenul).
- Art.I alin.(13) lit.a) VERBATIM: "Pe perioada aplicarii prevederilor prezentului articol, termenele pentru
  depunerea declaratiilor si pentru plata impozitului sunt urmatoarele: a) pentru contribuabilii platitori de
  impozit pe profit, prin derogare de la prevederile art.41 si 42 din Codul fiscal, termenul pentru depunerea
  declaratiei anuale privind impozitul pe profit si plata impozitului pe profit aferent anului fiscal respectiv
  este pana la data de 25 iunie inclusiv a anului urmator, iar pentru contribuabilii care intra sub incidenta
  prevederilor art.16 alin.(5) din Codul fiscal pana la data de 25 a celei de-a sasea luni inclusiv de la
  inchiderea anului fiscal modificat...".
- Art.VI VERBATIM: "Prevederile art.I intra in vigoare incepand cu data de 1 ianuarie 2021 si se aplica pentru
  perioada 2021-2025."
- Derogarea e GENERALA (toti platitorii de impozit pe profit), nu doar grupuri fiscale.
- Surse: legislatie.just.ro/Public/DetaliiDocument/229768 (forma originala); DetaliiDocumentAfis/230106 (consolidat);
  static.anaf.ro/static/10/Anaf/legislatie/OUG_153_2020.pdf.

## Temei 2026+ = 25 MARTIE (baza) -> 25 IUNIE (OUG 8/2026)
- Baza art.42(1) CF (Legea 227/2015): "25 martie inclusiv a anului urmator" - se aplica pentru fiscal 2026 dupa
  incheierea schemei OUG 153/2020. E ce cere DUKIntegrator instalat azi (R17.1: LL+3).
- OUG nr.8/2026 art.6 pct.12 (MO nr.147 din 25 februarie 2026): modifica art.42(1) la "25 iunie", aplicabil de la
  declaratia aferenta anului fiscal 2026 (art.45 alin.21^4 + art.10 alin.2). Jar-ul DUK instalat inca nu are aceasta
  modificare; D101 pt fiscal 2026 se depune in 2027, cand validatorul va fi actualizat.

## Proba DUKIntegrator instalat (testat 03.08.2026)
Data_S 2023/2024/2025 -> R17 cere LL+6 (iunie), respinge martie. Data_S 2026 -> R17.1 cere LL+3 (martie), respinge
iunie. Coincide exact cu: 2021-2025 iunie (OUG 153/2020), 2026 martie (baza, schema incheiata).

## Decizie (DECIZII.md 03.08.2026)
Tool-ul urmeaza validatorul pe ambele ramuri (valori si legal corecte pe 2022-2025). Cand jar-ul adopta OUG 8/2026
pe 2026, probele DUK pe an=2026 pica automat -> semnal sa treci _scadenta_2026 la iunie.

sha256(continut de mai sus, fara aceasta linie): 6dc14b8350ddea4254c6846dddf6b6393dd1ba24b54a3be257fc3e6321a680d1
