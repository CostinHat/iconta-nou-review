# C-4. DATE CORECTE — documentele care produc EFECTIV rândurile declarațiilor (VALIDAT Costin 05.08.2026, cu completări)

**Scop:** pentru fiecare firmă din C-2, documentele CONCRETE (facturi, evenimente de salarizare, extrase, operațiuni)
care produc RÂNDURILE cerute de declarațiile ei — nu date generice. Cu valori **la LIMITĂ** (praguri CA, plafon CM,
salariu minim, luni parțiale, operațiuni cu semn contrar).
**Ce e acest document:** DESIGN-ul (trasabilitate document→rând + catalog de limite + sume exacte de coerență). **Seed-ul
reproductibil** (fișiere versionate din care popularea se reface identic — R2) = implementarea de după validare; se
livrează pe firmă/modul (anunț de împărțire mai jos).
**Perioada:** an fiscal 2026 complet + ianuarie 2027 (anuale + tranziția). Parametri 2026 confirmați în C-1.

---

## A. PRINCIPIUL DE TRASABILITATE (regula de aur a categoriei)
Fiecare RÂND cerut de o declarație trebuie să aibă un DOCUMENT-sursă care îl produce — altfel rândul e „inventat", nu
„derivat". Ex.: „D394 rând achiziții de la neplătitori" ⇒ trebuie o factură de la un furnizor neplătitor (T-3, M1→P1);
„D300 taxare inversă" ⇒ o operațiune de taxare inversă (T-6, construcții P2→S1); „D390 rând IC" ⇒ o achiziție
intracomunitară reală (P1 de la furnizor UE extern). Documentul JUSTIFICĂ rândul; verificarea = rândul emis se regăsește
în documentul-sursă.

**Calea de intrare (R4)** — fiecare tip de document marchează cum intră; fiecare cale distinctă exersată prin ECRAN cel
puțin o dată, volumul prin SEED:

| tip document | cale distinctă | ecran / seed |
|---|---|---|
| factură emisă B2B | e-Factura (SPV) + tastare directă | ecran ×1 fiecare, restul seed |
| factură primită | upload manual / OCR bon / import e-Factura | ecran ×1 fiecare, restul seed |
| extras bancar | import bancă (fișier) | ecran ×1, restul seed |
| stat de plată / pontaj | tastare directă (salarizare) | ecran (S4 obligatoriu), restul seed |
| certificat CM | tastare directă | ecran (S4) |
| operațiune specială (marjă, taxare inversă, storno) | tastare directă | ecran ×1 fiecare tip |

---

## B. CATALOGUL DE VALORI LA LIMITĂ (miza campaniei — „valori la LIMITĂ", R1)
Parametrii 2026 din C-1.

> **REGULA CELOR 3 CAZURI (decizia 3 Costin):** fiecare valoare de prag numeric primește **TREI** cazuri —
> **exact pe prag, prag−1, prag+1**. Motiv: o regulă scrisă cu `>` unde trebuia `>=` (sau invers) se vede DOAR exact pe
> prag; prag+1 trece în ambele variante, deci nu probează nimic. Se aplică la pragurile marcate **[×3]** mai jos:
> L1 (micro 100k), L2 (perioadă TVA), L5/L6 (salariu minim la 30.06/01.07), L7 (plafon CM 12 SM), L8 (exces vacanță 6 SM),
> L9 (bază minimă CASS part-time), L10 (achiziție IC 10k). Pragurile structurale (L11 lună parțială, L12 semne, L13 an
> parțial, L14 multi-certificat) și L3 (neenforced) / L4 (dispecer pe dată) NU au ±1 numeric.

