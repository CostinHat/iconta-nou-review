# CATALOG_INVALIDITATE — datele care invalideaza fiecare declaratie (LANT legislatie TURA 2/4)

Construit tura 28 (TURA 2/4). Pentru FIECARE declaratie: tipurile de date care o invalideaza, ce incalca,
sursa, si mesajul CURENT catre utilizator. Metoda: 10 audituri paralele, fiecare tip **construit** pe date
POPULATE (injectii ROLLBACK) + rulat prin `genereaza` + DUKIntegrator; XML corupt trimis direct la DUK pentru
regulile pe care generatorul nu le poate produce (dovada ca gardul e load-bearing).

Legenda mesaj CURENT:
- **(a)** generatorul RIDICA ValueError (hard-block) - user nu primeste XML.
- **(b)** AVERTISMENT non-blocant (res.avertismente) - se genereaza oricum.
- **(c)** generatorul emite TACIT -> DUK respinge (E:) - userul afla DOAR daca ruleaza DUK.
- **(d)** TACIT complet - generatorul emite, DUK ACCEPTA date gresite/garbage - nimeni nu prinde. Cel mai grav.

Categorii: mandatory-missing / wrong-type / length / out-of-nomenclator(enum) / bad-format / checksum /
cross-field / total-mismatch / zero-nil / aggregation-loss.

═══════════════════════════════════════════════════════════════════════════════════════
## TEME TRANSVERSALE (se repara o data, acopera multe declaratii) - TINTELE TUREI 3

**T1. Checksum CUI/CNP NICIODATA pre-validat de app (9/9 declaratii).** erori_generare verifica doar non-gol.
Un CUI/CNP cu cifra de control gresita / lungime / non-numeric e emis TACIT; doar DUK il prinde (c). Exista deja
un validator (asociati_import_api.valideaza_cnp) folosit doar la import asociati, niciodata pe declaratii.
Afectat: D100(#7/#11/#19), D101(6.12), D112(3.1-3.4 CNP angajat), D205(c1/c2), D300(OE-3), D301(cif), D394(G-c1
cuiP R218.2), D406(E1/E16/E3), D710(D1/D2/I2). FIX: un gard comun valideaza_cui/valideaza_cnp la erori_generare.

**T2. `valideaza(res)` = COD MORT.** D300, D301, D406 au un `valideaza()` in modul (tip_decont↔luna, marja,
AccountType, nr_doc/tip gol) dar `genereaza()` cheama doar `erori_generare(prof)`, NU `valideaza(res)`. Verificari
prietenoase exista dar nu sunt invocate -> user primeste eroarea DUK bruta. FIX: apeleaza valideaza(res) in genereaza.

**T3. Coercitie TACITA enum-necunoscut -> default (date gresite trec validarea) - clasa (d).** D406 UOM
necunoscut->H87(bucata), PaymentMethod->03, cota->TaxCode 310312; D301 tip->1, tip_valuta->EUR; D394 CUI garbage
cu litere -> partener strain tip 3/4. XML DUK-valid dar raporteaza date GRESITE la ANAF. Doar avertisment (D406) sau
nimic (D301/D394). FIX: refuz/avertisment vizibil pe coercitia unei valori necunoscute, nu inlocuire tacuta.

