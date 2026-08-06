# PLAN_B — Verificare vizuală de către contabil (nu suită automată)

> Rescris 06.08.2026. **E1–E12 NU se execută în această campanie — acesta e DOAR documentul.**

## De ce PLAN_B (și ce NU prinde suita automată)

Suita automată (gărzile pytest) sunt **scanere de sursă**: verifică reguli pe cod (markeri, diacritice,
clase de buton, contracte de mesaj, izolare pe rute, reconcilieri numerice). Ele **nu văd**:
- **Randarea** — dacă un ecran *arată* corect (aliniere, câmpuri lipsă vizual, marker obligatoriu care nu se vede).
- **Fluxul real multi-pas** — onboarding → date → facturi → declarație → depunere, ca un om, nu ca un unit test.
- **UX-ul erorii** — dacă mesajul apare *lângă câmpul* care trebuie și dacă blocajul global rămâne vizibil.
- **Comportamentul la încărcare** — stări de loading, ecrane goale, latență, date parțiale (E12).

**Utilizatorul de test = CONTABILUL.** Nu un scenariu de cod, ci un profesionist care deschide produsul și
verifică VIZUAL că fiecare firmă își poate ține evidența și depune ce datorează. Un pas „trece" doar dacă
contabilul ar semna declarația rezultată.

## Firme de test — derivate din MATRICEA DE OBLIGAȚII LEGALE (nu din ce implementează codul)

Principiul-cheie: **ce declarații datorează o firmă rezultă din LEGE (vectorul fiscal), nu din ce știe aplicația
să genereze.** Firmele de test se construiesc din combinații de regim — iar un gol apare când *legea cere X și
aplicația nu oferă/randează X*. Matricea (regim TVA × regim impozit × salariați × operațiuni × special):