| # | limită | valoare 2026 | firma/documentul care o atinge | ce bug prinde |
|---|---|---|---|---|
| L1 | **prag micro→profit** | 100.000 EUR CA | **T2** trece exact peste în trim. III | comutarea regimului la momentul corect (art.52) |
| L2 | **perioadă TVA (lunar/trim)** | 100.000 EUR CA an ant. | **M2/P2** sub prag (trim), **P1** peste (lunar) | alegerea perioadei fiscale (art.322) |
| L3 | **prag scutire TVA** | 395.000 lei | **M1** clar sub (neplătitor coerent) | NB: neenforced (GARZI D) — se fixează manual |
| L4 | **TVA la încasare** | 4,5M (ian–feb) → 5M (1 mar) | o firmă pe sistemul TVA la încasare, factură pe granița 28.02↔01.03 | dispecerul pe la_data (deja corect, common.py:349) |
| L5 | **salariu minim** | 4.050 (ian–iun) / 4.325 (iul–dec) | **S4**: salariat exact la minim în ambele semestre | schimbarea SM la 01.07 (D112 iul ≠ iun) |
| L6 | **facilitate salariu minim** | scădere 300→200; plafon 4.300→4.600 (01.07) | **S4**: salariat cu facilitate pe granița 30.06↔01.07 | baza_contrib = sm − facilitate, period-aware |
| L7 | **plafon CM 12 SM/lună** | 12 × SM lunar | **S4**: salariat cu venituri mari + CM | capare per-lună înainte de mediere (datorie xfail cm_plafon_12sm) |
| L8 | **plafon vacanță 6 SM/an** | 6 × SM | **S4**: tichete vacanță cu exces peste plafon | excesul INTRĂ în baza CAS/CASS (b_imp) |
| L9 | **part-time bază minimă** | max(brut, sm−facilitate) | **S4**: part-time sub prag | suprataxare art.146(5^6) — CAS/CASS pe bază ridicată |
| L10 | **achiziție IC decont special** | 10.000 EUR | **N1**: achiziție IC exact peste 10k | declanșare D301 (art.317) |
| L11 | **lună parțială de angajare** | angajare la mijloc de lună | **T1** (înființare 07.2026) + **S4** (un angajat la 15 ale lunii) | proratarea corectă pe zile lucrate |
| L12 | **operațiuni cu semn contrar** | storno / retur / ajustare TVA | **P1/S2**: o factură storno + un retur + o ajustare TVA | rândurile negative în D300/D394 (nu se pierd/nu se dublează) |
| L13 | **an fiscal parțial** | înființare la mijloc | **T1**: 6 luni de activitate | bilanț parțial, praguri recalculate proporțional |
| L14 | **multi-certificat CM/lună** | 2+ certificate aceeași lună | **S4**: un salariat cu 2 certificate CM în aceeași lună | Σ(round per certificat) vs round(Σ) — datoria „2b rotunjire" |

---

## C. COERENȚA R3 — SUME EXACTE (T-1…T-7 fixate; identice pe ambele laturi)
Fiecare tranzacție = aceeași sumă/CUI/dată la EMITENT și la PRIMITOR → D394 vânzări↔cumpărări + control_incrucisat se
verifică din DATE. TVA 21% (cotă 2026). (Sumele sunt schema de coerență; seed-ul le materializează identic.)

| # | emitent → primitor | dată | net (lei) | TVA | total | particularitate |
|---|---|---|---|---|---|---|
| T-1 | P1 → M2 | 2026-03-15 | 50.000 | 10.500 (21%) | 60.500 | marfă; TVA lunar(P1)↔trim(M2) pe aceeași factură |
| T-2 | P1 → P2 | 2026-04-10 | 80.000 | 16.800 (21%) | 96.800 | marfă profit↔profit |
| T-3 | M1 → P1 | 2026-02-20 | 8.000 | — (neplătitor) | 8.000 | furnizor NEPLĂTITOR → P1 fără drept de deducere; D394 „achiziție de la neplătitor" |
| T-4 | NR1 → P1 | 2026-05-05 | 30.000 | 6.300 (21%) | 36.300 | servicii IT intern (latura nerezident a NR1 = furnizor extern, pt D207) |
| T-5 | S3 → P1 | 2026-06-12 | 25.000 | forfetar 8% = 2.000 | 27.000 | agricultor forfetar (art.315^1); **e-Transport** la S3; D394 achiziție de la agricultor (exceptia numită) |
| T-6 | P2 → S1 | 2026-07-08 | 40.000 | **taxare inversă** (art.331) | 40.000 | construcții între plătitori → reverse charge; S1 autolichidează; rând D300 taxare inversă |
| T-7 | P1 → S4 | 2026-03-20 | 60.000 | 12.600 (21%) | 72.600 | materii prime/utilaje; S4 cumpărător cu TVA deductibilă |

