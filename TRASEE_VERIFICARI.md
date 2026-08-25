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

- [ ] 

### `POST /coada/{coada_id}/aproba`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `POST /coada/{coada_id}/depune`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /coada/{coada_id}/respinge`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `POST /declaratii/{tip}`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `POST /declaratii/{tip}/valideaza`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `POST /tenants/{tenant_id}/istoric-declaratii-import`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T02 — Factura emisă — creare, contabilizare, ieșiri

*clasa MECANIC · 19 rute · 13 schimba date · 12 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi-recurente`, `/tenants/{tenant_id}/facturi/numerotare`, `/tenants/{tenant_id}/facturi/{factura_id:int}`, `/tenants/{tenant_id}/facturi/{factura_id}/pdf`*

### `POST /api/v1/firme/{tenant_id}/facturi`

*garda `cere_api_key` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/facturi`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/facturi-recurente`

*garda `cere_context` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/facturi/emite`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `PUT /tenants/{tenant_id}/facturi/numerotare`

*garda `cere_context` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/facturi/{factura_id}`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/email`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare`

*garda `cere_context` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/storno`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma`

*garda `cere_context` · **fara rol** · scrie in facturi*

- [ ] 

## T03 — Statul de plată și fluturașul

*clasa MECANIC · 6 rute · 3 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/fluturas/{salariat_id}`, `/tenants/{tenant_id}/stat-plata`, `/tenants/{tenant_id}/stat-plata/emis`*

### `POST /tenants/{tenant_id}/stat-plata/corectie`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stat-plata/emite`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/stat-plata/motiv`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T04 — Concediul medical

*clasa MECANIC · 5 rute · 3 schimba date · 4 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/concedii/coduri`, `/tenants/{tenant_id}/salariati/{salariat_id}/concedii`*

### `POST /tenants/{tenant_id}/calcul-cm`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/concedii`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

## T05 — Nota contabilă — de la document la registrul-jurnal

*clasa MECANIC · 28 rute · 24 schimba date · 17 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/balanta`, `/tenants/{tenant_id}/documente/balanta`, `/tenants/{tenant_id}/jurnal`, `/tenants/{tenant_id}/plan-conturi`*

### `POST /tenants/{tenant_id}/jurnal`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/nota-asociati`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-avans`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-bacsis`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-chirie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-contract-special`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-credit`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-decont-deplasare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-inventariere`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

- [ ] 

### `POST /tenants/{tenant_id}/nota-leasing`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-lichidare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-obiect-inventar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-ong`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-perisabilitati`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-productie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-provizion`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-sgr`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-sponsorizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-subventie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/nota-tva-incasare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/plan-conturi`

*garda `cere_context` · **fara rol** · scrie in plan_conturi*

- [ ] 

## T06 — Importul de e-Factura și transmiterea prin SPV

*clasa MANUAL · 7 rute · 4 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi-primite`, `/tenants/{tenant_id}/facturi-primite/{primita_id}/xml`, `/tenants/{tenant_id}/trimiteri-spv`*

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge`

*garda `cere_context` · **fara rol** · scrie in efactura_primite, factur, validata*

- [ ] 

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza`

*garda `cere_context` · **fara rol** · scrie in efactura_primite, factur, facturi, validata*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/import-efactura`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T07 — Extrasul bancar și potrivirea

*clasa MECANIC · 7 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/banca/reconciliere`, `/tenants/{tenant_id}/banca/reconciliere/facturi-deschise`*

### `POST /tenants/{tenant_id}/banca/parse-extras`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/import`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora`

*garda `cere_cabinet` · **fara rol** · scrie in extras_linii*

- [ ] 

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza`

*garda `cere_cabinet` · **fara rol** · scrie in extras_linii*

- [ ] 

## T08 — NIR și recepția

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/nir`*

### `POST /tenants/{tenant_id}/stocuri/nir`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T09 — Casa și registrul de casă

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/casa/registru`*

### `POST /tenants/{tenant_id}/casa/operatiuni`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T10 — Inventarierea

