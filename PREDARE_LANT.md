Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba) inainte de a incepe.

# PREDARE — Campania EXTINDEREA ACOPERIRII (05.08.2026)

## Stare la predare
- HEAD = origin/main = origin/backup/lant-20260805 = **ef9ba55** (sau commitul acestei predari, dupa push). Tree curat. Suita 1422 passed, verificator 0.
- NOU: GARZI.md are sectiunea **INVENTAR DESCHISE NON-CAMPANIE** (index canonic al tuturor deschiselor din afara celor 4 puncte;
  A actabil azi / B blocat extern / C decizie luata / D cere decizie produs). La revenire NU se recolecteaza - se citeste de acolo.
- Livrate in aceasta sesiune (peste 1a=4ad6f72): 1b TICHETE DE MASA (63b0865, CAS reconciliat/CASS afara),
  1c-PT PART-TIME suprataxare (133811e, CAS+CASS pe baza ridicata la max(brut, sm-facilitate)). Acoperire est ~40-55%.
- Ritual de pornire: agenda_drift curat, agenda arata campania GARDUL DE CONTINUT inchisa (6/6).
- REGULA NOUA de push (decizia c rasturnata 05.08, CLAUDE.md §2.3 pct.8): dupa fiecare executie, sub POARTA VERDE
  (pytest COLLECTED + verificator 0 + tree curat), push pe backup SI main FARA aprobare. Raportul §2.2 sect.11
  confirma HEAD=origin/main=backup pe acelasi commit.

## Campania: 4 puncte, in ordinea data de Costin (NU se schimba fara sa-i spui de ce)
Tiparul uniform (ca la cele 6 garduri de continut): recalcul INDEPENDENT (SQL+formula proprii), non-tautologie
probata pe AST (+ lant TRANZITIV la D112), mutatie obligatorie, HARD-BLOCK la divergenta care numeste ambele valori,
limita de acoperire DECLARATA. Orice valoare fiscala se verifica la sursa (common.cota / act) INAINTE de cod, cu comanda aratata.

### PUNCTUL 1 - D112 cazuri complexe (facilitati/CM/part-time/tichete). Se iau pe rand, ordinea prevalentei; dupa fiecare, cat a crescut acoperirea.
- **1a FACILITATE la minim, toata luna, full-time - LIVRAT (4ad6f72).** baza_contrib=sm-facilitate (S1 fac=300,
  S2 fac=200, verificat common.cota), CAS+CASS. Detectare stabilitate `_stabil_la_minim` (fara schimbare salariu in luna).
  Facilitatea PRORATATA (schimbare in luna) ramane sarita numit. Acoperire ~20-35% -> ~30-45% (est, nemasurat).
  ROTUNJIRE: generatorul tine cas la 2 zec (937.50); D112 EMITE intreg via _d112int (half-up->938); calea 2 confrunta
  valoarea EMISA: `got=_q(g[cas])`, nu int() trunchiere. (core/d112_reconciliere.py)
- **1b TICHETE DE MASA - LIVRAT (63b0865).** angajat peste minim cu tichete de masa: CAS reconciliat (tichetele nu ating baza CAS), CASS NUMIT-AFARA (CASS emis = salarial + cass_tichete, d112.py:239; recalc = tautologie + pontaj). Combo minim+tichete sarit. [istoric analiza:] Analiza facuta: tichetele de masa NU ating baza CAS (salarizare.py: b_imp=b+exces_vac,
  tichetele nu sunt in `b`) -> CAS = baza_contrib x cota_cas E RECONCILIABIL pentru angajatii cu tichete de masa.
  CASS insa creste cu cass_tichete (=nominal tichete x cota_cass) -> CASS pentru ei ramane de acoperit separat.
  Deci 1b poate reconcilia CAS pentru angajatii cu tichete de masa (fara alte beneficii), CASS ramane numit-afara.
  CAVEAT: tichetele cer pontaj CONFIRMAT (d112.pull ridica PerioadaNeconfirmata daca tichet_masa_valoare>0 si pontaj
  neconfirmat) -> fixtura de test trebuie sa confirme pontajul (mecanismul core.perioada.e_confirmat / tabela de
  confirmari - de gasit numele corect, NU e perioade_confirmate). Tichetele de VACANTA au excesul peste plafon anual
  (6 sm) care INTRA in baza (b_imp) -> pe alea CAS se schimba; acopera intai doar tichet de MASA (exces_vacanta=0).