IC (P1, N1) = de la furnizor UE EXTERN setului (VAT alt SM) → D390/D301 verificate structural, nu prin coerență A↔B.

---

## D. PER FIRMĂ — documentele definitorii → rândurile produse
(Compact: doar ce e DISTINCT/definitoriu pentru firmă. Volumul complet R1 = seed.)

- **M1** (micro neplătitor, 1 salariat): 12× stat salariu (1 angajat peste minim) → **D112** rânduri contribuții; facturi emise fără TVA (venit) → **D100** micro 1%; **D205** reținere salariu anual. Fără D300/D394.
- **M2** (micro plătitor TVA trim, 1 salariat): facturi emise/primite cu TVA 21/11 + T-1 (achiziție de la P1) → **D300(trim)** colectată/deductibilă + **D394(trim)**; 12× stat → **D112**; **D100** micro; **D205**.
- **P1** (profit, IC, TVA lunar): facturi emise (T-1,T-2,T-7) + primite (T-3 neplătitor, T-4, T-5 agricultor) + achiziție IC de la furnizor UE → **D300(lunar)** + **D390** (IC) + **D394(lunar)** cu rândurile speciale; mijloace fixe → amortizare → **D101** (P11) + rezervă legală (1061) + nedeductibile; 3× stat → **D112**; **D100** plăți anticipate; **D205**; bilanț. **Storno/retur/ajustare TVA (L12)** aici.
- **P2** (profit, TVA trim, fără IC): facturi cu TVA + T-2 (de la P1) + T-6 (către S1, taxare inversă) → **D300(trim)** + **D394(trim)** + rând taxare inversă; **D101**; 2× stat → **D112**; **D100**; **D205**; bilanț.
- **N1** (neplătitor, fără salariat, IC>10k): achiziție IC de la furnizor UE **exact peste 10.000 EUR (L10)** → **D301** (art.317) + **D100**. Fără D112/D300/D205.
- **S1** (marjă turism art.311): vânzări pachete pe **marjă** + achiziții (T-6 de la P2, taxare inversă) → **D300 rânduri pe marjă**; 2× stat → **D112**; **D101**; **D205**; bilanț.
- **S2** (marjă second-hand art.312): achiziții bunuri + vânzări pe **marjă per bun** (inclusiv un bun cu **marjă negativă → 0**) → **D300 pe marjă**; 1× stat → **D112**; **D101**; retur (L12); **D205**; bilanț.
- **S3** (agricultor forfetar art.315^1): vânzare T-5 către P1 cu **procent forfetar 8%** + **e-Transport** pe transport produse → **D100** (după caz), **D406**. Latura de cumpărător (P1) = achiziția de la agricultor în D394.
- **NR1** (profit, D207): plăți către **nerezident extern** (redevențe/servicii) cu reținere la sursă → **D207** (art.231, 28.02.2027); facturi interne (T-4 către P1) + TVA → **D300**/**D394**; **D101**; 2× stat → **D112**; **D205**; bilanț.
- **T1** (an parțial, micro, înființare 07.2026): activitate 6 luni; 1 angajat de la mijloc de lună **(L11)** → **D112** din luna angajării; **D100** micro; bilanț **parțial (L13)**; **D205**. TVA doar dacă se înregistrează.
- **T2** (micro→profit): CA care trece **exact peste 100.000 EUR (L1)** în trim. III → **D100** micro (trim I–III) apoi **D101** profit (de la trim. trecerii); facturi cu TVA → **D300**/**D394**; 1× stat → **D112**; **D205**; bilanț.
- **S4** (salarizare specială — miza D112): 8–12 salariați cu matricea completă:
  - CM **toate codurile** (01/07/08/09/10/15/17/91/92); un salariat cu **2 certificate/lună (L14)**; baza CM pe **zile lucrate**.
  - salariat **la minim** în ambele semestre **(L5)**; cu **facilitate pe granița 30.06↔01.07 (L6)**.
  - **part-time sub prag (L9)**; salariat cu venituri mari + CM **(plafon 12 SM, L7)**.
  - **tichete** masă (45 lei), vacanță cu **exces peste 6 SM (L8)**, culturale, creșă; **cnp_ingrijit** pentru cod 09/91/92/17.
  - un angajat **la mijloc de lună (L11)**.
  → **D112** lunar cu toate rândurile; **D300**/**D394** (activitate comercială); **D101**; **D205**; bilanț.

---

## E. PERIOADA + TRANZIȚIA DE AN (ianuarie 2027)
- 2026 complet: 12 luni D112/D300(după perioadă)/D406; D394 pe perioada D300; D390 lunile cu IC.
- **Ianuarie 2027** (tranziția): D406 luna 12/2026 → 31.01; D300/D112 luna 12 → 25.01; D394 → 30.01. Anuale pentru 2026:
  D205+D207 → 28.02.2027; D101 → 25.06.2027; bilanț → ~30.05.2027. **D392 NU se depune** (suspendat până 31.12.2026, C-1).
- Boundary de an: salariul minim (4.325 în dec.2026) vs eventuala schimbare 2027; cota micro 1% neschimbată; verificare că
  registrul de cote NU întoarce tacit valori 2026 pentru date din 2027 (gardul de expirare cote, common.py).

---

## F. ÎMPĂRȚIREA SEED-ULUI + DECIZII

**Împărțirea seed-ului în 3 tranșe — ORDINE VALIDATĂ (decizia 2 Costin — S4 PRIMA):**
1. **Tranșa 1 — SALARIZARE S4:** S4 integral (8–12 salariați, matricea CM toate codurile / tichete / facilitate /
   part-time / luni parțiale / multi-certificat, cu regula celor 3 cazuri pe praguri) + salariile simple ale celorlalte
   firme → **D112/D205**. Motiv ordine: S4 e zona cu tot istoricul de bug-uri; dacă bugetul se termină sau ceva se rupe,
   S4 e deja în bază, nu ultima.
2. **Tranșa 2 — COERENȚĂ + TVA:** cele 12 firme provizionate + T-1…T-7 (facturi coerente) + restul facturilor per firmă →
   D300/D394/D390/D301.
3. **Tranșa 3 — ANUALE + TRANZIȚIA:** amortizare/rezervă/nedeductibile → D101; bilanț; ianuarie 2027 (tranziția de an);
   operațiunile cu semn contrar (storno/retur/ajustare, L12); D207.

Fiecare tranșă = fișiere versionate (R2), poartă verde, DUK valid pe declarațiile atinse, raport de acoperire per firmă.

**Decizii Costin — VALIDATE 05.08.2026:**
1. **Sumele de coerență** T-1…T-7 — ordine de mărime OK, fără valori fixe.
2. **Ordinea tranșelor** — SCHIMBATĂ: (1) salarizare S4, (2) coerență+TVA, (3) anuale+tranziția (S4 prima).
3. **Praguri — regula celor 3 cazuri** (exact / prag−1 / prag+1) la L1/L2/L5/L6/L7/L8/L9/L10 (secțiunea B). NU doar prag+1.
4. **Volum** — mijlocul intervalelor R1 (fără cifre exacte impuse).

**Limite declarate:** IC fără coerență A↔B (furnizor extern). Achiziția de la agricultorul forfetar (T-5) atinge exceptia
numită (D394 orfan) — se tratează ca atare. CNP-urile (salariați S4 + persoane conturi) = generate la seed cu caveatul de
non-verificabilitate. Pragul TVA 395k neenforced (fixare manuală platitor_tva).

**C-4 VALIDAT ca design. Următorul: SEED tranșa 1 (salarizare S4), sub poartă verde + DUK.**