**T4. AVERTIZEAZA-dar-emite-INVALID.** D394 op1 C/V fara op11 (#39-41): app avertizeaza dar scrie XML pe care DUK
il respinge (R233.5). Avertismentul nu blocheaza. FIX: blocheaza sau exclude operatiunea, nu doar avertiza.

**T5. Cale MANUALA/IMPORT ocoleste gardurile.** D205 beneficiari manuali sar reconcilierea (imp1 gresit trece de
tot); D301 import scrie nr_doc/val/tva fara validarea din adauga; D710 obligatii manuale. FIX: aceleasi garduri pe
calea manuala/import ca pe cea automata.

**T6. Passthrough NETRUNCHIAT -> overflow lungime (c/d).** D301 nr_doc >C(20) fara gard NICAIERI (leak pur, DUK nu
impune lungimea = d); D112 serie/numar/diagnostic (D_1/D_2/D_23) netrunchiate -> XSD maxLength (c). (nume/den/adresa
SUNT trunchiate tacit prin text_anaf - pierdere de date silentioasa = d minor.) FIX: trunchiere/refuz pe passthrough.

**T7. SEMANTIC gresit-dar-consistent -> DUK NU poate prinde (tinta TURA 4).** D205 imp1≠rate×baza1 (d1), D301 RON cu
curs≠1 (baza supraevaluata), D100/toate suma din agregare mis-contabilizata, D710 suma_ded aruncat tacit, CUI cu
proprietar gresit. Validatorul verifica doar coerenta interna, nu corectitudinea vs contabilitate. -> RECONCILIERE.

**T8. Gap-uri de NON-IMPUNERE DUK (d - chiar si DUK rateaza).** D300 V19/V20 R25=R12 NEIMPUS (R12 fara R25 -> TVA
colectata supra-declarata, net≠0, trece); D101 d_reg=1 fara Stat_rezid / d_succ=1 fara cifS neimpuse; D101 cod_bug
orice 10-char acceptat; D205 sect_II duplicat same tip / all-zero benef acceptate.

**T9. EXCEPTII BRUTE in loc de mesaj prietenos.** D710 suma "abc"->decimal.InvalidOperation, lipsa cod_oblig->
KeyError (necapturate, criptice). FIX: wrap in ValueError cu mesaj clar.

**T10. UNREACHABLE = completitudine de FEATURE (nu invaliditate de date, dar flagat).** rectificativa (d_rec/d_recN),
anulare, succesor (cifS), grup fiscal (D101 P54-P56), exercitiu modificat, D406 Payments (plati mereu []), CNP-03
pe factura (D406 E3/E4), D301 d_rec. Nu se pot depune azi.

**T11. VALIDATOR IN URMA FORMEI (infra, flag Costin).** D112_209 (Apr 2026) e anterior formei 605/2026 (iulie 2026);
campurile noi (D_14a/D_15a/E3_97...) sunt emise dar NEVERIFICATE de validatorul instalat -> orice invaliditate in
ele trece azi. De actualizat DUK-ul.

═══════════════════════════════════════════════════════════════════════════════════════
## PER DECLARATIE (rezumat categorii + gap-urile (c)/(d) = tintele concrete)

### D100 (obligatii buget stat) - 31 tipuri; ~50 reguli DUK v9, ~20 accesibile (toate catalogate)
Gardat (a): CUI/den/adresa gol, obligatie zero (refuz "nu se depune pe zero"), cota↔121 bidirectional, luna trim,
scadenta cod-specifica (R15.1 micro trim IV 25.06.an+1), cod_oblig/cod_bugetar nomenclator, totalPlata_A (dublu gard).
GAP (c): #7/#11/#19 CUI non-numeric/lungime/checksum -> DUK "CUI/CNP invalid" (T1).
GAP (d): #12 nume/adresa >200/1000 trunchiate tacit; **#31 aggregation-loss** - suma_dat gresit din venituri
mis-contabilizate (cont≠70x / nevalidat / necontabilizat) -> emis + DUK-valid (T7, tinta TURA 4).

### D101 (impozit profit) - ~50 tipuri, 9 categorii; 26 reguli DUK v8 live
Gardat (a): identitate, cota↔121, reconciliere (contabil), totalPlata_A artefact.
GAP (c): manual P-uri (V2-V7 breaches, P36<0, P8<Σsub), cod_obligatie/caen out-of-nomenclator, cif bad-checksum -> DUK.
GAP (d): nil pt firma activa; CUI proprietar gresit; **cod_bug "5503XXXXXX" NEVALIDAT de DUK**; d_reg/d_succ
conditionale neimpuse (T8); scadenta LL+3 vs LL+6 OUG 8/2026 (decizie produs). UNREACHABLE: rectificativa/succesor/
grup fiscal (P54-56) neimplementate (T10).

### D112 (contributii + evidenta nominala) - 127 atribute required XSD; ~15 passthrough accesibile (toate catalogate); 91 V-reguli
Gardat (a): CUI/den firma, CM D_1/D_2/D_5/D_6/D_7 obligatorii (refuz), D_8/D_8a CNP ingrijit cod 09/17.
GAP (c): **CNP angajat** lungime/format/leading-zero/alpha (XSD pattern) + bad-checksum (DUK); nume angajat gol
(DUK "vid nepermis"); data_angajare NULL (XSD); caen '9999' (XSD enum); cod boala '99' (XSD D_9 enum); serie/numar/
diagnostic D_1/D_2/D_23 overflow (XSD maxLength - NETRUNCHIATE, T6); CM media=0 & brut=0 & zile>0 (DUK V52).
GAP (d): **judet_casa bogus -> casaSn "_B" (casa de sanatate GRESITA mascata)**; loc_prescriere 0->1; rand COTE
gresit -> tacit in toate bazele (T7). FLAG T11: validator anterior formei 605/2026.

### D205 (impozit retinut sursa/dividende) - ~19 reguli DUK + clase schema
Gardat (a): CUI/den/adresa, cifR/den1 obligatorii (refuz), nerezident dividende refuzat (R32 -> D207),
reconciliere 457 (cale auto).
GAP (c): CNP/NIF checksum (skip intentionat) -> DUK R29; CUI platitor checksum -> DUK; **asociat CNP duplicat ->
(tip_venit1+cifR) duplicat, reconcilierea colapseaza pe cheia cif** -> DUK R41b; beneficiari manuali sar reconcilierea
-> baza/imp negative -> DUK R44/R45.
GAP (d): **imp1 ≠ rate×baza1 pe beneficiar MANUAL trece de generator SI DUK** (reconciliere ocolita, DUK verifica
doar Timp=Σimp1) - declaratie material gresita acceptata cap-la-cap (T7, cel mai grav D205).

### D300 (decont TVA) - ~48 tipuri, 12 categorii; D300_27
Gardat (a): banca/cont/caen/cui/nume/tip_decont, chei manual necunoscute/computed (anti-drop), dubla-numarare
taxare inversa, perioada.
Avertisment (b): 19%/5%/9% fara rand DUK-valid (cuantificat), livrari 0% neclasificate (R14/R15), achizitii 0% -> R26,
taxare inversa primita -> R12/R25, forfait agricol orphan-TVA, decont pe zero cu facturi.
GAP (c): **valideaza() COD MORT (T2)** - tip_decont A/S↔luna -> DUK R18 brut in loc de mesaj; caen/cui/pro_rata
out-of-range; CR-1..4 oglinzi intracom one-sided (manual) -> DUK V7-V18.
GAP (d): **CR-5 R12 fara oglinda R25 trece de modul SI de DUK instalat (V19/V20 NEIMPUS)** -> TVA colectata
supra-declarata, net≠0 (T8). (c-soft) marja ±1% pe rand manual -> DUK atentionare (uploadabil), marja check = cod mort.

### D301 (decont special TVA) - ~11 clase DUK live; D301_9
Gardat (a): cif/den/banca/cont, curs≤0 (calc_baza), luna 1..12.
GAP (c): **valideaza() COD MORT (T2)** - nr_doc/data_doc gol, tip/valuta out-of-nomenclator -> DUK; cif checksum +
supra-lungime C(13); **an<2013 negardat** (gardeaza doar luna); data_doc format/calendar via import.
GAP (d): **nr_doc >C(20) fara gard NICAIERI (leak pur, T6)**; val_valuta/tva negative din import; **RON cu curs≠1 ->
baza supraevaluata 5x**; divergenta baza-vs-val_valuta la rotunjire (>2 zecimale); tip=0->sectiune 1; declarant
"ADMINISTRATOR" fabricat; **pers_inreg misclasificat** (art.317 fara flag emite "1"); d_rec mereu 0 (rectificativa).

### D390 (recapitulativ VIES) - ~35 tipuri, 11 categorii; D390_11 v2, reguli R13-R25.1
Gardat (a): CUI/den firma, tip manual necunoscut/directie ilegala, zero-refuse ("nu se depune pe zero").
GAP (c/d) FLAGSHIP: **codO EU VAT cu checksum INVALID emis fara NICIO diagnoza per-partener -> DUK R24.1**.
Avertismentul "X facturi fara CUI UE valid" e filtru SINTACTIC de prefix, NU verifica checksum-ul VIES (biblioteca
vatalgo e IN jar, app nu-l reimplementeaza) (T1).
GAP (d): tara mistypata (CR pt HR, GR pt EL) -> partenerul DISPARE intr-un count agregat generic, fara identitate;
**valideaza() COD MORT (T2)** - tara-nomenclator/codO-missing-L,T,P,R/totalPlata_A coerenta calculate dar niciodata
aratate; trunchieri tacute denO>200 si **codO>12 (CORUPE numarul de TVA!)**, telefon/cui NEclampate -> DUK.
UNREACHABLE: sectiunea de corectie <cos> neemisa -> R24.2-4/R25.1 + rectificativa D390 = feature intreg lipsa (T10).
Discrepanta: DUK instalat cere codO pt L,T,P (nu R); struct 2020 + app cer L,T,P,R.

### D394 (livrari/achizitii nationale) - ~45 tipuri, ~40 reguli, 8 categorii; D394_31 v5, ~90+ reguli reale
Gardat (a): tip manual necunoscut, cota pozitiva-necunoscuta (reconciliere hard-block).
Avertisment (b): cota negativa exclusa, N fara subcod exclus, cereale fara NC.
GAP (d): **G-d1 partener CUI cu litere -> misclasificat partener strain tip 3/4 -> LS cota0 -> DUK trece** (T3, cel
mai grav D394); G-d2 nrFacturi magnitude neverificat.
GAP (c): **G-c1 cuiP checksum fara pre-check -> DUK R218.2** (T1); own cui/caen present-but-invalid.
GAP (b+c): **G-bc1 op1 C/V fara op11 -> avertizeaza dar emite XML DUK-invalid R233.5 (T4)**; G-bc2 N/PF op11 cu CUI
de firma -> R233.4. ASIMETRIE G-x1: cota 7% hard-block vs cota -5 drop tacit (decizie produs).

### D406 (SAF-T) - Header/MasterFiles/GL/SourceDocuments; D406_35; XSD deliberat larg (DUK = autoritatea)
Gardat (a): totaluri antet↔linii (reconciliere), dubla-inregistrare (Σdebit=Σcredit), partener lipsa, CUI firma,
luna; date DB NOT-NULL.
GAP (c): **partener CUI checksum nepre-verificat -> DUK "format invalid" (T1)**; **E3/E4 CNP in tert_cui -> emis
00+CNP, DUK respinge INDIFERENT de validitate (tipul corect 03+CNP, cale inexistenta)**; country prefix ZZ.
GAP (d): **coercitie tacita (T3): UOM necunoscut->H87(bucata), PaymentMethod->03, cota->TaxCode 310312** - DUK-valid
dar UM/date GRESITE la ANAF (doar avertisment). valideaza(res) AccountType = cod mort (T2).
NESONDAT (hardcodat, TURA 3 injecteaza direct): Payments sub-tree (plati mereu []), InvoiceType out-of-enum, TaxCode
out-of-nomenclator, BaseRate, HeaderComment>2, AccountID-in-plan, Address Country.

### D710 (rectificativa D100) - suprafata = INPUT MANUAL (obligatii) + identitate profil; D710_56
Gardat (a): identitate, cod_oblig lipsa->KeyError(brut T9), suma "abc"->decimal(brut T9), cota↔121, scadenta format,
luna, chei manual necunoscute.
GAP (c): cod_oblig/cod_bugetar/cota/scadenta MANUALE acceptate raw -> DUK; **C5 cod 131/132 -> CRASH validator NPE**
(lipsa Data_I); CUI niciodata validat (D1/D2/I2, T1); scadenta calendar-invalid; B4 sume negative.
GAP (d): G2 rectificare nula (i==c) acceptata; **J1 suma_ded aruncat TACIT -> declaratie valid-dar-aritmetic-gresita**
(T7, LIMITA documentata).

═══════════════════════════════════════════════════════════════════════════════════════
## STARE PENTRU TURA 3 (mesajul catre utilizator) si TURA 4 (reconcilierea)
- TURA 3 tinteste (c)+(b-invalid): promoveaza in avertisment/refuz PRE-DUK cu motiv exact. Prioritar T1 (checksum
  CUI/CNP comun), T2 (valideaza() mort), T3 (coercitie tacuta), T4 (avertizeaza-dar-emite), T6 (lungimi passthrough),
  T9 (exceptii brute).
- TURA 4 tinteste (d)-semantic: T7 (imp1/curs/agregare/suma_ded/proprietar) + T8 (gap-uri non-impunere DUK) - se
  prind DOAR prin reconciliere sursa-vs-declaratie, nu prin DUK.
- Decizii produs: D101 scadenta LL+3-vs-LL+6, D394 asimetrie cota, T10 completitudine feature, T11 actualizare DUK.