| # | Arhetip | Vector fiscal | Declarații DATORATE prin lege (de verificat că apar și se generează) |
|---|---------|---------------|----------------------------------------------------------------------|
| F1 | Micro fără salariați, neplătitor TVA, doar intern | micro, neplătitor TVA, 0 salariați | D100 (impozit micro trim.), D101 (anual), bilanț |
| F2 | Micro cu salariați, plătitor TVA trimestrial | micro, TVA trim., salariați | D300 (trim.), D394 (trim.), D112 (lunar), D100, D205, bilanț |
| F3 | Profit real, TVA lunar, IC (livrări+achiziții) | profit, TVA lunar, IC | D300 (lunar), D394, D390 (IC), D101 (anual), D406 SAF-T (lunar), D112, bilanț |
| F4 | Profit real, TVA la încasare, taxare inversă | profit, TVA încasare, taxare inversă | D300 (regim încasare), D394 (V taxare inversă), D101, bilanț |
| F5 | IMCA (cifră afaceri > prag), profit | profit + IMCA art.18^1 | D101 cu impozit minim, D406 Assets anual, bilanț |
| F6 | Firmă cu CM (concedii medicale) toate codurile | salariați + CM (01/06/09/10/17/91/92…) | D112 cu indemnizații CM, stat de plată, recuperare FNUASS |
| F7 | Firmă în TRANZIȚIE de an / an parțial | înființare mid-an SAU micro→profit | D101 an parțial, bilanț, prima lună an nou (D406/D300/D112 dec.) |
| F8 | Firmă cu operațiuni SPECIALE (marjă / nerezidenți / forfetar) | regim special | *(PRODUS — vezi GARZI „PRODUS de abordat la final": marjă D300, D207 nerezidenți, forfetar D394)* |

> F8 e inclus intenționat ca **oglindă a golurilor de PRODUS**: la verificare, aceste cazuri trebuie să apară
> ca „nu e implementat încă", NU să producă tăcut o declarație greșită. Dacă F8 generează o declarație fără să
> semnaleze limita → e bug, nu gol.

## Cele 12 etape (E1–E12) — ce face contabilul și ce verifică VIZUAL

- **E1 — Onboarding & vector fiscal.** Creează cabinet + firmă, setează vectorul (regim TVA/impozit, salariați,
  IC). *Verifică:* vectorul DETERMINĂ corect setul de declarații datorate (F1–F7); proprietarul cabinetului poate
  imediat pregăti/valida/depune (fără deadlock de drepturi — vezi B3).
- **E2 — Date de bază.** Import + adăugare manuală: salariați, mijloace fixe, articole, asociați. *Verifică:*
  markerii obligatorii (`*`) apar unde backend-ul chiar cere; skip-urile la import sunt VIZIBILE (câte rânduri
  sărite — vezi D1a), nu tăcute; mesajele au diacritice și sunt explicite.
- **E3 — Facturare & operațiuni.** Emitere/primire facturi multi-cotă (21/11/scutit), taxare inversă, IC.
  *Verifică:* liniile reale apar (nu o linie sintetică), cotele perioadei (21/11 de la 08.2025), denumire
  beneficiar obligatorie.
- **E4 — TVA (D300 + D394).** Pe FIECARE regim: lunar (F3), trimestrial (F2), la încasare (F4). *Verifică:*
  perioada fiscală corectă, jurnalele de vânzări/cumpărări, linia scutită apare ca LS (vezi A6), reconcilierea
  D300↔D394 nu blochează fals.
- **E5 — Intracomunitar (D390).** Livrări + achiziții IC (F3). *Verifică:* VIES, sensul, că IC NU se dublează în
  D394; controlul încrucișat D390↔D300.
- **E6 — Salarizare (D112 + stat de plată).** F2, F6: CAS/CASS/impozit, CM cu toate codurile, CNP îngrijit unde
  D112 îl cere. *Verifică:* indemnizația CM, baza sub minim semnalată (suspect, nu tăcut), statul de plată.
- **E7 — Impozit (D100/D101).** Micro (F1/F2) vs profit (F3/F4) vs IMCA (F5); D101 anual. *Verifică:* impozitul
  minim IMCA, an parțial (F7), input amortizare fiscală (P11).
- **E8 — Informative (D205, D406 SAF-T).** D205 venituri; D406 lunar (SourceDocuments cu linii reale) + Assets
  anual (F5). *Verifică:* SourceDocuments emite linii reale (nu fallback sintetic); *metoda de amortizare afișată
  = metoda efectiv calculată* (vezi A5 — decizie deschisă: azi calc e liniar chiar dacă metoda zice degresiv).
- **E9 — Situații financiare.** Bilanț 2026; tranziția de an (F7): decembrie → ianuarie an nou. *Verifică:*
  coerența solduri, că D392 NU se depune, prima lună an nou.
- **E10 — Depunere & control.** Fluxul pregătire→validare→depunere (drepturi, four-eyes), DUK pe fiecare
  declarație, controlul încrucișat. *Verifică:* proprietarul depune fără blocaj (B3); un rol insuficient e refuzat
  cu mesaj clar; DUK „valid" pe artefactul real.
- **E11 — Erori & stări de blocare.** Perioadă închisă, date lipsă, permisiuni insuficiente, izolare tenant.
  *Verifică:* mesajul apare LÂNGĂ câmpul cauză (G10), blocajul global rămâne vizibil (nu fundătură), starea goală
  are cele 3 părți, izolarea ține (niciun 2xx cross-tenant).
- **E12 — Comportament la ÎNCĂRCARE.** Deschidere ecran, re-încărcare (F5), latență, date parțiale, revenire din
  eroare de rețea. *Verifică:* fără flash de ecran gol confundabil cu „nu ai date"; loading vizibil; o eroare la
  load NU lasă ecranul mut (mesaj, nu tăcere); reintrarea reface starea corect. *(Aceasta e etapa pe care NICIO
  gardă de sursă n-o poate acoperi — pur vizuală/temporală.)*

## Cum se citește un eșec
Un pas eșuează dacă: (a) o declarație DATORATĂ prin lege nu apare/nu se generează; (b) apare tăcut o declarație
GREȘITĂ (bază 0 / zero linii / total 0 fără motiv — EROARE până la proba contrarie); (c) un blocaj/eroare e tăcut
sau plasat greșit; (d) la încărcare ecranul minte (gol confundabil cu eroare). Fiecare eșec → divergență = bug
până la proba contrarie → vânătoare de clasă, nu petic pe instanță.
