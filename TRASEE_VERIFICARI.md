# TRASEE — CE TREBUIE SA FIE ADEVARAT DUPA FIECARE PAS

Al cincilea document, si singurul care NU se genereaza. `TRASEE.md` Partea XII spune
**ce face** fiecare pas — extras din cod. Aici se scrie **ce trebuie sa fie adevarat
dupa el** — iar aia nu se poate extrage din cod: codul spune ce s-a schimbat, nu ce
*trebuia* sa se schimbe.

**Cum se completeaza.** Sub fiecare pas e un rand care incepe cu `- [ ]`. Se inlocuieste
cu propozitia care trebuie sa fie adevarata dupa pasul ala. Diferenta care conteaza
(`TRASEE.md` VII.5): *«butonul a functionat, coada a trecut de la 3 la 2»* e o
observatie; *«declaratia are stare depusa, cu autor si moment, iar verdictul de
validare e pastrat»* e o verificare.

**Ce pazeste instrumentul aici:** ca niciun pas sa nu ramana fara loc. `--verificari`
NU rescrie ce s-a scris — listeaza doar ce lipseste. Un pas nou (o ruta noua) apare ca
lipsa in `core/test_trasee.py`, nu suprascrie nimic.

---

## T01 — Declarația — generare, validare, coadă, aprobare, depunere

*clasa MECANIC · 15 rute · 8 schimba date · 7 firme il pot exercita azi*

*citiri (nu schimba nimic): `/coada`, `/coada/{coada_id}/continut`, `/control-fiscal`, `/control-fiscal/{tenant_id}`, `/declaratii/tipuri`, `/firme/{tenant_id}/verificari`, `/termene`*

### `POST /coada`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [ ] 

### `POST /coada/{coada_id}/aproba`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [ ] 

### `POST /coada/{coada_id}/depune`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [ ] 

### `POST /coada/{coada_id}/respinge`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [ ] 

### `POST /declaratii/{tip}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: intoarce {avertismente, note_rezultat, operatiuni, tip, xml}*

- [ ] 

### `POST /declaratii/{tip}/valideaza`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: Genereaza declaratia si o trece prin validatorul OFICIAL ANAF (DUKIntegrator)*

- [ ] 

### `POST /tenants/{tenant_id}/istoric-declaratii-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie declaratii_depuse (DELETE/INSERT) — prin `istoric_declaratii_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie declaratii_depuse (DELETE/INSERT) · migrare_status (INSERT) — prin `istoric_declaratii_import_api`, `migrare_api`*

- [ ] 

## T02 — Factura emisă — creare, contabilizare, ieșiri

*clasa MECANIC · 19 rute · 13 schimba date · 12 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi-recurente`, `/tenants/{tenant_id}/facturi/numerotare`, `/tenants/{tenant_id}/facturi/{factura_id:int}`, `/tenants/{tenant_id}/facturi/{factura_id}/pdf`*

### `POST /api/v1/firme/{tenant_id}/facturi`

*garda `cere_api_key` · **fara rol***

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi-recurente`

*garda `cere_context` · **fara rol***

*ce face: scrie facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [ ] 

### `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

*ce face: scrie facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [ ] 

### `PUT /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

*ce face: scrie facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/emite`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie articole (INSERT/UPDATE) · factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `facturi_api`, `stocuri_cv_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/facturi/numerotare`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/facturi/{factura_id}`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Nota ciorna din factura (AI propune, contabilul valideaza) — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/email`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`, `firma_profil_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare`

*garda `cere_rol` · rol:admin_firma*

*ce face: F131: supapa per factura — scrie facturi (UPDATE) · firma_profil (UPDATE) — prin `scadentar`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/storno`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma`

*garda `cere_rol` · rol:admin_firma · scrie in facturi*

*ce face: Transforma proforma/aviz in factura fiscala (numerotare noua, nota se genereaza normal). — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [ ] 

## T03 — Statul de plată și fluturașul

*clasa MECANIC · 6 rute · 3 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/fluturas/{salariat_id}`, `/tenants/{tenant_id}/stat-plata`, `/tenants/{tenant_id}/stat-plata/emis`*

### `POST /tenants/{tenant_id}/salarii-contare/propunere`

*garda `cere_cabinet` · nu scrie nimic*

*ce face: Nota pe care ar scrie-o statul de plata + divergentele fata de D112, cu ambele cifre.*

- [ ] 

### `POST /tenants/{tenant_id}/salarii-contare`

*garda `cere_cabinet` · scrie nota ciorna a statului de plata*

*ce face: Scrie nota ciorna a statului de plata — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/stat-plata/corectie`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {salariat_id, an, luna} — scrie state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [ ] 

