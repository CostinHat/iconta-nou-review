# AMENDAMENT la raportul `_trimite_brevo` — explicația „35 → 20" era greșită

*11.09.2026. Cifrele regenerate NU se ating: sunt corecte. Se corectează explicația mea.*

## Ce am scris, și de ce era greșit

Am scris, în raport și în mesajul commitului `0e6560ce`: *„`T05` trece de la 35 la 20 de firme…
Cauza e chiar incidentul de azi-dimineață — cele 12 firme-fantomă au ieșit din numărătoarea
activă."*

**35 − 20 = 15, nu 12.** Nu am verificat aritmetica înainte de a numi cauza. Și mecanismul era
greșit, nu doar numărul.

## Ce numără de fapt metrica

`METRIC_DEFINITION` = numărul de **scheme** (de firmă sau de test) care au **cel puțin un rând** în
cel puțin una dintre cele patru tabele ale traseului T05 — `inregistrari`, `inregistrari_linii`,
`plan_conturi`, `registru_inventar` — citite **live**, din baza pe care rulează instrumentul
(`scan_trasee.construieste(cu_db=True)`).

## De ce 35 → 20

`WHY_35_TO_20` = **cele două numere nu măsoară aceeași bază.** `35` a fost produs rulând
instrumentul pe **producție**, în tura de noapte de pe 11.09. `20` e produs rulând același
instrument pe **baza izolată de test**, restaurată din dumpul de `2026-09-10 03:00` — acolo rulează
suita de la R68 încoace, deci acolo se regenerează și antetul.

Producția poartă, pe lângă cele 20 de scheme de firmă reale, un set de scheme `ztest_*` — reziduu
al rulărilor de suită de dinainte de R68. Dumpul din care se restaurează baza de test e **anterior**
creării lor, deci ele nu există acolo.

Măsurat pe trei instantanee, cu același instrument:

| bază | T05 |
|---|---|
| dump `2026-09-10 03:00` (= baza de test de azi) | **20** |
| dump `2026-09-11 03:00` | **37** |
| producție, acum | **37** |

## Clasificarea celor 15

```
TENANTS_REMOVED_BY_R68_DISABLED=0
```

**Zero, nu 12.** Cele 12 firme dezactivate n-au **nicio schemă** — exact de-aia a picat P2, care
compara 49 de firme active cu 37 de proiecții. O firmă fără schemă n-a fost numărată niciodată de
metrica asta, nici înainte, nici după. Afirmația mea era greșită în ambele direcții: și ca număr, și
ca mecanism.

```
OTHER_COUNT_DELTA=15
OTHER_COUNT_DELTA_IDS_OR_KEYS=scheme `ztest_*` din producție, absente din dumpul de 10.09:
  ztest_ordine_poarta · ztest_p4 · ztest_sv_a5 · ztest_sv_d101a · ztest_sv_d101b · ztest_sv_d101c
  ztest_sv_d101d · ztest_sv_d101e · ztest_sv_d101f · ztest_sv_d101g · ztest_sv_d394a
  ztest_sv_d394b · ztest_sv_d394c · ztest_sv_ef_a · ztest_sv_ef_b · ztest_sv_ef_c · ztest_sv_ef_d
OTHER_COUNT_DELTA_REASON=prezente în producție (unde s-a măsurat 35), absente din baza izolată
  (unde se măsoară 20), fiindcă au fost create pe 11.09 între 00:07 și 00:58 — după momentul
  dumpului din care se restaurează baza de test.
```

## Ce NU pot închide mecanic, declarat

Lista de mai sus are **17** nume, iar delta e **15**. Cele două instantanee care încadrează
momentul dau **20** și **37**; valoarea `35` a fost produsă între ele, când două dintre cele 17
încă nu aveau rânduri în tabelele lui T05.

**Nu pot numi care două.** Cincisprezece dintre ele sunt numărate prin `plan_conturi`, care **n-are
coloană de timp**, iar între `00:07` și `03:00` nu există niciun instantaneu. Singurele două care se
pot data — `ztest_perechi_gen` (`00:50:45`) și `ztest_smoke_duk` (`00:58:00`) — sunt candidatele
plauzibile, dar plauzibil nu e măsurat, și nu-l scriu ca și cum ar fi.

Deci:

```
BREVO_REPORT_CONSISTENCY=PARTIAL
  · clasa întreagă a celor 15: EXPLICATĂ MECANIC (scheme ztest_* din producție, absente din baza izolată)
  · afirmația greșită (cele 12): CORECTATĂ — contribuția lor reală e 0
  · identitatea exactă a 2 din 17: NEDETERMINABILĂ din artefactele existente
```

## Ce rămâne adevărat

Cifra **20** din `TRASEE_VERIFICARI.md` e corectă și nu se atinge: e ce măsoară instrumentul în
mediul în care rulează suita, iar garda `test_trasee` o compară cu exact acea măsurătoare. `35` era
o măsurătoare pe altă bază, ajunsă în document printr-o regenerare făcută înainte ca suita să se
mute pe baza izolată.

`BREVO_STATUS=CLOSED_ACCEPTED` · `BREVO_REOPEN_REQUIRED=NO` — nimic din codul familiei nu e atins de
amendamentul ăsta.

---

## Verdictul arhitectului (11.09.2026)

```
DELTA_ACCOUNTED_FOR=YES
CLASS_EXPLANATION_MECHANICALLY_PROVEN=YES
UNRECOVERABLE_HISTORICAL_IDENTITY_EXPLICITLY_DECLARED=YES
UNPROVEN_IDENTITY_CLAIMS=0

EXACT_TWO_SCHEMAS_IDENTIFIED=NO
IDENTIFICATION_RECOVERABLE_FROM_EXISTING_EVIDENCE=NO
EVIDENCE_LIMITATION=DOCUMENTED

BREVO_REPORT_CONSISTENCY=PARTIAL_ACCEPTED_WITH_EVIDENCE_LIMITATION
BREVO_STATUS=CLOSED_ACCEPTED
BREVO_REOPEN_REQUIRED=NO
```

**Limitare permanentă de trasabilitate istorică, nu blocaj funcțional.** Regula de acum înainte nu
mai e „toate cele 15 se identifică nominal" — ceea ce e imposibil retroactiv —, ci: delta se
contabilizează, clasa se dovedește mecanic, identitatea nerecuperabilă se **declară**, iar numărul
afirmațiilor de identitate nedovedite rămâne **zero**.
