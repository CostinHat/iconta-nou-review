# BRIEF_CODE_PACHET_18IUL — 4 teme independente, executie in ordine

Costin a aprobat un pachet mai mare. Executa temele IN ORDINE, cap-coada, raportand
scurt dupa fiecare (commit + rezultat). Nu astepta confirmare intre teme - doar la PORTI.

Autonomie pe executie. PORTI unde STOP si intrebi (comune tuturor):
- schema noua sau modificare de cod LIVE care schimba comportament existent
- regula Design System inexistenta pentru ceva vizual nou
- Storage Box neprovizionat (Tema 1)
- orice ambiguitate fiscala/legala neconfirmabila la sursa
Regula de aur peste tot: verifica la sursa inainte de a declara "absent/de construit";
verificare functionala reala, nu py_compile; registrul (FUNCTIONALITATI.csv) se actualizeaza
in ACELASI commit; decizii in DECIZII.md; nu construi paralel cu ce exista.

================================================================================
TEMA 0 (intai, fara cod) — harta de prioritati in DECIZII.md
================================================================================
Scrie in DECIZII.md:

URGENT (se poate face acum): backup off-site (F170) - Tema 1 de mai jos.
BLOCAT PE ANAF: cluster SPV (F121 e-Transport, F126 e-Factura, F160 e-Factura gratuit =
pragul pozitionarii contra SmartBill). Se deblocheaza la confirmarea OAuth. Notat.
LA SEMNAL (nu preventiv): integrari (PSD2 F130, plati reale F123, borderouri F132),
concurenta (tichete F133, COR F137, centre cost F143, cloud F148), F161 (primul client
gratuit care migreaza), F307 (primul caz anulare cod TVA). La cerere reala, nu inainte.
CERE OM: SAGA import real, audit vizual ~20 ecrane, pilot Daniela.
Miezul e complet (contabilitate, salarizare, 9/9 declaratii LIVE+DUK, stoc, facturare,
control fiscal, export SAGA). Ce ramane = expansiune la cerere, nu goluri.
Comit.

================================================================================
TEMA 1 (URGENTA) — backup off-site pe Hetzner Storage Box
================================================================================
Context (verificat 18.07): backup local LIVE (iconta-backup.timer, pg_dump zilnic 03:00,
retentie 7 zile), restaurare CONFIRMATA. Lipseste copia off-site. /var/backups e pe acelasi
disc ca baza -> nu supravietuieste mortii discului. Decis: Hetzner Storage Box.

FAZA 0: verifica daca Storage Box e provizionat (credentiale SFTP/rsync in ~/.iconta, /etc,
crontab?). Citeste /usr/local/bin/iconta-backup.sh complet.
- Daca Storage Box NU e provizionat -> STOP, raporteaza: Costin il creeaza din panoul
  Hetzner (nu se poate din SSH). NU inventa credentiale.

FAZA 1 (daca e provizionat): extinde iconta-backup.sh (nu script paralel). Dupa pg_dump
local reusit, sincronizeaza catre Storage Box prin rsync-over-SSH cu cheie dedicata (nu
parola). Retentie off-site mai lunga (30 zile) decat local (7). FAIL-SAFE: daca off-site
esueaza, backup-ul LOCAL tot reuseste; esecul off-site se logheaza separat. Dupa upload,
confirma remote (stat/ls prin sftp) + logheaza dimensiunea.

FAZA 2: daca off-site esueaza N zile la rand -> email (refoloseste Brevo din monitor_fiscal.py).
Backup off-site care esueaza tacit e mai rau decat lipsa lui.

TEST real: ruleaza scriptul manual, confirma dump-ul pe Storage Box (ls remote + dimensiune).
Simuleaza esec off-site (cheie gresita temporar): confirma ca LOCAL tot reuseste + logheaza.
NU sterge backup-uri existente. Backup local = SACRU.
La final: F170 -> LIVE (off-site), DECIZII.md actualizat, comit.

================================================================================
TEMA 2 (igiena) — iteratia mig-gol -> arataMesaj (~50 mesaje de eroare in catch)
================================================================================
Context: la migrarea starilor goale (v2.13, .stare-goala) au ramas ~50 aparitii mig-gol
care NU sunt stari goale, ci mesaje de EROARE/validare in blocuri catch. Acelea apartin
lui arataMesaj (feedback dupa actiune), nu .stare-goala (continut de ecran). Sunt tema
separata, decisa 17.07.

- grep toate `mig-gol` ramase in .js. Fiecare din catch/validare/loading -> converteste la
  arataMesaj(zona, mesaj, "eroare") (sau tipul corect: eroare/avert/info dupa context).
- ATENTIE: nu converti la arataMesaj ceva ce e de fapt stare goala (lista 0 randuri) - ala
  e .stare-goala. Distinge dupa context: catch/dupa-actiune = arataMesaj; lista goala =
  .stare-goala. Daca ai dubiu pe o aparitie, las-o si raporteaz-o, nu ghici.
- Verificare functionala reala per ecran (cai de eroare greu de atins), nu doar node --check.
- verificator_conformitate.py TOTAL 0 la final. DS regula 0a: fara mig-gol mort ramas.
- Registru + comit.

================================================================================
TEMA 3 (verificare) — igiena preluarii tenant
================================================================================
Context (DECIZII.md, punte tenant): cand un cabinet adauga o firma cu CUI care exista deja
ca cont gratuit, se creeaza tenant nou gol (CORECT - datele gratuite nu se transfera, adevarul
contabil e la contabil). RAMAS de verificat: contul gratuit VECHI ce se intampla dupa? Ramane
activ (firma ar putea emite din DOUA locuri cu acelasi CUI)? Se inchide?

- Verifica la sursa (tenant_provisioning.py + ruta adaugare firma + auth): dupa ce cabinetul
  adauga firma cu CUI-ul unui cont gratuit existent, contul gratuit vechi ramane logabil/activ?
- Daca ramane activ SI ar putea emite cu acelasi CUI -> e o gaura de igiena. Raporteaza cu
  dovada, NU repara automat - propune (inchidere cont gratuit vechi la preluare? marcare?).
  Inchiderea unui cont = decizie, cere Costin.
- Doar raporteaza + propune. Nu construi fara DA.

================================================================================
Ordine: TEMA 0 -> 1 -> 2 -> 3. Raporteaza scurt dupa fiecare. STOP doar la porti.
La final: rezumat cu toate commit-urile si ce a atins fiecare porta (daca vreuna).
