# MARKETING — Strategia de achiziție clienți iConta.eu

*Document normativ · stabilit 20.07.2026 · în git (editabil prin SSH). Strategie, nu decizie tehnică
(aceea → DECIZII.md). Afirmațiile publice se ancorează în inventarul real FUNCTIONALITATI.csv.*

---

## BRAND
- Numele se scrie PESTE TOT ca **"iConta.eu"** (i mic, C mare, .eu inclus în nume). Motiv: există alte
  "iConta" — .eu ne desprinde clar. Regulă strictă, fără excepții în orice material public.

## POZIȚIONARE (verificată contra pieței, iulie 2026)
- NU vindem pe "gratuit" — SAGA e gratuit permanent, pierdem lupta asta frontal.
- Vindem pe ce SAGA/concurența NU au: cloud modern (vs SAGA desktop/FoxPro), **CONTROL FISCAL AUTOMAT**
  (control încrucișat D390/D112/D300/cotă TVA + semafor — nimeni nu-l are), fondator prezent, 12 luni
  gratuit (vs SmartBill 3 luni).
- Diferențiator de vârf în mesaj = **"control fiscal automat"**, NU "contabilitate completă" (aia e
  masă/paritate).
- Concurență: SAGA (gratuit dar desktop/vechi, backup+IT pe client, fără control automat), SmartBill
  (modern dar gratuit doar 3 luni), Oblio/FGO (facturare limitată).
- Ton contra SAGA: respectuos, NU agresiv (contabilii respectă SAGA). Prezentăm diferența ca alegere de
  model, lăsăm contabilul să tragă concluzia pe costurile ascunse SAGA (legare de birou, backup manual,
  IT, module plătite).

## AFIRMAȚII PERMISE (din inventar FUNCTIONALITATI.csv, onest)
- "Software PENTRU contabilitate completă" (NU "oferim contabilitate" — zid legal CECCAR: iConta.eu e
  instrument, contabilul prestează).
- "Generează și validează toate declarațiile (D100-D406) pe validatorul oficial ANAF (DUK)".
- "Control fiscal automat: control încrucișat + semafor + alerte roșii".
- "Depunerea o faci din SPV cu XML verificat de iConta.eu (ANAF nu oferă depunere prin API niciunui soft
  cloud)".

## AFIRMAȚII INTERZISE (overclaim/fals)
- "Depune cu un click la ANAF" — FALS (F127 blocat).
- "e-Factura funcțională live end-to-end" — PREMATUR (round-trip neprobat pe CIF real cu drept SPV). Doar
  după probă live.
- "100% fără alt tool" — FALS (portal SPV necesar).

## OFERTĂ: Program Cabinet Fondator
- ȚINTĂ: contabili care ÎȘI PORNESC cabinetul (nelegați încă de SAGA — tablă goală, zero zid de
  comoditate). NU cabinete SAGA existente (greu de mutat, se izbesc de comoditate + percepția "vine să-mi
  vândă").
- CE OFERIM: platforma iConta.eu completă (cabinet, nu contul gratuit F160 limitat), gratuit 12 luni,
  limită 3 firme/cabinet.
- Motiv limită 3 firme (nu 5-7): acoperă startul cabinetului, dar creează conversația de creștere/plată
  natural când cabinetul depășește 3 firme. Cifră de testat cu primii contabili, nu literă de lege.
- Numărul de cabinete în program: 5-7 (destui pentru feedback, dar puțini ca să-i ajut personal pe
  fiecare).
- ÎN SCHIMB: feedback (primii utilizatori reali → găsesc bug-urile) + testimonial/referință dacă sunt
  mulțumiți. Relație, nu contract.
- DIFERENȚIATOR cheie: gratuit + FONDATORUL personal ajută la onboarding și construiește ce le lipsește —
  niciun competitor mare nu oferă atenția asta.

## MOTOR DE CREȘTERE (flywheel — vânzare directă + vizibilitate, se hrănesc reciproc)
1. Vânzare directă → primii 5-7 contabili care pornesc (rapid, feedback).
2. Ei folosesc, se mulțumesc → word-of-mouth către colegi (inclusiv cabinete SAGA). Recomandarea de la un
   peer sparge zidul pe care vânzarea directă nu-l poate sparge (experiență trăită, nu pitch).
3. Vizibilitate (pagini SEO) prinde curioșii care caută "iConta.eu" după ce aud recomandarea + validează
   că produsul e real. Fără vizibilitate, word-of-mouth-ul se stinge când colegul caută și nu găsește
   nimic.
4. Fiecare client nou → mai mult word-of-mouth → mai multă căutare → paginile lucrează mai tare. Volant.

## SEO — pagini per funcționalitate
- Fiecare funcționalitate LIVE client-facing → o pagină SEO reală (NU descriere CSV copiată — thin content
  = penalizare Google). Poveste (durere concretă) + temei legal verificat la sursă + procedură manuală
  (80% valoare) + iConta.eu ca automatizare (20%).
- Țintă: long-tail de nișă unde iConta.eu e SINGURUL (ex. "control încrucișat D390 decont TVA") —
  concurență ~zero, ranking rapid, intenție de cumpărare mare. NU termeni generali ("software
  contabilitate") unde pierdem contra giganților.
- Date fictive plauzibile în exemple (SC Exemplu SRL, sume rotunde credibile), NU date de test
  (tenant_002). Datele reale de clienți NU se pot publica NICIODATĂ (GDPR/secret fiscal) — deci fictive
  curate, permanent.
- Design: semaforul (verde/galben/roșu) = element-semnătură (e produsul). Ton cald + riguros fiscal (art.
  de lege citat corect).
- STARE (26.07.2026): NELIVRAT — plan, nu realitate. La sursă NU există ruta /ghid/{slug}, niciun șablon și nicio pagină; infrastructura nu e începută. Prima pagină-șablon planificată: control-incrucisat-d390 (temeiul legal — articolul din Codul fiscal — se citează și se verifică la sursă când se scrie pagina, nu se presupune). URL pattern intenționat: iconta.eu/ghid/{slug}.
- Fiecare afirmație din pagini DOAR din lista PERMISE, niciodată din INTERZISE.