- **1c PART-TIME - LIVRAT (133811e).** suprataxare CF art.146 alin.(5^6): D112 emite CAS/CASS pe baza ridicata
  la max(brut, sm-facilitate). Sub prag -> cas_min_pt/cass_min_pt (dif pe angajator B4_8D/B4_6D); peste prag -> pe brut.
  calea 2 recalculeaza prag=sm-facilitate INDEPENDENT (registru), full month fara CM -> fara proratare/pontaj. Confrunta EMISUL.
- **1c CM - BLOCAT pe DECIZIE DE PRODUS (tura 3, 05.08). PREMISA RETETEI DE MAI JOS E GRESITA - vezi GARZI 05.08 "DESCOPERIRE 1c-CM".**
    Verificat empiric pe generator: poarta cale2 primeste valorile PRE-emisie din pull (salary-only pe brut_lucrat
    proratat, g[cas]=1047.62), NU valoarea EMISA la ANAF (B4_8=4323=salary pe brut intreg + cm_cas). g[cas] NU e emisul
    -> a-l reconcilia = falsa incredere. In plus candidat bug: baza salariala CM difera intre fluturas (proratat) si
    declaratie (brut intreg). Decizie ceruta: (1) baza proratat vs brut intreg; (2) re-arhitectura poarta pe valori emise.
    URMATORUL actionabil fara decizie = Punctul 2. Reteta istorica de mai jos: cotele si rotunjirea (half-even per-cert) raman corecte.