### `POST /tenants/{tenant_id}/stat-plata/emite`

*garda `cere_rol` · rol:admin_firma*

*ce face: corp: {an, luna} — scrie state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [ ] 

### `POST /tenants/{tenant_id}/stat-plata/motiv`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {exemplar_id, motiv} — scrie state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [ ] 

## T04 — Concediul medical

*clasa MECANIC · 5 rute · 3 schimba date · 4 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/concedii/coduri`, `/tenants/{tenant_id}/salariati/{salariat_id}/concedii`*

### `POST /tenants/{tenant_id}/calcul-cm`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {salariat_id, an, luna (luna certificatului), zile_lucratoare_cm, cod?, zile_episod?, prima_zi_din_episod?, spitalizare?, data_certificat?}*

- [ ] 

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/concedii`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [ ] 

## T05 — Nota contabilă — de la document la registrul-jurnal

*clasa MECANIC · 28 rute · 24 schimba date · 17 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/balanta`, `/tenants/{tenant_id}/documente/balanta`, `/tenants/{tenant_id}/jurnal`, `/tenants/{tenant_id}/plan-conturi`*

### `POST /tenants/{tenant_id}/jurnal`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [ ] 

### `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [ ] 

### `POST /tenants/{tenant_id}/nota-asociati`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie dividend|regularizare|imprumut, descriere?, + dividend{brut, interimar?, cu_plata?}; regularizare{total_interimar, dividend_anual}; imprumut{suma, f — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-avans`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie avans_platit|regularizare_platit|avans_incasat| regularizare_incasat, suma (fara TVA), cota?, destinatie? (platit: stocuri|servicii|imobilizari|imob — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-bacsis`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel incasare|distribuire, suma, sursa card|numerar (incasare) / banca|casa (distribuire), descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-chirie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel comodat|chirie_platita|chirie_incasata|refacturare, descriere?, cota?, + comodat{valoare, moment primire|restituire}; chirie_platita{chirie, proprietar p — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-contract-special`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel zilier|cenzor|mandat, brut, sursa casa|banca, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-credit`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie primire|dobanda|plata|restanta|garantie, tip lung|scurt, descriere?, + pe operatie: primire{suma}; dobanda{dobanda}; plata{rata?, dobanda?, comision — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-decont-deplasare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel avans|decont|plafon, descriere?, sursa casa|banca, + avans{suma}; decont{avans, diurna?, transport?, cazare?, cota?}; plafon{diurna_pe_zi, zile, salariu_ — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-inventariere`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