*clasa MECANIC · 5 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d406-active`, `/tenants/{tenant_id}/d406-stocuri`, `/tenants/{tenant_id}/rip/inventar/{an}`, `/tenants/{tenant_id}/verificare-stocuri`*

### `POST /tenants/{tenant_id}/stocuri/inventar`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T11 — Închiderea lunii

*clasa MECANIC · 6 rute · 4 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/perioada`, `/tenants/{tenant_id}/perioade-blocate`*

### `POST /tenants/{tenant_id}/facturi/perioada/confirma`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/perioada/redeschide`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `DELETE /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

- [ ] 

### `POST /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

- [ ] 

## T12 — Închiderea anului și situațiile financiare

*clasa PARTIAL · 4 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/s1003-xml`, `/tenants/{tenant_id}/s1005-xml`*

### `POST /tenants/{tenant_id}/s1003-valideaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/s1005-valideaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T13 — Trecerea de regim fiscal

*clasa MECANIC · 8 rute · 4 schimba date · 17 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/vector`, `/tenants/{tenant_id}/firma-profil`, `/tenants/{tenant_id}/firma-profil/date`, `/tenants/{tenant_id}/vector`*

### `POST /tenants/{tenant_id}/firma-profil/date`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/firma-profil/model`

*garda `cere_context` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/firma-profil/regim-tva`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

- [ ] 

### `POST /tenants/{tenant_id}/vector`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

## T14 — Preluarea unei firme

*clasa MECANIC · 32 rute · 20 schimba date · 5 firme il pot exercita azi*

*citiri (nu schimba nimic): `/control-fiscal/{tenant_id}/audit-preluare`, `/migrare/asociati`, `/migrare/istoric-declaratii`, `/migrare/mijloace-fixe`, `/migrare/parteneri`, `/migrare/plan-conturi`, `/migrare/salariati`, `/migrare/solduri`, `/migrare/status`, `/migrare/straturi`, `/tenants/{tenant_id}/parteneri`, `/tenants/{tenant_id}/solduri`*

### `POST /migrare/fisier`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /migrare/importa`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /migrare/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /migrare/status`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /migrare/valideaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/articole-import`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/articole-import/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/asociati-import`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/asociati-import/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/mijloace-fixe-import`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/parteneri`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/parteneri/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/retete-import`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/retete-import/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/rip-import/incarca`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/salariati-import`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/salariati-import/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/solduri`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/solduri/incarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T15 — Salariatul — angajare, contract, adeverință, REGES

*clasa MANUAL · 16 rute · 11 schimba date · 8 firme il pot exercita azi*

*citiri (nu schimba nimic): `/contracte/marcaje`, `/cor`, `/tenants/{tenant_id}/contracte/sabloane`, `/tenants/{tenant_id}/salariati`, `/tenants/{tenant_id}/salariati/{salariat_id}`*

### `POST /tenants/{tenant_id}/contracte/genereaza`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /tenants/{tenant_id}/contracte/sabloane`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/reges-config`

*garda `cere_cabinet` · **fara rol** · scrie in reges_chei*

- [ ] 

### `POST /tenants/{tenant_id}/reges-poll`

*garda `cere_cabinet` · **fara rol** · scrie in reges_mesaje*

- [ ] 

### `POST /tenants/{tenant_id}/reges-trimite-salariat`

*garda `cere_rol` · rol:admin_firma · scrie in reges_mesaje*

- [ ] 

### `POST /tenants/{tenant_id}/salariati`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

## T16 — Pontajul

*clasa MECANIC · 4 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/salariati/{salariat_id}/pontaj`, `/util/zile-lucratoare`*

### `POST /tenants/{tenant_id}/pontaj/confirma`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj`

*garda `cere_context` · **fara rol***

- [ ] 

## T17 — Plata salariilor — fișierul către bancă

*clasa PARTIAL · 2 rute · 0 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/plata-salarii-fisier`, `/tenants/{tenant_id}/plata-salarii-preview`*

**Traseul nu are niciun pas care schimba ceva.** Ce trebuie sa fie adevarat
dupa el e o proprietate a IESIRII, nu a unui pas:

- [ ] 

## T18 — Chitanța și încasarea

*clasa MANUAL · 6 rute · 3 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/plata/{ref}`, `/tenants/{tenant_id}/chitante`, `/tenants/{tenant_id}/chitante/{chitanta_id}/pdf`*

### `POST /public/plata/{ref}/confirma`