- **[ISTORIC RETETA - premisa g[cas]=emis GRESITA] 1c CM - Sub-caz MARE (scopat 05.08).**
  Motivul opririi acestei sesiuni: buget de context + risc de DIVERGENTA FALSA din rotunjire (vezi mai jos), nu
  dificultate necunoscuta. Toata analiza de mai jos e verificata la sursa; sesiunea noua porneste direct pe cod.

  COTELE (taxe_cm, salarizare.py:562-597, verificat): CAS 25% UNIFORM pe TOATE codurile (CF art.139(1)(o)+140);
  CASS 10% DOAR cod in {01,07,10} (_CM_COD_CU_CASS, art.155(1)i / OUG 34/2024 art.17(2)); impozit 10%. NU importa/apela
  taxe_cm din cale2 (numele e in lista interzisa a test_non_tautologie) - aplica cotele DIRECT din common.cota.

  EMISUL unui angajat cu CM (d112.py, ramura `if cms and zile_cm>0`, ~l.190-210):
    cm_cas  = SUMA per certificat de _d112int((brut_ang+brut_fnuass) x cota_cas)    # 25% pe fiecare cert
    cm_cass = SUMA per certificat de _d112int((brut_ang+brut_fnuass) x cota_cass)   # DOAR cod in {01,07,10}
    cas = _d112int(bazac x cota_cas) + cm_cas ;  cass = _d112int(bazac x cota_cass) + cm_cass
  unde bazac = baza SALARIALA pe zile LUCRATE (nu pe brut intreg): brut_lucrat = brut x (nzl - zile_cm)/nzl,
  bazac = brut_lucrat - facilitate (facilitate 0 daca peste minim). zile_cm = SUMA(zile_ang+zile_fnuass) pe certificate.

  CE TREBUIE IN CALE2 (core/d112_reconciliere.py):
    - relaxeaza skip-ul cm_ids (azi l.~166 sare orice angajat cu CM) DOAR pentru cazul simplu: angajat peste minim,
      full-time, ne-scutit, fara tichete/alte beneficii, CM cod in {01,07,10} (ca sa fie si CASS reconciliabil).
    - capabilitate NOUA: nzl = zile lucratoare holiday-aware. Importa `core.scadente` (NU e in lista interzisa;
      interzise sunt doar salarizare/d112/salariu_istoric) - foloseste zile_lucratoare_luna(an,luna). Verifica pe AST
      ca lantul tranzitiv al scadente NU atinge salarizare/d112 (altfel gaseste alt drum).
    - citeste certificatele: SELECT cod, zile_ang, zile_fnuass, brut_ang, brut_fnuass FROM concedii_medicale
      WHERE salariat_id, an, luna (SQL propriu). exp_cas = _d112int(bazac x cota_cas) + SUMA _d112int((ba+bf) x cota_cas);
      la fel cass (doar cod cu CASS). Confrunta g[cas]/g[cass].

  CAVEAT CRITIC (de ce e MARE): rotunjirea. Generatorul aduna _d112int PER CERTIFICAT apoi sumeaza, si _d112int(bazac x cota)
  SEPARAT. Cale2 TREBUIE sa replice EXACT aceeasi ordine: round(salariu) + SUMA(round(cert_i)), NU round(salariu + total_cm).
  Un round(Σ) in loc de Σ(round) -> DIVERGENTA FALSA de 1-2 lei -> hard-block gresit. Testeaza cu 2 certificate ca sa
  prinzi ordinea. La fel, brut_lucrat proratat: verifica ca formula (nzl-zile_cm)/nzl coincide cu d112.pull:468 (brut_lucrat).

  LIMITA declarata: baza indemnizatiei (brut_ang/brut_fnuass) = INPUT PARTAJAT (§8) - ambele cai o citesc din
  concedii_medicale, o baza gresita acolo nu se prinde. media6 (_cm_media6) e doar pentru afisarea D17/D18, NU pentru
  contributii - cale2 nu are nevoie de ea. Coduri fara CASS (08/09/05 etc.) + defalcarea C2 = xfail-uri separate
  (test_datorie_cm05_subrows, test_datorie_cm_art_xi) - NU le atinge 1c-CM simplu. Verifica OUG 158/2005 la sursa DOAR
  daca extinzi dincolo de aplicarea cotei (procente/plafoane de indemnizatie) - pentru reconcilierea cotei nu e nevoie.

  FIXTURA: rand concedii_medicale (salariat_id, an, luna, cod='01', zile_ang, zile_fnuass, brut_ang, brut_fnuass) pe un
  salariat peste minim. Proba: g[cas] = round(bazac x 25%) + round((ba+bf) x 25%); mutatie pe brut_ang -> pica.

### PUNCTUL 2 - D101 profitul IMPOZABIL (ajustari fiscale). Anual, miza mare.
Azi calea 2 (core/d101_reconciliere.py) acopera doar profitul CONTABIL (P1/P2/P4/P5 din clasele 7/6). Ajustarile
(P6 deduceri, P7, P8 nedeductibile, P10 pierderi reportate) sunt in d101 INTRARI MANUALE ale contabilului (default 0,
d101.py:104-106 + genereaza) -> §8, calea 2 NU le poate recalcula din nimic (nu exista sursa in date). VERIFICA la
sursa (CF art.25 cheltuieli deductibile/nedeductibile, art.26 provizioane/rezerve) CE ajustari CALCULEAZA generatorul
din date (nu manual) - DOAR alea intra in calea 2. Ex. deja calculat de generator: rezerva legala deductibila
(d101.pull ia capital/rezerva_existenta/chelt_impozit din 1012/1061/691 - vezi d101.pull) -> P al rezervei se poate
reconcilia independent din aceleasi conturi. Daca restul ajustarilor raman manuale, SCRIE ca profitul impozabil
ramane pe golden+§8 si calea 2 acopera doar ajustarile COMPUTATE (rezerva legala etc.), nu "D101 impozabil acoperit".