*ce face: corp: {data, operatie plus|plus_mf|minus|casare, descriere?, + plus{valoare, cont_stoc?}; plus_mf{valoare, cont_imobilizare?}; minus{valoare, cont_stoc?, imputabil?, valo — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · mijloace_fixe (INSERT/UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-leasing`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, tip primire|rata|reziduala|operational, descriere?, cota?, + campuri pe tip: primire{valoare_capital, dobanda_totala, cont_imobilizare?}; rata{capital, doban — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-lichidare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie vanzare_activ|partaj, descriere?, + vanzare_activ{pret, valoare_bruta, amortizare_cumulata, conturi?, cota?}; partaj{capital_social, rezerve?, profi — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-obiect-inventar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie achizitie|dare_folosinta|scoatere, valoare, cota?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-ong`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie venit|scutire, descriere?, + venit{suma, fel cotizatie|contributie|donatie|sponsorizare|financiar| fonduri|ocazional|alte, sursa casa|banca}; scutir — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-perisabilitati`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare_intrari, procent_limita (coef — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-productie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie obtinere|pic|vanzare, descriere?, + obtinere{cost_standard, cost_efectiv?}; pic{suma, moment constatare|reluare}; vanzare{pret_vanzare, cost_standar — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-provizion`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel creanta|provizion|stoc, actiune constituire|reluare, suma, descriere?, + creanta{zile_depasire?, garantata?, afiliata?, faliment?} | provizion{tip litigi — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-sgr`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie achizitie|vanzare|restituire|autofactura|virare, descriere?, + nr_ambalaje|suma, sursa casa|banca, + autofactura{garantii_returnate, tarif_gestionar — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-sponsorizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, suma, mod contract|plata, descriere?, + optional pentru calcul credit: cifra_afaceri, impozit_profit, tip_impozit profit|micro, beneficiar_in_registru} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-subventie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel exploatare|investitii|reluare, descriere?, + exploatare/investitii{suma, moment drept|incasare}; reluare{valoare_activ, subventie, amortizare_lunara}}. — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/nota-tva-incasare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, sens incasare|plata, suma_incasata, cota?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/plan-conturi`

*garda `cere_context` · **fara rol** · scrie in plan_conturi*

*ce face: scrie plan_conturi (INSERT)*

- [ ] 

## T06 — Importul de e-Factura și transmiterea prin SPV

*clasa MANUAL · 7 rute · 4 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi-primite`, `/tenants/{tenant_id}/facturi-primite/{primita_id}/xml`, `/tenants/{tenant_id}/trimiteri-spv`*

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge`

*garda `cere_context` · **fara rol** · scrie in efactura_primite, factur, validata*

*ce face: Respinge o factura primita: status=respinsa + motiv — scrie efactura_primite (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza`

*garda `cere_rol` · rol:admin_firma · scrie in efactura_primite, factur, facturi, validata*

*ce face: FOUR-EYES: omul valideaza ciorna importata de cron -> creeaza cheltuiala (factura primita) + leaga factura_id + status=validata — scrie efactura_primite (UPDATE) · facturi (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv`

*garda `cere_rol` · rol:admin_firma*

*ce face: Trimite o factura emisa in SPV (F126/F160) — scrie efactura_trimiteri (INSERT/UPDATE) — prin `efactura_send`*

- [ ] 

### `POST /tenants/{tenant_id}/import-efactura`

*garda `cere_cabinet` · **fara rol***

*ce face: Upload XML/ZIP e-Factura*

- [ ] 

## T07 — Extrasul bancar și potrivirea

*clasa MECANIC · 7 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/banca/reconciliere`, `/tenants/{tenant_id}/banca/reconciliere/facturi-deschise`*

### `POST /tenants/{tenant_id}/banca/parse-extras`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce {nr, tranzactii}*

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/import`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie extras_linii (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `reconciliere_api`*

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie extras_linii (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `reconciliere_api`*

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora`

*garda `cere_cabinet` · **fara rol** · scrie in extras_linii*

*ce face: scrie extras_linii (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza`

*garda `cere_cabinet` · **fara rol** · scrie in extras_linii*

*ce face: scrie extras_linii (UPDATE)*

- [ ] 

## T08 — NIR și recepția

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/nir`*

### `POST /tenants/{tenant_id}/stocuri/nir`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · nir (INSERT) · nir_linii (INSERT) — prin `stocuri_api`*

- [ ] 

## T09 — Casa și registrul de casă

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/casa/registru`*

### `POST /tenants/{tenant_id}/casa/operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [ ] 

## T10 — Inventarierea

*clasa MECANIC · 5 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d406-active`, `/tenants/{tenant_id}/d406-stocuri`, `/tenants/{tenant_id}/rip/inventar/{an}`, `/tenants/{tenant_id}/verificare-stocuri`*

### `POST /tenants/{tenant_id}/stocuri/inventar`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

## T11 — Închiderea lunii

*clasa MECANIC · 6 rute · 4 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/perioada`, `/tenants/{tenant_id}/perioade-blocate`*

### `POST /tenants/{tenant_id}/facturi/perioada/confirma`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Declara luna INCHISA pe facturi: evidenta ei devine autoritativa, iar semaforul se poate sprijini pe ea cand spune ca o declaratie nu se datoreaza*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/perioada/redeschide`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Redeschide luna (o corectie de facturi cere redeschiderea)*

- [ ] 

### `DELETE /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

*ce face: scrie perioade_blocate (DELETE)*

- [ ] 

### `POST /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

*ce face: scrie perioade_blocate (INSERT)*

- [ ] 

## T12 — Închiderea anului și situațiile financiare

*clasa PARTIAL · 4 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/s1003-xml`, `/tenants/{tenant_id}/s1005-xml`*

### `POST /tenants/{tenant_id}/s1003-valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

### `POST /tenants/{tenant_id}/s1005-valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

## T13 — Trecerea de regim fiscal

*clasa MECANIC · 8 rute · 4 schimba date · 17 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/vector`, `/tenants/{tenant_id}/firma-profil`, `/tenants/{tenant_id}/firma-profil/date`, `/tenants/{tenant_id}/vector`*

### `POST /tenants/{tenant_id}/firma-profil/date`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [ ] 

### `POST /tenants/{tenant_id}/firma-profil/model`

*garda `cere_context` · **fara rol***

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [ ] 

### `POST /tenants/{tenant_id}/firma-profil/regim-tva`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [ ] 

### `POST /tenants/{tenant_id}/vector`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie firma_profil (INSERT/UPDATE) · migrare_status (INSERT) — prin `firma_profil_api`, `migrare_api`, `vector_fiscal_api`*

- [ ] 

## T14 — Preluarea unei firme

*clasa MECANIC · 32 rute · 21 schimba date · 5 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/asociati`, `/migrare/istoric-declaratii`, `/migrare/mijloace-fixe`, `/migrare/parteneri`, `/migrare/plan-conturi`, `/migrare/salariati`, `/migrare/solduri`, `/migrare/status`, `/migrare/straturi`, `/tenants/{tenant_id}/parteneri`, `/tenants/{tenant_id}/solduri`*

### `POST /control-fiscal/{tenant_id}/audit-preluare`

*garda `cere_rol` · rol:admin_firma*

*ce face: F183: audit de PRELUARE firma — coerenta INTERNA a pachetului preluat de la contabilul anterior (balanta echilibrata, defalcare parteneri vs sintetic, solduri fiscale vs  — scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

### `POST /migrare/fisier`

*garda `cere_cabinet` · **fara rol***

*ce face: Primește un CSV/XLSX, extrage CUI-urile și le validează la ANAF.*

- [ ] 

### `POST /migrare/importa`

*garda `cere_rol` · rol:admin_firma*

*ce face: Creează câte un tenant pentru fiecare firmă selectată — scrie firma_profil (INSERT/UPDATE) · migrare_status (INSERT) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `migrare_api`, `tenant_provisioning`*

- [ ] 

### `POST /migrare/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Primește un fișier (.csv/.xlsx), extrage CUI-urile și le validează la ANAF.*

- [ ] 

### `POST /migrare/status`

*garda `cere_rol` · rol:admin_firma*

*ce face: Marchează un strat 'gata' sau 'in_lucru' (cu notă obligatorie la in_lucru). — scrie migrare_status (INSERT) — prin `migrare_api`*

- [ ] 

### `POST /migrare/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: Verifică o listă de CUI-uri la ANAF; întoarce denumirea + status.*

- [ ] 

### `POST /tenants/{tenant_id}/articole-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie articole (INSERT) · miscari_stoc (INSERT) — prin `articole_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/articole-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT) · miscari_stoc (INSERT) — prin `articole_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/asociati-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie asociati (DELETE/INSERT) — prin `asociati_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/asociati-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie asociati (DELETE/INSERT) · migrare_status (INSERT) — prin `asociati_import_api`, `migrare_api`*

- [ ] 

### `POST /tenants/{tenant_id}/mijloace-fixe-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie mijloace_fixe (DELETE/INSERT) — prin `mijloace_fixe_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie migrare_status (INSERT) · mijloace_fixe (DELETE/INSERT) — prin `migrare_api`, `mijloace_fixe_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/parteneri`

*garda `cere_rol` · rol:admin_firma*

*ce face: Salveaza soldurile partenerilor unei firme (inlocuieste ce era). — scrie solduri_parteneri (DELETE/INSERT) — prin `solduri_parteneri_api`*

- [ ] 

### `POST /tenants/{tenant_id}/parteneri/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parseaza fisierul de parteneri si intoarce preview + verificare coerenta vs balanta. — scrie migrare_status (INSERT) · solduri_parteneri (DELETE/INSERT) — prin `migrare_api`, `solduri_parteneri_api`*

- [ ] 

### `POST /tenants/{tenant_id}/retete-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: intoarce ce da `retete_import_api.importa()`*

- [ ] 

### `POST /tenants/{tenant_id}/retete-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce {retete, rezumat}*

- [ ] 

### `POST /tenants/{tenant_id}/rip-import/incarca`

*garda `cere_rol` · rol:admin_firma*

*ce face: Import registru incasari-plati la preluarea unui PFA — scrie migrare_status (INSERT) · rip_operatiuni (INSERT) — prin `migrare_api`, `rip_migrare_api`*

- [ ] 

### `POST /tenants/{tenant_id}/salariati-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: Importa salariatii cu CNP valid (upsert pe CNP) — scrie salariati (INSERT) — prin `salariati_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/salariati-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parseaza exportul de salariati si intoarce preview cu validare CNP (nu salveaza). — scrie migrare_status (INSERT) · salariati (INSERT) — prin `migrare_api`, `salariati_import_api`*

- [ ] 

### `POST /tenants/{tenant_id}/solduri`

*garda `cere_rol` · rol:admin_firma*

*ce face: Salvează soldurile inițiale ale unei firme (înlocuiește ce era). — scrie plan_conturi (INSERT) · solduri_initiale (DELETE/INSERT) — prin `solduri_api`*

- [ ] 

### `POST /tenants/{tenant_id}/solduri/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parsează o balanță și întoarce preview (nu salvează). — scrie migrare_status (INSERT) · plan_conturi (INSERT) · solduri_initiale (DELETE/INSERT) — prin `migrare_api`, `solduri_api`*

- [ ] 

## T15 — Salariatul — angajare, contract, adeverință, REGES

*clasa MANUAL · 17 rute · 12 schimba date · 8 firme il pot exercita azi*

*citiri (nu schimba nimic): `/contracte/marcaje`, `/cor`, `/tenants/{tenant_id}/contracte/sabloane`, `/tenants/{tenant_id}/salariati`, `/tenants/{tenant_id}/salariati/{salariat_id}`*

### `POST /tenants/{tenant_id}/contracte/genereaza`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [ ] 

### `POST /tenants/{tenant_id}/contracte/sabloane`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [ ] 

### `POST /tenants/{tenant_id}/prapastie-salariu`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce ce da `_pr.prapastie()`*

- [ ] 

### `POST /tenants/{tenant_id}/reges-config`

*garda `cere_cabinet` · **fara rol** · scrie in reges_chei*

*ce face: corp: {username, parola, mediu test|prod} — scrie reges_chei (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/reges-poll`

*garda `cere_cabinet` · **fara rol** · scrie in reges_mesaje*

*ce face: Citeste+consuma un mesaj din coada REGES; salveaza referintele in reges_mesaje. — scrie reges_mesaje (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/reges-trimite-salariat`

*garda `cere_rol` · rol:admin_firma · scrie in reges_mesaje*

*ce face: corp: {salariat_id, adresa, contract {numar, data_contract, data_inceput, salariu, cor, ...}?} — scrie reges_mesaje (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/salariati`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [ ] 

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta`

*garda `cere_rol` · rol:admin_firma*

*ce face: F136: adeverinta de salariat (art*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: [F133 Faza 2a] beneficiu one-off pe luna (vacanta/cadou/cultural) — scrie beneficii_lunare (DELETE/INSERT) — prin `beneficii_api`*

- [ ] 

## T16 — Pontajul

*clasa MECANIC · 4 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/salariati/{salariat_id}/pontaj`, `/util/zile-lucratoare`*

### `POST /tenants/{tenant_id}/pontaj/confirma`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Confirma pontajul lunii -> devine AUTORITATIV pentru salarizare (tichete pe zile efectiv lucrate)*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj`

*garda `cere_context` · **fara rol***

*ce face: F135: seteaza starea unei zile (stare goala/prezent = sterge exceptia). — scrie pontaj (DELETE/INSERT) — prin `pontaj`*

- [ ] 

## T17 — Plata salariilor — fișierul către bancă

*clasa PARTIAL · 2 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/plata-salarii-preview`*

### `POST /tenants/{tenant_id}/plata-salarii-fisier`

*garda `cere_rol` · rol:admin_firma*

*ce face: [F134] Fisierul SEPA/ISO 20022 pain.001.001.03 de plata a salariilor NET pe card (download) — scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

## T18 — Chitanța și încasarea

*clasa MANUAL · 6 rute · 3 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/plata/{ref}`, `/tenants/{tenant_id}/chitante`, `/tenants/{tenant_id}/chitante/{chitanta_id}/pdf`*

### `POST /public/plata/{ref}/confirma`

*garda `FARA GARDA` · **fara rol***

*ce face: scrie facturi (UPDATE) — prin `plati`*

- [ ] 

### `POST /tenants/{tenant_id}/chitante`

*garda `cere_rol` · rol:admin_firma · scrie in chitante, facturi*

*ce face: Emite chitanta (cod 14-4-1, Ordin 2634/2015) pentru incasare in numerar: numerotare pe serie per firma + operatiune in Registrul de casa prin casa_api (5311=4111, nota ci — scrie casa_operatiuni (DELETE/INSERT) · chitante (INSERT) · facturi (UPDATE) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie facturi (UPDATE) — prin `plati`*

- [ ] 

## T19 — Scadențarul și notificările de scadență

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/scadentar`*

### `PUT /tenants/{tenant_id}/scadentar/opt-in`

*garda `cere_rol` · rol:admin_firma*

*ce face: F131: activeaza/dezactiveaza notificarile email de scadenta pt firma (default OFF). — scrie facturi (UPDATE) · firma_profil (UPDATE) — prin `scadentar`*

- [ ] 

## T20 — Mișcarea de stoc — intrare, ieșire, transfer, reclasificare

*clasa MECANIC · 12 rute · 7 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/analitica`, `/tenants/{tenant_id}/stocuri/articole`, `/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa`, `/tenants/{tenant_id}/stocuri/barcode/{cod}`, `/tenants/{tenant_id}/stocuri/locatii`*

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/descarcare`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · nir (INSERT) · nir_linii (INSERT) — prin `stocuri_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/iesire`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/intrare`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/reclasificare`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/transfer`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

## T21 — Rețeta și producția

*clasa MECANIC · 9 rute · 7 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/produse`, `/tenants/{tenant_id}/retete`*

### `POST /tenants/{tenant_id}/produse`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `POST /tenants/{tenant_id}/produse/potriveste`

*garda `cere_context` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `POST /tenants/{tenant_id}/retete`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [ ] 

### `POST /tenants/{tenant_id}/retete/descarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/retete/{reteta_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [ ] 

## T22 — Mijlocul fix și amortizarea

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/mijloace-fixe`*

### `POST /tenants/{tenant_id}/amortizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ. — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/reevaluare-imobilizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie reevaluare|surplus, + reevaluare{mijloc_fix_id, valoare_justa, sold_105_activ?, pierdere_655_anterioara?} | surplus{suma}} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T23 — Bonul de la client — portalul și decontul

*clasa MECANIC · 9 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/portal/bon/{bon_id}/imagine/{n}`, `/tenants/{tenant_id}/bonuri/de-verificat`, `/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate`, `/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}`*

### `POST /portal/bon`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Extrage datele bonului cu AI si salveaza ca DRAFT (status='extras') + pozele pe disc — scrie bonuri (DELETE/INSERT)*

- [ ] 

### `DELETE /portal/bon/{bon_id}`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Clientul reface poza -> draftul (status='extras') si pozele lui se sterg. — scrie bonuri (DELETE)*

- [ ] 

### `POST /portal/bon/{bon_id}/confirma`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Clientul confirma ca poza e intreaga si lizibila -> bonul intra la contabil. — scrie bonuri (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba`

*garda `cere_cabinet` · **fara rol** · scrie in bonuri, inregistrari, inregistrari_linii*

*ce face: scrie bonuri (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge`

*garda `cere_rol` · rol:admin_firma · scrie in bonuri, facturi*

*ce face: Chitanta certificata de contabil: plata furnizor prin Registrul de casa (casa_api.adauga -> 401=5311 ciorna + operatiune casa + verificare plafon) — scrie bonuri (UPDATE) · casa_operatiuni (DELETE/INSERT) · facturi (UPDATE) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [ ] 

## T24 — Bonul fiscal și raportul Z (AMEF, horeca)

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/horeca/import-amef`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Upload p7b/XML AMEF (OPANAF 146/2018 II.7) -> nota Raport Z CIORNA — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/horeca/raport-z`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T25 — Comanda din magazinul online (WooCommerce)

*clasa MANUAL · 3 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/woocommerce/config`*

### `PUT /tenants/{tenant_id}/woocommerce/config`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

*ce face: scrie firma_profil (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/woocommerce/sincronizeaza`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie facturi (UPDATE) · firma_profil (UPDATE) — prin `woocommerce`*

- [ ] 

## T26 — Registratura

*clasa MECANIC · 2 rute · 1 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/registratura`*

### `POST /tenants/{tenant_id}/registratura`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie registratura (INSERT) — prin `registratura_api`*

- [ ] 

## T27 — e-Transport

*clasa MANUAL · 3 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/etransport/trimiteri`*

### `POST /tenants/{tenant_id}/etransport-xml`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce {nota, xml}*

- [ ] 

### `POST /tenants/{tenant_id}/etransport/trimite`

*garda `cere_rol` · rol:admin_firma*

*ce face: Trimite notificarea UIT in SPV (F121): genereaza XML + trimite() cu PORTI in ordine (garda de timp -> idempotency -> validare pe TEST -> upload) — scrie etransport_trimiteri (INSERT/UPDATE) — prin `etransport_send`*

- [ ] 

## T28 — Operațiunile intracomunitare, VIES și Intrastat

*clasa MECANIC · 10 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/verifica-cui/{cui}`, `/tenants/{tenant_id}/d390-clasificare`, `/tenants/{tenant_id}/intrastat-praguri`, `/tenants/{tenant_id}/verifica-cui/{cui}`, `/tenants/{tenant_id}/verifica-vies`*

### `POST /tenants/{tenant_id}/achizitie-ic`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: AIC bunuri/servicii primite (art — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/d390-clasificare/manual`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga linie pur manuala: {an, luna, tip, tara, cod, den, baza}. — scrie d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare`

*garda `cere_cabinet` · **fara rol***

*ce face: Override tip pe o operatiune auto: {an, luna, directie, tara, cod, tip}. — scrie d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-ic`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: LIC bunuri (art — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T29 — Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă

*clasa MECANIC · 11 rute · 10 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/jurnal-marja`*

### `POST /tenants/{tenant_id}/achizitie-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare (fara taxa), cont_cheltuiala, agricultor_in_registru, agricultor?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/achizitie-necorporala`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

*ce face: corp: {data, denumire, valoare (fara TVA), tip software|licenta|brevet| dezvoltare|constituire, dnf_luni?, cota?, cod?} — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · mijloace_fixe (INSERT) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/achizitie-neinregistrat`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: Achizitie de la persoana fizica NEINREGISTRATA in scop TVA -> op N in D394 (pct.216 tip_partener=2) — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/achizitie-taxare-inversa`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, categorie, valoare (fara TVA), cont_destinatie, cota?, furnizor_platitor_tva, descriere?} — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/export-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare, tara_client, dovada_export, cont_venit?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/import-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare_vamala (RON), procent_taxa_vamala?, accize?, accesorii?, cota?, certificat_amanare?, cont_destinatie, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, pret (fara taxa), descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-aur-investitii`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, tip lingou|plancheta|moneda, puritate, an_emisie?, pret_unitar?, valoare_aur?, suma, optiune_taxare?, calitate_client PF|PJ, client_identificare, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-marja`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, pret_vanzare, pret_cumparare, cota?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-marja-turism`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, calitate_client PF|PJ, locuri [RO|UE|NONUE], optiune_normal?, intermediar?, cota?, descriere?} + per regim: special: incasat, cost_ue, cost_non_ue? | normal: — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T30 — Operațiunile în valută

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/decontare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Incasare creanta / plata datorie in valuta cu diferenta de curs 665/765 — scrie curs_bnr_zilnic (INSERT) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `curs_bnr`*

- [ ] 

### `POST /tenants/{tenant_id}/reevaluare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Reevaluare lunara solduri valuta (OMFP 1802 pct — scrie curs_bnr_zilnic (INSERT) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `curs_bnr`*

- [ ] 

## T31 — Completările manuale la o declarație (D300, D301)

*clasa MECANIC · 6 rute · 4 schimba date · 3 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d300-manual`, `/tenants/{tenant_id}/d301-operatiuni`*

### `POST /tenants/{tenant_id}/d300-manual`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga/actualizeaza un rand manual D300: {an, luna, rand, baza, tva, descriere}. — scrie d300_manual (DELETE/INSERT) — prin `d300_manual_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/d300-manual/{rid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie d300_manual (DELETE/INSERT) — prin `d300_manual_api`*

- [ ] 

### `POST /tenants/{tenant_id}/d301-operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga o operatiune: {an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, cota}. — scrie d301_operatiuni (DELETE/INSERT) — prin `d301_operatiuni_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie d301_operatiuni (DELETE/INSERT) — prin `d301_operatiuni_api`*

- [ ] 

## T32 — Registrul de încasări și plăți (partida simplă)

*clasa MECANIC · 7 rute · 5 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/rip/d212/{an}`, `/tenants/{tenant_id}/rip/registru`*

### `POST /tenants/{tenant_id}/rip/import-banca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `POST /tenants/{tenant_id}/rip/import-casa`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `POST /tenants/{tenant_id}/rip/operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

## T33 — Exportul contabil (SAGA, WinMentor)

*clasa PARTIAL · 3 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/{factura_id}/export-saga`*

### `POST /tenants/{tenant_id}/facturi/export-saga`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/export-winmentor`

*garda `cere_rol` · rol:admin_firma*

*ce face: Export WinMENTOR: Facturi.txt + Articole.txt (Windows-1250) co-locate intr-un zip — scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

## T34 — Rapoartele comerciale, centrele de cost și rapoartele salvate

*clasa MECANIC · 14 rute · 5 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/ansamblu`, `/api/v1/firme/{tenant_id}/kpi`, `/cabinet/consolidare`, `/tenants/{tenant_id}/centre-cost`, `/tenants/{tenant_id}/centre-cost/raport`, `/tenants/{tenant_id}/centre-cost/varianta`, `/tenants/{tenant_id}/rapoarte-comerciale`, `/tenants/{tenant_id}/rapoarte-comerciale/fisa`, `/tenants/{tenant_id}/rapoarte-salvate`*

### `POST /tenants/{tenant_id}/centre-cost`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget`

*garda `cere_cabinet` · **fara rol***

*ce face: Seteaza bugetul anual (cheltuieli + venituri) al unui centru pe un an. — scrie bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [ ] 

### `POST /tenants/{tenant_id}/rapoarte-salvate`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rapoarte_salvate (DELETE/INSERT) — prin `rapoarte_comerciale_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rapoarte_salvate (DELETE/INSERT) — prin `rapoarte_comerciale_api`*

- [ ] 

## T35 — Pachetul lunar către client și solicitările lui

*clasa MECANIC · 36 rute · 15 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/pachete/{tenant_id}/poveste`, `/pachete/{tenant_id}/preview`, `/pachete/{tenant_id}/rezumat`, `/portal/acasa`, `/portal/acces-cont`, `/portal/cashflow`, `/portal/declaratii`, `/portal/documente/balanta`, `/portal/documente/luni`, `/portal/facturi`, `/portal/firma`, `/portal/firme`, `/portal/kpi`, `/portal/povesti`, `/portal/recomanda/preview`, `/portal/solicitari`, `/portal/solicitari/contor`, `/tenants/{tenant_id}/client-acces`, `/tenants/{tenant_id}/clienti`, `/tenants/{tenant_id}/clienti/{client_id}`, `/tenants/{tenant_id}/solicitari`*

### `POST /pachete/{tenant_id}/genereaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie pachet_povestea (INSERT) — prin `pachete_api`*

- [ ] 

### `POST /pachete/{tenant_id}/poveste`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie pachet_povestea (INSERT) — prin `pachete_api`*

- [ ] 

### `POST /pachete/{tenant_id}/trimite`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie pachet_povestea (INSERT) — prin `pachete_api`*

- [ ] 

### `POST /portal/acces-cont/acces`

*garda `cere_client` · rol:verificat-în-corp · scrie in user_tenants, users*

*ce face: scrie user_tenants (INSERT) · users (INSERT/UPDATE)*

- [ ] 

### `DELETE /portal/acces-cont/acces/{user_id}`

*garda `cere_client` · **fara rol** · scrie in user_tenants, users*

*ce face: scrie user_tenants (DELETE) · users (UPDATE)*

- [ ] 

### `PUT /portal/acces-cont/email`

*garda `cere_client` · **fara rol** · scrie in users*

*ce face: scrie users (UPDATE)*

- [ ] 

### `POST /portal/recomanda`

*garda `cere_client` · **fara rol***

*ce face: intoarce {ok, rezultate}*

- [ ] 

### `POST /portal/solicitari`

*garda `cere_client` · **fara rol** · scrie in solicitari_client*

*ce face: scrie notificari (INSERT/UPDATE) · solicitari_client (INSERT) — prin `notificari_api`*

- [ ] 

### `POST /tenants/{tenant_id}/acces-portal`

*garda `cere_rol` · rol:admin_firma,angajat,verificat-în-corp*

*ce face: Emite un token de PREVIZUALIZARE (read-only, tab-local) pentru portalul clientului firmei*

- [ ] 

### `POST /tenants/{tenant_id}/client-acces`

*garda `cere_rol` · rol:admin_firma,verificat-în-corp · scrie in user_tenants, users*

*ce face: scrie firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) · users (INSERT/UPDATE) — prin `tenant_provisioning`*

- [ ] 

### `DELETE /tenants/{tenant_id}/client-acces/{user_id}`

*garda `cere_rol` · rol:admin_firma · scrie in users*

*ce face: scrie users (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/clienti`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [ ] 

### `POST /tenants/{tenant_id}/solicitari`

*garda `cere_rol` · rol:admin_firma · scrie in solicitari_client*

*ce face: scrie solicitari_client (INSERT)*

- [ ] 