*garda `FARA GARDA` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/chitante`

*garda `cere_rol` · rol:admin_firma · scrie in chitante, facturi*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata`

*garda `cere_context` · **fara rol***

- [ ] 

## T19 — Scadențarul și notificările de scadență

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/scadentar`*

### `PUT /tenants/{tenant_id}/scadentar/opt-in`

*garda `cere_context` · **fara rol***

- [ ] 

## T20 — Mișcarea de stoc — intrare, ieșire, transfer, reclasificare

*clasa MECANIC · 12 rute · 7 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/analitica`, `/tenants/{tenant_id}/stocuri/articole`, `/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa`, `/tenants/{tenant_id}/stocuri/barcode/{cod}`, `/tenants/{tenant_id}/stocuri/locatii`*

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/descarcare`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/iesire`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/intrare`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/reclasificare`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/transfer`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T21 — Rețeta și producția

*clasa MECANIC · 9 rute · 7 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/produse`, `/tenants/{tenant_id}/retete`*

### `POST /tenants/{tenant_id}/produse`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/produse/potriveste`

*garda `cere_context` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/retete`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/retete/descarca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/retete/{reteta_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T22 — Mijlocul fix și amortizarea

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/mijloace-fixe`*

### `POST /tenants/{tenant_id}/amortizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/reevaluare-imobilizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

## T23 — Bonul de la client — portalul și decontul

*clasa MECANIC · 9 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/portal/bon/{bon_id}/imagine/{n}`, `/tenants/{tenant_id}/bonuri/de-verificat`, `/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate`, `/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}`*

### `POST /portal/bon`

*garda `cere_context` · **fara rol** · scrie in bonuri*

- [ ] 

### `DELETE /portal/bon/{bon_id}`

*garda `cere_context` · **fara rol** · scrie in bonuri*

- [ ] 

### `POST /portal/bon/{bon_id}/confirma`

*garda `cere_context` · **fara rol** · scrie in bonuri*

- [ ] 

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba`

*garda `cere_cabinet` · **fara rol** · scrie in bonuri, inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge`

*garda `cere_cabinet` · **fara rol** · scrie in bonuri, facturi*

- [ ] 

## T24 — Bonul fiscal și raportul Z (AMEF, horeca)

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/horeca/import-amef`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/horeca/raport-z`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

## T25 — Comanda din magazinul online (WooCommerce)

*clasa MANUAL · 3 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/woocommerce/config`*

### `PUT /tenants/{tenant_id}/woocommerce/config`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

- [ ] 

### `POST /tenants/{tenant_id}/woocommerce/sincronizeaza`

*garda `cere_context` · **fara rol***

- [ ] 

## T26 — Registratura

*clasa MECANIC · 2 rute · 1 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/registratura`*

### `POST /tenants/{tenant_id}/registratura`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T27 — e-Transport

*clasa MANUAL · 3 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/etransport/trimiteri`*

### `POST /tenants/{tenant_id}/etransport-xml`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/etransport/trimite`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

## T28 — Operațiunile intracomunitare, VIES și Intrastat

*clasa MECANIC · 10 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/verifica-cui/{cui}`, `/tenants/{tenant_id}/d390-clasificare`, `/tenants/{tenant_id}/intrastat-praguri`, `/tenants/{tenant_id}/verifica-cui/{cui}`, `/tenants/{tenant_id}/verifica-vies`*

### `POST /tenants/{tenant_id}/achizitie-ic`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/d390-clasificare/manual`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-ic`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

## T29 — Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă

*clasa MECANIC · 11 rute · 10 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/jurnal-marja`*

### `POST /tenants/{tenant_id}/achizitie-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/achizitie-necorporala`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

- [ ] 

### `POST /tenants/{tenant_id}/achizitie-neinregistrat`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/achizitie-taxare-inversa`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/export-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/import-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-aur-investitii`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-marja`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-marja-turism`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

## T30 — Operațiunile în valută

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/decontare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

### `POST /tenants/{tenant_id}/reevaluare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

- [ ] 

## T31 — Completările manuale la o declarație (D300, D301)

*clasa MECANIC · 6 rute · 4 schimba date · 3 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d300-manual`, `/tenants/{tenant_id}/d301-operatiuni`*

### `POST /tenants/{tenant_id}/d300-manual`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/d300-manual/{rid}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/d301-operatiuni`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T32 — Registrul de încasări și plăți (partida simplă)