### PUNCTUL 3 - amortizare MF neliniara (degresiva+accelerata). Subsistem propriu.
Temeiuri deja culese: CF art.28 alin.5-8 (eligibilitate pe clasa, coeficienti degresiv 1.5/2/2.5 dupa durata,
accelerata 50% an 1). xfail deja deschis: **test_datorie_mf_metode_amortizare** (ancora). Atinge MF (core/mijloace_fixe
sau d406_active.py) + D101 (amortizare fiscala P11) + D406 AssetTransactions. REGULI ANUALE (schema pe ani,
switch-to-liniar la degresiva cand rata liniara pe durata ramasa depaseste degresiva, prorata an partial). O amortizare
gresita = deducere fiscala eronata in D101 -> nu pe jumatate. Daca prea mare pt un punct: SUB-BLOCAJ motivat (4 elemente
CE/DE CE/CE TREBUIE/URMATOR) si mergi mai departe. VERIFICA art.28 la sursa inainte de cod.

### PUNCTUL 4 - tip_document 2-5 in D394 (borderouri/file carnet/contracte/alte). Ultimul - extindere de contract.
Azi calea auto D394 emite mereu tip_document=1 (facturi), CORECT pt ce se introduce azi. Devine necesar DOAR cand
exista o cale care creeaza operatiuni pe borderou/contract. VERIFICA daca exista o asemenea cale (grep pe
tip_document / borderou / operatiuni manuale d394). Daca NU exista -> spune-o si trateaz-o ca EXTINDERE AMANATA cu
trigger scris in GARZI (ex. "cand apare UI de operatiuni pe borderou"), NU ca datorie deschisa.

### NU e in campanie
Agricultorul forfetar - blocat pe absenta ghidajului ANAF, nu se poate debloca prin munca, ramane exceptie numita.

## Reguli de oprire (Costin)
Oprire DOAR pentru: poarta rosie, tree murdar, esec migrare pe tenant real, sau alegere care schimba ce declara
contabilul si NU rezulta din structura oficiala. Prea mare pt un punct -> sub-blocaj motivat, mergi mai departe.
Raport §2.2 per punct/sub-caz. RAPORT FINAL la sfarsit: acoperire per declaratie inainte/dupa, cifre unde exista,
"nemasurat" unde nu.

## De ce m-am oprit aici (sesiunea 05.08 tura 2)
Oprire §2.3 pct.6 (buget de context) dupa 1b + 1c-PT livrate, la granita curata de commit (133811e). Urmatorul (1c-CM)
e un sub-caz mare (media6 + cod-dependent CASS + fixtura certificat + §8 baza partajata) - a-l incepe risca tree murdar la
mijloc. Registrele (GARZI/DECIZII/TESTE/ISTORIC) la zi pentru 1b si 1c-PT. Firul in TESTE.md arata urmatorul = 1c-CM.
NU e oprire 'ca sa dirijeze Costin' - ordinea o da agenda; e strict buget de context. Analiza CM de mai sus (Punctul 1)
e suficienta ca sesiunea noua sa porneasca direct pe cod.

## [ISTORIC] De ce m-am oprit la 1a (tura 1)
Granita curata de commit (1a livrat+pins). Restul campaniei (1b/1c + P2/P3/P4, mai ales amortizarea neliniara)
e mai mult decat un context; §2.3 pct.6 - oprire la granita curata cu predare, nu start de sub-caz riscand tree murdar.
Registrele (GARZI/DECIZII/TESTE/ISTORIC) sunt la zi pentru 1a. Firul in TESTE.md "In lucru acum" arata urmatorul = 1b.