*clasa MECANIC · 7 rute · 5 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/rip/d212/{an}`, `/tenants/{tenant_id}/rip/registru`*

### `POST /tenants/{tenant_id}/rip/import-banca`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/rip/import-casa`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/rip/operatiuni`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T33 — Exportul contabil (SAGA, WinMentor)

*clasa PARTIAL · 3 rute · 0 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/export-saga`, `/tenants/{tenant_id}/facturi/export-winmentor`, `/tenants/{tenant_id}/facturi/{factura_id}/export-saga`*

**Traseul nu are niciun pas care schimba ceva.** Ce trebuie sa fie adevarat
dupa el e o proprietate a IESIRII, nu a unui pas:

- [ ] 

## T34 — Rapoartele comerciale, centrele de cost și rapoartele salvate

*clasa MECANIC · 14 rute · 5 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/ansamblu`, `/api/v1/firme/{tenant_id}/kpi`, `/cabinet/consolidare`, `/tenants/{tenant_id}/centre-cost`, `/tenants/{tenant_id}/centre-cost/raport`, `/tenants/{tenant_id}/centre-cost/varianta`, `/tenants/{tenant_id}/rapoarte-comerciale`, `/tenants/{tenant_id}/rapoarte-comerciale/fisa`, `/tenants/{tenant_id}/rapoarte-salvate`*

### `POST /tenants/{tenant_id}/centre-cost`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /tenants/{tenant_id}/rapoarte-salvate`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}`

*garda `cere_cabinet` · **fara rol***

- [ ] 

## T35 — Pachetul lunar către client și solicitările lui

*clasa MECANIC · 36 rute · 15 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/pachete/{tenant_id}/poveste`, `/pachete/{tenant_id}/preview`, `/pachete/{tenant_id}/rezumat`, `/portal/acasa`, `/portal/acces-cont`, `/portal/cashflow`, `/portal/declaratii`, `/portal/documente/balanta`, `/portal/documente/luni`, `/portal/facturi`, `/portal/firma`, `/portal/firme`, `/portal/kpi`, `/portal/povesti`, `/portal/recomanda/preview`, `/portal/solicitari`, `/portal/solicitari/contor`, `/tenants/{tenant_id}/client-acces`, `/tenants/{tenant_id}/clienti`, `/tenants/{tenant_id}/clienti/{client_id}`, `/tenants/{tenant_id}/solicitari`*

### `POST /pachete/{tenant_id}/genereaza`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /pachete/{tenant_id}/poveste`

*garda `cere_cabinet` · **fara rol***

- [ ] 

### `POST /pachete/{tenant_id}/trimite`

*garda `cere_rol` · rol:admin_firma*

- [ ] 

### `POST /portal/acces-cont/acces`

*garda `cere_client` · rol:verificat-în-corp · scrie in user_tenants, users*

- [ ] 

### `DELETE /portal/acces-cont/acces/{user_id}`

*garda `cere_client` · **fara rol** · scrie in user_tenants, users*

- [ ] 

### `PUT /portal/acces-cont/email`

*garda `cere_client` · **fara rol** · scrie in users*

- [ ] 

### `POST /portal/recomanda`

*garda `cere_client` · **fara rol***

- [ ] 

### `POST /portal/solicitari`

*garda `cere_client` · **fara rol** · scrie in solicitari_client*

- [ ] 

### `POST /tenants/{tenant_id}/acces-portal`

*garda `cere_rol` · rol:admin_firma,angajat,verificat-în-corp*

- [ ] 

### `POST /tenants/{tenant_id}/client-acces`

*garda `cere_rol` · rol:admin_firma,verificat-în-corp · scrie in user_tenants, users*

- [ ] 

### `DELETE /tenants/{tenant_id}/client-acces/{user_id}`

*garda `cere_rol` · rol:admin_firma · scrie in users*

- [ ] 

### `POST /tenants/{tenant_id}/clienti`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `DELETE /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `PUT /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

- [ ] 

### `POST /tenants/{tenant_id}/solicitari`

*garda `cere_context` · **fara rol** · scrie in solicitari_client*

- [ ] 

