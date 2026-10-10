# -*- coding: utf-8 -*-
"""core/test_p7_uc.py — CONTRACTUL HTTP al valului use-case, confruntat cu starea de dinainte.

Valul a mutat 312 corpuri de ruta si 59 de helperi din `main.py` in stratul use-case, traducand pe
drum fiecare `HTTPException(cod, mesaj)` in `_erori.<Clasa>(mesaj)`. Afirmatia care tine tot valul e
una singura: **codul si mesajul care ies din aplicatie sunt neschimbate.**

Proba nu o crede pe cuvant. Ia `main.py` **de la commitul dinainte de val** (`git show
43fd2197:main.py`), aduna pentru fiecare ruta si fiecare helper multimea perechilor
`(cod HTTP, mesaj)` pe care le ridica, si o compara cu multimea de acum — citita din functia
use-case unde a ajuns corpul, cu clasa tradusa inapoi in cod prin **aceeasi harta** pe care o
foloseste `main._http_din`.

DE CE MERGE ASA, si nu pe text: mesajul se compara ca **ARBORE** (`ast.dump`), nu ca sir. Corpul a
fost dedentat cand a plecat, deci un `"...' \\n '..."` scris pe doua randuri isi schimba sursa fara
sa-si schimbe valoarea; arborele nu se lasa pacalit nici intr-o directie, nici in cealalta.

CE NU ACOPERA: perechile pe care le ridica functii chemate DIN corp (ele se confrunta la randul lor,
ca helperi), si rutele care n-au plecat inca — acelea se compara cu ele insele, deci proba spune
despre ele doar ca n-au fost atinse.
"""
import ast
import copy
import io
import os
import subprocess

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: ultimul commit publicat INAINTE de valul use-case. Nu se schimba: e reperul confruntarii.
BAZA = "43fd2197"
METODE = ("get", "post", "put", "patch", "delete", "head", "options")

#: abaterile acceptate de la „mesaj neschimbat", fiecare cu motivul ei. Orice alta abatere pica.
ABATERI = {
    ('_cere_z_unic', "MESAJ_Z_DUPLICAT % {'numar': numar, 'data': data_ex, 'id': iid, 'cum': 'importata din fisier AMEF' if sursa == 'amef' else 'tastata'}"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('banca_rec_reactiveaza', 'linia nu e ignorata'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('chitanta_stinge', 'documentul nu e in asteptare'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('eu_anunt_confirma', 'anunt inexistent'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('factura_primita_valideaza', 'factura a fost respinsa; nu se poate valida'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('factura_recunoaste', "'factura nu e o ciornă de recunoaștere (stare `%s`): actul e pentru facturile EMISE aduse prin import' % stare"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('factura_trimite_spv', "'Factura are deja o trimitere activa in SPV (%s).' % r.get('stare_existenta')"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('facturi_emite', 'Raspunde la poarta: pleaca marfa acum? (DA descarca gestiunea / NU doar fiscal)'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('horeca_import_amef', "f'fisier AMEF invalid: {e}'"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('nota_tva_incasare', 'sens invalid (incasare/plata)'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('proforma_transforma', "f'deja transformat in factura #{r[1]}'"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('register', 'Termenii și condițiile nu se pot citi acum, deci acordul tău nu s-ar putea consemna. Contul NU a fost creat. Încearcă din nou peste câteva minute.'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('tenant_plan_conturi_adauga', "'Simbolul contului se scrie din cifre, cu separator pentru analitic (`.`, `_`, `-`, `/`) — am primit %r.' % simbol"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ('wc_config', 'N-ai trimis niciun câmp. Cererea asta ar fi golit adresa magazinului și cheile lui, adică ar fi oprit canalul WooCommerce — dacă asta vrei, trimite explicit `url`, `ck` și `cs` goale.'): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.2 (limba textului afișat): același refuz, același cod; mesajul scris corect "
        "(diacritice, fără nume de câmpuri sau de stări interne, fără majuscule de accent)."),
    ("perioada_blocheaza", 'dict(\n                _af.afirmatie(\n                    "neconformitate", "inchidere_perioada",\n                    "Luna %02d/%04d nu se poate închide." % (luna, an),\n                    unde="perioada %02d/%04d" % (luna, an),\n                    regula="o perioadă se închide doar după ce tot ce s-a întâmplat în ea e "\n                           "înregistrat și validat"),\n                cod="PERIOADA_NU_SE_POATE_INCHIDE",\n                motive=motive, ciorne=ciorne, facturi=facturi_desch, blocaj=bl)'): (
        "Decizia Costin 08.10.2026, W2 + W3: același refuz (422, aceeași afirmație „Luna … nu se poate închide.”), cu două chei în "
        "plus — `blocaje` (lista structurată, inclusiv AMORTIZARE_NEINREGISTRATA) și `semnale` (soldul 581 nenul) —, din "
        "`uc_comun.controale_inchidere`, sursa unică pentru poartă și pentru ecranul „Închidere lună”."),
    ("firma_profil_date_salveaza", "r.get('mesaj', 'date invalide')"): (
        "Deciziile Costin 08.10.2026 §6 pct.4 (luna preluării, refuz lângă câmp), generalizat: același refuz (422, același mesaj), "
        "cu câmpul lui în `erori_campuri` când `salveaza_date` îl numește — ecranul Date firmă îl pune lângă câmp (DS cap.6, G10)."),
    ("tenant_amortizare", "Amortizarea lunii e deja generată."): (
        "Decizia Costin 08.10.2026 §6 pct.6 („aceeași regulă ca T1 — înlocuire automată a ciornei nevalidate; ce e validat nu se "
        "atinge”): același cod (400) rămâne numai pentru nota VALIDATĂ, cu numărul ei; ciorna nevalidată sau respinsă se înlocuiește."),
    ("_adresa_e_libera", "EMAIL_EXISTA"): (
        "Testarea ca asistent, comanda Costin 04.10.2026 pct.3 (aceeași clasă): „Există deja un cont cu acest email. "
        "Autentifică-te…” i se spunea celui care își SCHIMBĂ adresa — e deja autentificat. Același cod (400), mesaj "
        "numit (EMAIL_OCUPAT, cu adresa), pus pe câmpul `email`."),
    ("banca_rec_lista", "'stare necunoscută: %r (stările reconcilierii: %s)' % (status, ', '.join(_STARI_REC))"): (
        "Fluxul de factură pe F1, comanda Costin 05.10.2026 pct.8: lista stărilor din mesaj era „noua/potrivita/contata/"
        "ignorata”, iar baza scrie „nou/potrivit/contat/ignorat” — orice filtru întorcea o listă goală. Același cod (422), "
        "același text; lista vine acum din `STARI_EXTRAS` (stările reale), la nivel de modul."),
    ("coada_depune", '{"cod": "CONSTATARI_NECONFIRMATE", "mesaj": ("%d constatare/constatări certe pe firma și perioada asta cer o '
                     'confirmare scrisă înainte de depunere. Depunerea NU e blocată: confirmă-le, cu motiv, și continuă." % '
                     'len(_ramase)), "constatari": _ramase, "actiune": "Retrimite cererea cu `confirmari`: [{amprenta, motiv}] '
                     'pentru fiecare."}'): (
        "Comanda Costin „Retest 08.10” pct.14 („limbaj de programator în ecrane … texte cu majuscule”): același refuz (409, aceeași "
        "cheie CONSTATARI_NECONFIRMATE, aceleași constatări); „NU” devine „nu”, iar `actiune` nu mai arată contabilului corpul "
        "cererii (`confirmari`: [{amprenta, motiv}]), ci ce are de făcut. Gard: `core/test_text_afisat_limbaj.py`."),
    ("vanzare_aur_investitii", "suma invalida"): (
        "G5 (`core/test_g1_cod_mesaj.py`): un input-guard telegrafic primeste constrangerea in "
        "mesaj. Codul ramane 422. Cazul a intrat in domeniul lui G5 odata cu mutarea corpului "
        "rutei din `main.py` in `core/uc_tenants.py` — regula nu s-a slabit, s-a aplicat."),
}


#: Perechi (cod, mesaj) ADAUGATE deliberat DUPA mutarea P7, cu motivul. Simetric cu APELURI_INLOCUITE:
#: garda P7 pazeste ca MUTAREA a fost verbatim; o functionalitate NOUA adaugata dupa mutare (auth) nu
#: e o abatere a mutarii, ci un adaus declarat. Anti-vacuu: `test_ADAUGARILE_declarate_chiar_exista`.
#: Cheia mesajului e ori NUMELE constantei (FARA_DREPT_PREGATIRE), ori chiar literalul (404 pe obiect).
PERECHI_ADAUGATE = {
    ("achizitie_ic", "str(e)"): (
        "Deficiența 224 generalizată (10.10.2026): refuzul motivat al creării facturii (`creeaza_factura` ridică `ValueError` — cod partener, serie, cotă) ieșea 500; tradus în 422, ca la `factura_creeaza`. Gardul: `test_refuz_generator_422::test_refuzul_emiterii_nu_ajunge_la_contabil_ca_500`."),
    ("achizitie_necorporala", "str(e)"): (
        "Deficiența 224 generalizată (10.10.2026): refuzul motivat al creării facturii (`creeaza_factura` ridică `ValueError` — cod partener, serie, cotă) ieșea 500; tradus în 422, ca la `factura_creeaza`. Gardul: `test_refuz_generator_422::test_refuzul_emiterii_nu_ajunge_la_contabil_ca_500`."),
    ("achizitie_neinregistrat", "str(e)"): (
        "Deficiența 224 generalizată (10.10.2026): refuzul motivat al creării facturii (`creeaza_factura` ridică `ValueError` — cod partener, serie, cotă) ieșea 500; tradus în 422, ca la `factura_creeaza`. Gardul: `test_refuz_generator_422::test_refuzul_emiterii_nu_ajunge_la_contabil_ca_500`."),
    ("tenant_plan_conturi_adauga", "'Analiticul se scrie după contul sintetic, cu cifre după separator (de exemplu 4111.01) — s-a primit %r.' % simbol"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.13 (decizia O12, prinsă la proba din ecran): „4111.” — un separator fără analitic "
        "după el — intra în plan. Refuz numit (422): analiticul = sinteticul + separator + cifre."),
    ("tenant_plan_conturi_adauga", "'Simbolul contului are cel mult 10 caractere — s-a primit %r (%d).' % (simbol, len(simbol))"): (
        "Comanda Costin 09.10.2026, „Retest 2” pct.13: coloana `plan_conturi.simbol` e varchar(10); un simbol mai lung cădea în driver "
        "(500). Refuz numit (422), cu lungimea."),
    ("coada_adauga", "_blocaj"): (
        "Deciziile Costin 08.10.2026, U1 (+ completarea: D300, D394, D390) și V1 (D406): „«Trimite în coadă» e blocat” când TVA-ul "
        "D300 nu se potrivește cu rulajele 4427 / 4426 (TVA_DIFERA_DE_BALANTA), respectiv când totalurile GeneralLedgerEntries nu sunt "
        "rulajele balanței (D406_DIFERA_DE_BALANTA). Refuz 422 structurat, înaintea validatorului DUK. [§6 pct.7, R36] „compară "
        "validat cu validat; dacă există ciorne în lună, dau doar avertisment, nu blocaj” — cele două refuzuri au devenit unul "
        "(`_blocaj`, din `decizie_poarta`), ridicat numai fără ciorne în perioadă."),
    ("factura_contabilizeaza", "_nl.detaliu_refuz(e)"): (
        "Decizia Costin 08.10.2026, pct.2: „la contarea facturii se propune legarea cu NIR-ul nelegat de la același furnizor "
        "(preselecție permisă — dedusă din date, vizibilă, modificabilă). Dacă contabilul nu leagă, confirmă explicit «altă "
        "livrare»; nu se blochează.” Factura de marfă (371, global-valoric) cu NIR „fără factură” nelegat la același furnizor se "
        "refuză (422) STRUCTURAT — `cod` NIR_DE_LEGAT / NIR_NELEGABIL / COST_DIFERIT_DE_FACTURA, candidații, propunerea — până "
        "când omul alege NIR-ul sau „altă livrare”; înainte se conta tăcut și 371 se încărca de două ori."),
    ("factura_primita_valideaza", "_nl.detaliu_refuz(e)"): (
        "Decizia Costin 08.10.2026, pct.2 (aceeași ca la `factura_contabilizeaza`), pe calea SPV: alegerea NIR-ului se cere ÎNAINTE "
        "de validare — refuzul (422, structurat) anulează tot actul, ca factura să nu rămână validată fără notă."),
    ("chitanta_emite", 'refuz_spre_ecran(MESAJ_SERIE_CHITANTA_LIPSA, COD_SERIE_CHITANTA_LIPSA, "date_firma", "OMFP 2634/2015 anexa 1 pct.24")'): (
        "Comanda Costin 07.10.2026 („Deciziile 07.10”, pct.5): „Seria chitanței: cerută la prima folosire, ca seria facturii; fără "
        "«CH» din oficiu.” Prima chitanță a firmei fără serie se refuză (400), STRUCTURAT cu ținta `ecran` (butonul spre Date "
        "firmă) — înainte se emitea cu „CH”, pe care nu-l alesese nimeni (OMFP 2634/2015 anexa 1 pct.24: seria „stabilit(ă) de entitate”)."),
    ("coada_adauga", '_refuz_duk("ERORI_DUK", _rez, _sev)'): (
        "Comanda Costin 07.10.2026, C3: „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.” Eroarea DUK refuză intrarea (422) FĂRĂ portiță — înainte `motiv_trecere` trecea și peste erori." ),
    ("coada_adauga", '_refuz_duk("ATENTIONARI_NECONFIRMATE", _rez, _sev)'): (
        "Comanda Costin 07.10.2026, C3: „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.” Atenționarea neconfirmată se refuză (422) cerând confirmarea scrisă; cu ea, intră." ),
    ("stocuri_descarcare", 'refuz_spre_ecran(rez["eroare"], rez.get("cod"), rez["ecran"], rez.get("regula"))'): (
        "Lotul 07.10 pct.2 (comanda Costin 06.10.2026): „orice mesaj care trimite în alt ecran are buton direct spre el”. Refuzul "
        "metodei de stoc nedeclarate (Date firmă) rămâne același refuz (400, același mesaj), dar STRUCTURAT cu ținta `ecran`, ca "
        "ecranul să pună butonul spre Date firmă; un refuz fără țintă rămâne frază, ca înainte."),
    ("stocuri_adauga", 'refuz_spre_ecran(rez["eroare"], rez.get("cod"), rez["ecran"], None)'): (
        "Lotul 07.10 B, C10 (decizia Costin 07.10.2026): „evaluarea stocului … e setare a firmei și se aplică identic la intrări și "
        "ieșiri … Dacă setarea firmei nu spune evaluarea, se cere la prima folosire, ca seria și metoda.” NIR-ul refuză (400) când "
        "metoda de stoc nu e declarată, STRUCTURAT cu ținta `ecran` (butonul spre Date firmă), ca la descărcarea lunară."),
    ("coada_continut", "Nota nu mai există în jurnal (a fost ștearsă)."): (
        "Comanda Costin 06.10.2026 (răspunsul la §6, pct.1): coada poartă și NOTE; conținutul unui element-notă se citește din "
        "jurnalul firmei, iar nota ștearsă între timp se refuză cu motivul numit (404), nu cu un conținut gol."),
    ("pachet_poveste_set", "MESAJ_APROBARE_PE_RUTA_EI"): (
        "Comanda Costin 05.10.2026 pct.2: aprobarea poveștii lunii cere «Poate valida» și are ruta ei "
        "(`/pachete/{tenant_id}/poveste/aproba`); ruta de ciornă («Poate pregăti») refuză `status=aprobat` cu motivul numit "
        "(400), altfel garda pe ciornă ar fi lăsat aprobarea să treacă pe pregătire."),
    ("coada_adauga", "FARA_DREPT_PREGATIRE"): (
        "B4 (17.09.2026, audit A1): a pune o declaratie in coada e actul de PREGATIRE — cere "
        "`poate_pregati`. In BAZA flagul aparea doar la setare, nu la folosire; orice angajat sub "
        "`cere_cabinet` genera si punea in coada. Poarta e acum pe ACTIUNE, nu doar in profil."),
    ("eu_competente_set", "DOAR_ADMIN_CABINET"): (
        "B2 (17.09.2026, audit A1): `poate_valida`/`poate_depune` sunt privilegii de CONTROL INTERN "
        "(patru-ochi) — le acorda administratorul prin `/asistenti/{uid}/permisiuni`, nu si le acorda "
        "fiecare singur. In BAZA orice angajat isi scria toate trei flagurile pe propriul rand si "
        "apoi aproba orice. Ruta e rezervata acum admin_firma/superadmin."),
    ("coada_depune", "Element de coadă negăsit (sau alt cabinet)."): (
        "B1 (17.09.2026, audit A1): apartenenta pe OBIECT verificata devreme — elementul e al "
        "cabinetului apelant? Altfel 404, fara sa atinga `declaratii_depuse` al altei firme. In BAZA "
        "aproba/respinge/depune lucrau pe orice `coada_id`, doar cu dreptul apelantului verificat."),
    ("horeca_raport_z", "MESAJ_Z_FARA_BONURI"): (
        "D394 op2 Î1, decizia Costin B (02.10.2026): ruta tastată a raportului Z cere numărul de bonuri fiscale "
        "(OPANAF 2194/2025, anexa D394 lit.G, pct.14) — fără el D394 n-ar avea ce declara pe lună; refuz de contabil "
        "(400), nu violarea CHECK-ului din bază."),
    ("facturi_emite", "MESAJ_FACTURA_BON_STOC"): (
        "Decizia Costin A (02.10.2026): factura emisă pe baza bonului fiscal nu e o vânzare nouă — marfa a ieșit cu bonul "
        "(raportul Z), deci a doua descărcare de gestiune se refuză (422), cu ieșirea numită („NU — doar fiscal”)."),
    ("facturi_emite", "_cs.detaliu_metoda_stoc(e)"): (
        "Lotul 06.10.2026, comanda Costin §6.3: metoda de stoc explicită — factura cu marfă la metoda nedeclarată (sau ieșire pe "
        "articol la global-valoric) se refuză STRUCTURAT (422 spre Date firmă), factura păstrată pe ecran."),
    ("facturi_emite", "facturi_api.detaliu_serie_lipsa(e)"): (
        "Lotul 06.10.2026, comanda Costin §6.1: seria obligatorie la emitere (CF art.319 alin.(20) lit.a). Refuz STRUCTURAT "
        "(422: cod SERIE_LIPSA + temei + câmp), ca ecranul să seteze seria peste factură și emiterea să continue."),
    ("facturi_emite", "_cs.detaliu(e)"): (
        "Lot 19 defectul 12, decizia Costin (03.10.2026): factura unei societăți fără forma juridică / capitalul social "
        "din Date firmă se refuză la emitere (Legea 31/1990 art.74 alin.(3)), STRUCTURAT (422): ce lipsește, temeiul, "
        "ecranul spre care trimite — caseta păstrează factura tastată."),
    ("achizitie_taxare_inversa", "str(e)"): (
        "Lot 19 defectul 13 (03.10.2026): bifa „furnizor plătitor de TVA” se citește prin `_uc_comun.bifa`; o valoare care "
        "nu e da/nu e refuzată (422), nu ghicită — înainte orice șir era „plătitor”."),
    ("centre_cost_activ", "str(e)"): (
        "Lot 19 defectul 13 (03.10.2026): `activ` se citește prin `_uc_comun.bifa`; „false” trimis ca text nu mai "
        "activează centrul (bool(\"false\") era True) — o valoare care nu e da/nu e refuzată (422)."),
    ("salariat_actualizeaza", "{'mesaj': str(e), 'erori_campuri': _ec, 'cod': e.cod, 'existent': e.existent}"): (
        "Salariul în timp, decizia Costin (04.10.2026): schimbarea salariului la o dată deja în istoric e refuzată NUMIT "
        "(422, cod SALARIU_DATA_OCUPATA + intrarea existentă), nu rescrisă tăcut prin UPSERT; ecranul oferă înlocuirea "
        "explicită (`inlocuieste`)."),
    ("chitanta_emite", "_amef.detaliu(e)"): (
        "D394 Î2, deciziile Costin (03.10.2026): chitanța de VÂNZARE fără factură se emite doar la firma exceptată de la "
        "AMEF (OUG 28/1999 art.1 alin.(1) / art.2), cu cota obligatorie și permisă la data ei — refuz STRUCTURAT (400: "
        "cod + temei). Chitanța de creanță fără factură (firmă neexceptată, fără cotă) rămâne neatinsă."),
    ("chitanta_emite", "'Data chitanței: %r nu e o dată din calendar. Se așteaptă forma AAAA-LL-ZZ.' % (c.data,)"): (
        "D394 Î2 (03.10.2026): cotele permise depind de data chitanței, deci data se citește înainte — o zi care nu "
        "există în calendar e refuz de contabil (400), cum o refuza deja `casa_api.adauga` mai târziu."),
    ("tenant_creeaza", "{'mesaj': EMAIL_INVALID, 'erori_campuri': [{'camp': 'email_client', 'mesaj': EMAIL_INVALID}]}"): (
        "Testarea ca asistent, comanda Costin 04.10.2026 pct.3: emailul clientului se judecă ÎNAINTE de crearea firmei — "
        "o adresă fără formă de email se refuză pe câmpul `email_client` (400), ca la `client-acces`; firma nu se mai "
        "creează pentru ca abia apoi invitația să cadă."),
    ("facturi_numerotare_get", "'Data emiterii nu e o dată calendaristică (aaaa-ll-zz): %r.' % la_data"): (
        "Fluxul de factură pe F1, comanda Costin 05.10.2026 pct.3: cotele permise se citesc la DATA FACTURII din formular "
        "(`?data=`), nu „azi” (interdicția 3); o zi care nu există în calendar e refuz de contabil (422), ca la chitanțe."),
    ("horeca_import_amef", "MESAJ_AMEF_FARA_BONURI"): (
        "D394 op2 Î1, decizia Costin B (02.10.2026): un fișier AMEF fără `nrB` nu poate scrie rândul `rapoarte_z_amef` "
        "(nr_bonuri > 0); refuz numit (422), nu un rând care ar opri D394 mai târziu."),
}


#: [lot 19 defectul 13, 03.10.2026] Functiile in care `bool(corp.get(x))` a devenit `_uc_comun.bifa(corp, x)`:
#: ecranul trimite selecturile ca TEXT („true”/„false”), iar `bool("false")` e True — imputabil „Nu” devenea imputabil,
#: furnizor neplatitor -> taxare inversa, agricultor neinscris -> compensare deductibila. (credit pe apel, extra, motiv)
_BOOL_GET = {"bool": 1, "get": 1}
BIFA_INLOCUIRI = {
    "centre_cost_activ": (_BOOL_GET, {}, "activ"),
    "export_extracomunitar": (_BOOL_GET, {}, "dovada_export"),
    "import_extracomunitar": (_BOOL_GET, {}, "certificat_amanare"),
    "nota_asociati": ({"bool": 1, "get": 1}, {}, "interimar: select „0”/„1”; [07.10.2026, „Cele 33 de chei”] DA/NU nou în ecran („true”/„false” ca TEXT) citit acum prin `bifa`, nu prin `corp.get`: cu_plata"),
    "nota_credit": ({"get": 1}, {}, "[07.10.2026, „Cele 33 de chei”] DA/NU nou în ecran („true”/„false” ca TEXT) citit acum prin `bifa`, nu prin `corp.get`: dobanda_angajata"),
    "nota_sponsorizare_ep": ({"get": 1}, {}, "[07.10.2026, „Cele 33 de chei”] DA/NU nou în ecran („true”/„false” ca TEXT) citit acum prin `bifa`, nu prin `corp.get`: beneficiar_in_registru"),
    "vanzare_aur_investitii": ({"get": 1}, {}, "[07.10.2026, „Cele 33 de chei”] DA/NU nou în ecran („true”/„false” ca TEXT) citit acum prin `bifa`, nu prin `corp.get`: optiune_taxare"),
    "vanzare_marja_turism": ({"get": 3}, {}, "[07.10.2026, „Cele 33 de chei”] DA/NU nou în ecran („true”/„false” ca TEXT) citit acum prin `bifa`, nu prin `corp.get`: intermediar, optiune_normal, tva_inclus"),
    "nota_inventariere": (_BOOL_GET, {}, "imputabil, asigurat_sau_distrus, destinatie_cd"),
    "nota_obiect_inventar": (_BOOL_GET, {}, "durata_sub_1_an"),
    "nota_perisabilitati": (_BOOL_GET, {}, "degradare_dovedita_distrusa"),
    "nota_provizion_ep": (_BOOL_GET, {}, "garantata, afiliata, faliment"),
    "vanzare_ic": ({"bool": 1}, {}, "dovada_transport"),
    "achizitie_taxare_inversa": ({"get": 1, "strip": 1, "lower": 1}, {"get": 1},
                                 "furnizor_platitor_tva; al doilea `corp.get` (sirul trimis la se_aplica) inlocuit "
                                 "de verdictul ANAF/bifa `_tert_pl`"),
}


#: [07.10.2026] Același refuz (același mesaj), cu UN cod HTTP ÎN PLUS — `(funcție, mesaj): (codul adăugat, motivul)`. Mai strâns
#: decât ABATERI (care acceptă alt mesaj sub același cod) și decât PERECHI_ADAUGATE (care acceptă o pereche nouă oricare ar fi
#: codul): se scutește EXACT perechea veche `(coduri, m)` față de cea nouă `(coduri | {cod}, m)`, nimic altceva.
#: Anti-vacuu: `test_CODURILE_adaugate_chiar_sunt_in_cod`.
CODURI_ADAUGATE = {
    ("coada_aproba", 'r.get("mesaj", cod)'): (422, "Comanda Costin 07.10.2026, C3: „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.” Aprobarea refuză acum cu 422 (nu 404) un element cu ERORI_DUK sau cu "
                                                   "ATENTIONARI_NECONFIRMATE — e o stare a datelor, nu o lipsă."),
    ("coada_depune", 'r.get("mesaj", cod)'): (422, "Comanda Costin 07.10.2026, C3: „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.” Depunerea refuză acum cu 422 (nu 404) un element cu ERORI_DUK sau cu "
                                                   "ATENTIONARI_NECONFIRMATE — e o stare a datelor, nu o lipsă."),
}


#: Refuzuri MUTATE într-un ajutor comun, cu motivul: aceeași stare, același cod HTTP, ridicate acum de ajutorul pe
#: care funcția îl cheamă (o singură formulare pentru „adresa invitată are deja cont”, în loc de trei).
_MOTIV_EMAIL_OCUPAT = (
    "Testarea ca asistent, comanda Costin 04.10.2026 pct.3: „adresa aparține deja unui cont cu alt rol” — refuz NUMIT, "
    "pe câmp, dintr-o singură funcție (`uc_comun._refuza_email_ocupat`). Până azi trei rute ridicau aceeași stare cu "
    "„Autentifică-te…”, scris pentru proprietarul adresei, nu pentru cel care invită. Codul HTTP rămâne același.")
PERECHI_MUTATE_IN_AJUTOR = {
    ("asistent_creeaza", "EMAIL_EXISTA"): ("_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("client_acces_creeaza", "EMAIL_EXISTA"): ("_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("portal_adauga_acces", "EMAIL_EXISTA"): ("_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
}


def test_MUTARILE_in_ajutor_chiar_cheama_ajutorul():
    """Anti-vacuu: o mutare declarată fără apelul ajutorului ar scuza un refuz PIERDUT."""
    import ast as _ast
    from core import scan_sql_efectiv as _ef
    for (fn_nume, _mesaj), (ajutor, motiv) in PERECHI_MUTATE_IN_AJUTOR.items():
        assert len(motiv) > 80
        _cale, _nod = _ef.functia(fn_nume)
        chemate = {x.func.attr for x in _ast.walk(_nod) if isinstance(x, _ast.Call) and isinstance(x.func, _ast.Attribute)}
        assert ajutor in chemate, "%s: mutarea declarată în %s nu e în cod" % (fn_nume, ajutor)


#: Apeluri INLOCUITE deliberat, cu motivul. Nu sunt pierderi: numele s-a schimbat, iar inlocuitorul
#: face STRICT MAI MULT decat cel vechi. Orice alt apel dispărut pica in continuare.
APELURI_INLOCUITE = {
    ("tenant_mijloace_fixe", "today"): (
        "azi_ro",
        "Comanda Costin 09.10.2026, „Retest 2” pct.5 („calculul merge până la ultima lună încheiată, aceeași regulă ca la închiderea "
        "lunii”): ziua României (`azi_ro`), ca `inchidere_luna.ultima_zi_incheiata`, nu ziua serverului."),
    ("bon_aproba", "nota_bon_validata"): (
        "nota_bon_ciorna",
        "Decizia Costin 08.10.2026 §6 pct.7 (R36: „evidența = ce a validat un om”): nota bonului aprobat intră CIORNĂ — aceeași "
        "scriere, alt status; validarea e actul separat."),
    ("horeca_raport_z", "nota_horeca_z_validata"): (
        "nota_horeca_z_ciorna",
        "Decizia Costin 08.10.2026 §6 pct.7 (R36): raportul Z tastat intră CIORNĂ la ambele metode de stoc — cele două apeluri "
        "(ciornă la cantitativ-valoric, validată în rest) devin unul."),
    ("tenant_amortizare", "nota_amortizare_validata"): (
        "nota_amortizare_ciorna",
        "Deciziile Costin 08.10.2026 §6 pct.6 + pct.7 (R36 + clasa T1, retest 08.10 pct.1): nota de amortizare intră CIORNĂ și se înlocuiește cât e "
        "nevalidată."),
    ("salarii_contare_scrie", "_date"): (
        "ultima_zi_a_lunii",
        "Lotul 07.10 pct.7 (comanda Costin 06.10.2026: „dacă nu are [temei], data e ultima zi a lunii”): data notei de salarii "
        "nu mai e `_date(an, luna, 28)`, ci `_uc_comun.ultima_zi_a_lunii(an, luna)` — aceeași dată a lunii, ziua ei ultimă."),
    ("tenant_amortizare", "_date"): (
        "ultima_zi_a_lunii",
        "Lotul 07.10 pct.7: nota de amortizare și poarta lunii închise nu mai iau ziua 28 (`_date(an, luna, 1).replace(day=28)`), "
        "ci ultima zi a lunii (`_uc_comun.ultima_zi_a_lunii`)."),
    ("tenant_amortizare", "replace"): (
        "ultima_zi_a_lunii",
        "Lotul 07.10 pct.7: `.replace(day=28)` (de două ori) înlocuit de `ultima_zi_a_lunii` — aceeași dată, ultima zi."),
    ("tenant_stat_plata", "stat_plata"): (
        "stat_final",
        "Comanda Costin 06.10.2026 (răspunsul la §6, pct.2): ecranul statului arată indemnizația CM cu reținerile DECLARATE "
        "în D112 — `stat_final` cheamă `stat_plata` și aplică peste ea reținerile declarate; apelul vechi e în interiorul celui nou."),
    ("produse_potriveste", "potriveste"): (
        "propunere_pentru_linie",
        "Fluxul de factură pe F1, comanda Costin 05.10.2026 pct.9: potrivirea pe linie caută întâi produsul în nomenclatorul "
        "firmei (cota, UM, preț) și abia apoi cheamă `potriveste` (AI) — apelul vechi n-a dispărut, e în interiorul celui nou."),
    ("vanzare_ic", "nota_facturi_ciorna"): (
        "nota_facturi_cu_factura",
        "R187 (16.09.2026, decizia lui Costin): livrarea intracomunitara produce acum FACTURA, iar "
        "nota ramane CIORNA — amandoua helperele scriu `status='ciorna'` — dar e LEGATA de factura "
        "prin `factura_id`. Deci apelul n-a dispărut: a fost inlocuit cu unul care scrie tot ce "
        "scria cel vechi, PLUS legatura. Fara factura, operatiunea nu putea ajunge nici in D300 "
        "rd.1/rd.3, nici in D390."),
    ("asistent_creeaza", "id_si_activ_dupa_email"): (
        "contul_dupa_email",
        "Testarea ca asistent (04.10.2026, pct.3): refuzul trebuie să știe ROLUL contului existent (alt rol vs. asistent "
        "existent), deci citirea întoarce și rolul. Aceeași căutare după adresă, cu o coloană în plus."),
    ("asistent_creeaza", "creeaza_cont_de_client"): (
        "creeaza_cont_asistent",
        "Testarea ca asistent (04.10.2026): funcția veche se numea „de client” și avea parametrii numiți greșit (`rol` "
        "primea cabinetul, `accounting_firm_id` bifa) — INSERT-ul ieșea corect doar din poziție. Înlocuitorul scrie "
        "aceleași coloane, cu numele lor, plus „Poate pregăti” (decizia Costin: munca curentă o face orice asistent)."),
    ("asistent_creeaza", "HTTPException"): (
        "_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("client_acces_creeaza", "HTTPException"): (
        "_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("portal_adauga_acces", "HTTPException"): (
        "_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("portal_revoca_acces", "dezactiveaza_contul"): (
        "dezactiveaza_contul_client",
        "B3 (17.09.2026, audit A1): portalul dezactiva un cont NEscoped — un client titular stingea "
        "orice user fara randuri in `user_tenants` (un angajat neatribuit, un admin ale carui firme "
        "fusesera scoase, superadminul). Inlocuitorul filtreaza pe `rol='client'`: portalul stinge "
        "DOAR conturi de client. Face strict mai putin daunator, acoperind exact clasa vulnerabila."),
}


#: [08.10.2026] Corpuri EXTRASE într-un ajutor, cu motivul: funcția cheamă acum ajutorul, iar apelurile vechi le face AJUTORUL.
#: Creditul NU se dă orb: se numără apelurile din corpul ajutorului (plus funcțiile modulului lui pe care le cheamă direct), deci
#: un apel care nu există nici acolo rămâne pierdut. Anti-vacuu: `test_EXTRAGERILE_declarate_chiar_cheama_ajutorul`.
APELURI_EXTRASE_IN_AJUTOR = {
    "perioada_blocheaza": (("core/uc_comun.py", "controale_inchidere"), (
        "Decizia Costin 08.10.2026, W2 + W3: „Închiderea lunii e blocată dacă amortizarea lunii nu e înregistrată” și „controalele de "
        "închidere semnalează soldul 581 nenul”. Controalele (ciorne, facturi neîncheiate, e-Facturi, amortizare, 581) trăiesc într-o "
        "singură funcție, `uc_comun.controale_inchidere`, chemată și de poarta închiderii și de ecranul „Închidere lună”.")),
    "declaratie_valideaza": (("core/uc_declaratii.py", "campuri_rezultat"), (
        "Comanda Costin „Retest 08.10” pct.16: „D406: caseta «Rezumat» nu se vede” — `sinteza` intrase numai în răspunsul "
        "generării, iar ecranul cheamă validarea. Câmpurile rezultatului (avertismente, note_rezultat, sinteza, operatiuni, "
        "componente) se asamblează acum într-o singură funcție, `uc_declaratii.campuri_rezultat`, chemată de amândouă rutele.")),
    "declaratie_genereaza": (("core/uc_declaratii.py", "campuri_rezultat"), (
        "Comanda Costin „Retest 08.10” pct.16: „D406: caseta «Rezumat» nu se vede” — `sinteza` intrase numai în răspunsul "
        "generării, iar ecranul cheamă validarea. Câmpurile rezultatului (avertismente, note_rezultat, sinteza, operatiuni, "
        "componente) se asamblează acum într-o singură funcție, `uc_declaratii.campuri_rezultat`, chemată de amândouă rutele.")),
    "_verificari_contabile": (("core/uc_comun.py", "_tva_balanta_sau_nu_se_aplica"), (
        "Deficiența 211 (retestul Costin 09.10.2026): „Control fiscal, firmă neplătitoare de TVA: «TVA vs sold balanță» cu bulină "
        "verde; trebuie «nu se aplică»”. Coerența brută 4427/4426 se calculează acum într-o funcție care întâi citește dacă firma e "
        "plătitoare de TVA (`_tva_balanta_sau_nu_se_aplica`) — aceleași apeluri `coerenta_tva` și `get` pe balanță, mutate acolo.")),
    "_bon_imagine_cale": (("core/common.py", "dir_bonuri"), (
        "Deficiența 9 + comanda Costin 09.10.2026 pct.7 („director de bonuri separat”): calea pozelor bonurilor era scrisă de patru ori "
        "(`os.path.expanduser(\"~/iconta_date/bonuri\")`); acum stă într-un singur loc, `common.dir_bonuri`, care o mută pe mediul "
        "de test (`ICONTA_BON_DIR`) și refuză mutarea pe producție. Același `expanduser`, mutat acolo.")),
    "portal_bon": (("core/common.py", "dir_bonuri"), (
        "Deficiența 9 + comanda Costin 09.10.2026 pct.7 („director de bonuri separat”): calea pozelor bonurilor era scrisă de patru ori "
        "(`os.path.expanduser(\"~/iconta_date/bonuri\")`); acum stă într-un singur loc, `common.dir_bonuri`, care o mută pe mediul "
        "de test (`ICONTA_BON_DIR`) și refuză mutarea pe producție. Același `expanduser`, mutat acolo.")),
    "portal_bon_sterge": (("core/common.py", "dir_bonuri"), (
        "Deficiența 9 + comanda Costin 09.10.2026 pct.7 („director de bonuri separat”): calea pozelor bonurilor era scrisă de patru ori "
        "(`os.path.expanduser(\"~/iconta_date/bonuri\")`); acum stă într-un singur loc, `common.dir_bonuri`, care o mută pe mediul "
        "de test (`ICONTA_BON_DIR`) și refuză mutarea pe producție. Același `expanduser`, mutat acolo.")),
    "tenant_mijloace_fixe": (("core/mf_registru.py", "registru"), (
        "Decizia Costin 08.10.2026, W2: „registrul afișează amortizarea înregistrată în contabilitate, iar separat diferența față de "
        "calculul teoretic, cu lunile neînregistrate … durata, codul din catalog și planul lunar”. Rândul registrului se construiește "
        "în `mf_registru.registru` (același calcul teoretic, `amortizat_la_data`, plus cel înregistrat).")),
}


def _apeluri_ajutor(cale, nume):
    """Apelurile din corpul ajutorului + din funcțiile aceluiași modul pe care le cheamă direct (un nivel)."""
    arb = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
    fn = {n.name: n for n in arb.body if isinstance(n, ast.FunctionDef)}
    c = {}

    def _numara(nod):
        for x in ast.walk(nod):
            if isinstance(x, ast.Call):
                f = x.func
                n = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if n:
                    c[n] = c.get(n, 0) + 1
    _numara(fn[nume])
    for x in [k for k in list(c) if k in fn and k != nume]:
        _numara(fn[x])
    return c


def test_EXTRAGERILE_declarate_chiar_cheama_ajutorul():
    """Anti-vacuu: o extragere declarată fără apelul ajutorului (sau cu un ajutor inexistent) ar scuza apeluri pierdute."""
    import ast as _ast
    from core import scan_sql_efectiv as _ef
    for fn_nume, ((cale, ajutor), motiv) in APELURI_EXTRASE_IN_AJUTOR.items():
        assert len(motiv) > 80
        assert _apeluri_ajutor(cale, ajutor), "%s: ajutorul %s nu cheamă nimic" % (fn_nume, ajutor)
        _cale, _nod = _ef.functia(fn_nume)
        # ajutorul poate fi în alt modul (`_uc_comun.controale_inchidere(...)`) sau în același (`campuri_rezultat(...)`, retest 08.10)
        chemate = {x.func.attr if isinstance(x.func, _ast.Attribute) else x.func.id for x in _ast.walk(_nod)
                   if isinstance(x, _ast.Call) and isinstance(x.func, (_ast.Attribute, _ast.Name))}
        assert ajutor in chemate, "%s: extragerea declarată în %s nu e în cod" % (fn_nume, ajutor)


def test_INLOCUIRILE_declarate_chiar_exista():
    """ANTI-VACUU pe tabelul de mai sus: o inlocuire declarata care nu e in cod ar scuza o pierdere
    ADEVARATA. Se cere ca inlocuitorul sa fie chemat de chiar functia numita."""
    import ast as _ast
    from core import scan_sql_efectiv as _ef
    for (fn_nume, vechi), (nou, motiv) in APELURI_INLOCUITE.items():
        assert len(motiv) > 80, "%s: motivul inlocuirii e prea scurt ca sa fie util" % fn_nume
        _cale, _nod = _ef.functia(fn_nume)
        chemate = {x.func.attr for x in _ast.walk(_nod)
                   if isinstance(x, _ast.Call) and isinstance(x.func, _ast.Attribute)}
        assert nou in chemate, (
            "%s: inlocuirea declarata (%s -> %s) NU e in cod — tabelul ar scuza o pierdere reala"
            % (fn_nume, vechi, nou))
        assert vechi not in chemate, (
            "%s: apelul vechi (%s) mai e chemat, deci nu s-a inlocuit nimic" % (fn_nume, vechi))


def test_ADAUGARILE_declarate_chiar_exista():
    """ANTI-VACUU pe PERECHI_ADAUGATE: o adaugare declarata care nu e in cod ar scuza o schimbare de
    contract nedeclarata. Se cere ca perechea (cod, mesaj) declarata sa fie chiar ridicata de functia
    numita, in stratul use-case."""
    harta = _harta_cod()
    uc_dupa_nume = {nume: nod for (_mod, nume), nod in _module_uc().items()}
    for (fn_nume, msg_repr), motiv in PERECHI_ADAUGATE.items():
        assert len(motiv) > 80, "%s: motivul adaugarii e prea scurt ca sa fie util" % fn_nume
        corp = uc_dupa_nume.get(fn_nume)
        assert corp is not None, (
            "%s: functia declarata nu exista in stratul use-case — adaugarea ar scuza o schimbare "
            "fantoma" % fn_nume)
        forme = _forme_mesaj(msg_repr)
        mesaje = {p[1] for p in perechi_noi(corp, harta)}
        assert forme & mesaje, (
            "%s: adaugarea declarata (%s) NU e in cod — tabelul ar scuza o schimbare de contract reala"
            % (fn_nume, msg_repr))


def test_CODURILE_adaugate_chiar_sunt_in_cod():
    """ANTI-VACUU pe CODURI_ADAUGATE: codul declarat trebuie să fie chiar printre codurile perechii cu acel mesaj, în funcția
    numită. MUTAȚIE: 422 scos din maparea lui `coada_depune` -> pică (scutirea ar acoperi o schimbare care nu există)."""
    harta = _harta_cod()
    uc_dupa_nume = {nume: nod for (_mod, nume), nod in _module_uc().items()}
    for (fn_nume, msg_repr), (cod, motiv) in CODURI_ADAUGATE.items():
        assert len(motiv) > 80, "%s: motivul e prea scurt ca să fie util" % fn_nume
        corp = uc_dupa_nume.get(fn_nume)
        assert corp is not None, "%s: funcția declarată nu există în stratul use-case" % fn_nume
        forme = _forme_mesaj(msg_repr)
        coduri = [p[0] for p in perechi_noi(corp, harta) if p[1] in forme]
        assert coduri and all(cod in c for c in coduri), "%s: codul %s declarat adăugat NU e în cod: %s" % (fn_nume, cod, coduri)


def _sursa_veche():
    r = subprocess.run(["git", "show", "%s:main.py" % BAZA], cwd=RAD,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("commitul de baza %s nu e in arborele asta: %s" % (BAZA, r.stderr[:120]))
    return r.stdout


def _harta_cod():
    """clasa de domeniu -> cod HTTP, CITITA din stratul HTTP, nu rescrisa aici."""
    import main
    return {c.__name__: cod for c, cod in main._COD_EROARE}


def _intregi(arb):
    """Numele care ÎNSEAMNĂ un cod HTTP: constante întregi de modul, scrise aici sau importate.

    Șase refuzuri scriu codul ca nume (`COD_FARA_ACCES_TENANT`), importat din `core.mesaje`. Citit
    doar din fișier, el ar rămâne necunoscut, iar comparația ar raporta o „schimbare" între un cod
    nerezolvat și unul rezolvat — despre aceeași linie."""
    out = {}
    for n in arb.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant) \
                and isinstance(n.value.value, int) and not isinstance(n.value.value, bool):
            out[n.targets[0].id] = n.value.value
        elif isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
            try:
                import importlib
                mod = importlib.import_module(n.module)
            except Exception:
                continue
            for a in n.names:
                v = getattr(mod, a.name, None)
                if isinstance(v, int) and not isinstance(v, bool):
                    out[a.asname or a.name] = v
    return out


def _e_ruta(n):
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    for d in n.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Attribute) and f.attr in METODE:
            return True
    return False


class _FaraCalificare(ast.NodeTransformer):
    """`_uc_comun._mesaj_intrare(e)` și `_mesaj_intrare(e)` sunt ACELAȘI apel.

    Învelișul din `main.py` cheamă funcția din `core/uc_comun.py` și-i întoarce rezultatul neatins,
    deci mesajul produs e identic. Ce s-a schimbat e unde locuiește funcția, nu ce spune. Calificarea
    se scoate înainte de comparație — altfel proba ar raporta 40 de „schimbări de contract" care
    sunt, toate, același nume scris cu adresa lui."""

    #: ce citea ruta din obiectul HTTP → cum se numește valoarea aceea în use-case. Învelișul o
    #: citește și o pasează, deci e ACEEAȘI valoare, sub alt nume.
    DIN_FISIER = {"filename": "nume_fisier", "content_type": "tip_continut"}

    def visit_Attribute(self, nod):
        self.generic_visit(nod)
        if isinstance(nod.value, ast.Name) and nod.value.id in ("_uc_comun", "_erori"):
            return ast.copy_location(ast.Name(id=nod.attr, ctx=ast.Load()), nod)
        if nod.attr in self.DIN_FISIER and isinstance(nod.value, ast.Name):
            return ast.copy_location(ast.Name(id=self.DIN_FISIER[nod.attr], ctx=ast.Load()), nod)
        return nod

    def visit_Call(self, nod):
        self.generic_visit(nod)
        if isinstance(nod.func, ast.Name) and nod.func.id == "_octetii":
            return ast.copy_location(ast.Name(id="continut", ctx=ast.Load()), nod)
        return nod


def _dump(nod):
    if nod is None:
        return ""
    return ast.dump(_FaraCalificare().visit(copy.deepcopy(nod)))


def _mesaj(apel):
    if len(apel.args) > 1:
        return apel.args[1]
    for kw in apel.keywords:
        if kw.arg == "detail":
            return kw.value
    return None


def _frunze_cod(expr, intregi, locale):
    """Codurile pe care le poate lua expresia — un `409 if ... else 404` da {409, 404}.

    Se accepta si un NUME: o constanta de modul, sau o variabila locala legata o singura data de
    un `IfExp` de intregi (`http = 409 if ... else 404`), fiindca atunci valorile sunt tot fixe."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, int):
        return frozenset([expr.value])
    if isinstance(expr, ast.IfExp):
        return _frunze_cod(expr.body, intregi, locale) | _frunze_cod(expr.orelse, intregi, locale)
    if isinstance(expr, ast.Name):
        if expr.id in intregi:
            return frozenset([intregi[expr.id]])
        if expr.id in locale:
            return _frunze_cod(locale[expr.id], intregi, {})
    return frozenset()


def _frunze_clasa(expr, harta):
    """Codurile in care se traduce expresia de CLASA din use-case, prin harta stratului HTTP."""
    if isinstance(expr, ast.Attribute) and expr.attr in harta:
        return frozenset([harta[expr.attr]])
    if isinstance(expr, ast.Name) and expr.id in harta:
        return frozenset([harta[expr.id]])
    if isinstance(expr, ast.IfExp):
        return _frunze_clasa(expr.body, harta) | _frunze_clasa(expr.orelse, harta)
    return frozenset()


def _locale(fn):
    """Variabilele locale legate O SINGURA data — doar alea se pot citi ca valori fixe."""
    cate, val = {}, {}
    for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
        if isinstance(x, ast.Assign) and len(x.targets) == 1 and isinstance(x.targets[0], ast.Name):
            n = x.targets[0].id
            cate[n] = cate.get(n, 0) + 1
            val[n] = x.value
    return {n: v for n, v in val.items() if cate[n] == 1}


def perechi_vechi(fn, intregi):
    """`(coduri, arborele mesajului)` pentru fiecare `raise HTTPException(...)` din corp."""
    out, loc = [], _locale(fn)
    for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
        if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call) \
                and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException":
            a = x.exc.args[0] if x.exc.args else None
            if a is None:
                for kw in x.exc.keywords:
                    if kw.arg == "status_code":
                        a = kw.value
            m = _mesaj(x.exc)
            out.append((_frunze_cod(a, intregi, loc), _dump(m)))
    return out


def perechi_noi(fn, harta):
    """La fel, dar din use-case: clasa de domeniu tradusa inapoi in cod."""
    out, loc = [], _locale(fn)
    for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
        if not isinstance(x, ast.Raise) or not isinstance(x.exc, ast.Call):
            continue
        coduri = _frunze_clasa(x.exc.func, harta)
        if not coduri and isinstance(x.exc.func, ast.Name) and x.exc.func.id in loc:
            coduri = _frunze_clasa(loc[x.exc.func.id], harta)
        if not coduri:
            continue
        m = x.exc.args[0] if x.exc.args else None
        out.append((coduri, _dump(m)))
    return out


def _module_uc():
    """{(modul, nume): nod} pentru tot stratul use-case."""
    out = {}
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.startswith("uc_") or not f.endswith(".py"):
            continue
        arb = ast.parse(io.open(os.path.join(RAD, "core", f), encoding="utf-8").read())
        for n in arb.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[(f[:-3], n.name)] = n
    return out


def _tinta_invelisului(nod):
    """`(modul, nume)` pe care îl îmbracă funcția din `main.py`, sau None dacă nu e înveliș.

    Forma nu e una singură: cele mai multe învelișuri sunt `try: return _uc_X.f(...)`, dar cele care
    construiesc un răspuns au înăuntru `a, b = _uc_X.f(...)` urmat de `return Response(...)`, iar
    cele care primesc un fișier citesc octeții înainte. Ce le face înveliș e **delegarea din `try`**,
    nu forma lui `return`."""
    if not isinstance(nod, ast.FunctionDef) or not nod.body:
        return None
    t = nod.body[-1]
    if not isinstance(t, ast.Try) or not t.body:
        return None
    for x in ast.walk(ast.Module(body=t.body, type_ignores=[])):
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) \
                and isinstance(x.func.value, ast.Name) and x.func.value.id.startswith("_uc"):
            alias = x.func.value.id
            return (alias[1:] if alias.startswith("_") else alias, x.func.attr)
    return None


def confrunta(vechi_src, nou_src, uc, harta):
    """Nucleul probei, scos afara ca sa poata fi chemat si pe un univers FABRICAT.

    Intoarce `(diferente, numar_de_functii_confruntate, numar_de_perechi)`."""
    av, an = ast.parse(vechi_src), ast.parse(nou_src)
    iv, inn = _intregi(av), _intregi(an)
    vechi = {n.name: n for n in av.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    nou = {n.name: n for n in an.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    dif, confruntate, perechi = [], 0, 0
    for nume, vfn in sorted(vechi.items()):
        nfn = nou.get(nume)
        if nfn is None:
            continue
        tinta = _tinta_invelisului(nfn)
        if tinta is not None:
            corp = uc.get(tinta)
            if corp is None:
                dif.append("%s: invelisul trimite la %s, care nu exista" % (nume, tinta))
                continue
            acum = perechi_noi(corp, harta)
        else:
            acum = perechi_vechi(nfn, inn)          # n-a plecat inca: se compara cu el insusi
        inainte = perechi_vechi(vfn, iv)
        confruntate += 1
        perechi += len(inainte)
        if sorted(inainte) != sorted(acum):
            ramase_v = [p for p in inainte if p not in acum]
            ramase_n = [p for p in acum if p not in inainte]
            ramase_v, ramase_n = _fara_abateri(nume, ramase_v, ramase_n)
            if ramase_v or ramase_n:
                dif.append("%s:\n      inainte, fara pereche: %s\n      acum, fara pereche:     %s"
                           % (nume, ramase_v[:3], ramase_n[:3]))
    return dif, confruntate, perechi


def _forme_mesaj(msg_repr):
    """Formele sub care un mesaj declarat poate aparea in cod: constanta NUMITA (`FARA_DREPT_PREGATIRE`),
    literal (`"Element de coadă..."`) sau — [lot 19, 03.10.2026] — EXPRESIA scrisa ca atare (`str(e)`,
    `_cs.detaliu(e)`): un refuz care poarta mesajul exceptiei nu are nici nume, nici literal."""
    forme = {ast.dump(ast.Name(id=msg_repr, ctx=ast.Load())), ast.dump(ast.Constant(value=msg_repr))}
    try:
        forme.add(ast.dump(ast.parse(msg_repr, mode="eval").body))
    except SyntaxError:
        pass
    return forme


#: [deficiența 172, retestul Costin 09.10.2026 — limbajul de programator în textul afișat] o frază rescrisă PESTE TOT unde apare: același
#: refuz, același cod, în toate funcțiile care îl ridicau; mesajul vechi -> (mesajul nou, motivul). Se aplică numai perechilor
#: (cod, mesaj vechi) care au, pe ACELAȘI cod, perechea (cod, mesaj nou).
MESAJE_RESCRISE = {
    "'tenant inexistent sau fără acces'": ("'Firma nu există sau nu ai acces la ea.'",
        "Deficiența 172 (retestul Costin 09.10.2026): „tenant” e jargon de programator pe ecranul contabilului; același 404."),
    "'template tenant indisponibil pe server'": ("'Șablonul pentru o firmă nouă lipsește pe server — anunță administratorul platformei.'",
        "Deficiența 172: același refuz, aceeași clasă de eroare, fără „template tenant”."),
    "'XML neparsabil: %s' % str(e)[:200]": ("'XML-ul nu se poate citi: %s' % str(e)[:200]",
        "Deficiența 172: același 422, fără „neparsabil”."),
}


#: [deficiența 172] un FRAGMENT rescris într-un refuz structurat (dict cu `mesaj`): perechea veche, cu fragmentul înlocuit, e perechea nouă
FRAGMENTE_RESCRISE = {
    "Câmpuri obligatorii lipsă (schema eTransport): ": ("Câmpuri obligatorii lipsă (structura eTransport): ",
        "Deficiența 172: același 422 structurat (CAMPURI_LIPSA), fără „schema”."),
    # [comanda Costin 10.10.2026 pct.5] vocea aplicației, la persoana a treia (gardul: `test_text_afisat_limbaj::test_aplicatia_vorbeste_la_persoana_a_treia`)
    "(aștept ": ("(se așteaptă ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "Am primit ": ("S-a primit ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "am primit ": ("s-a primit ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "nu am putut ": ("nu s-a putut ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "Nu am putut ": ("Nu s-a putut ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "Nu pot ": ("Nu se poate ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "n-am putut ": ("nu s-a putut ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
    "Aștept ": ("Se așteaptă ", "Comanda Costin 10.10.2026 pct.5 („Vocea «nu pot …» … se rescrie la persoana a treia, pe toată clasa”): același refuz, același cod."),
}


def _fara_abateri(nume, ramase_v, ramase_n):
    """Scoate abaterile DECLARATE — fiecare cu motivul ei, sus in fisier."""
    for vechi, (nou, _motiv) in FRAGMENTE_RESCRISE.items():
        for p in [p for p in ramase_v if vechi in p[1]]:
            pereche = [q for q in ramase_n if q[0] == p[0] and q[1] == p[1].replace(vechi, nou)]
            if pereche:
                ramase_v = [x for x in ramase_v if x != p]
                ramase_n = [x for x in ramase_n if x != pereche[0]]
    for vechi, (nou, _motiv) in MESAJE_RESCRISE.items():
        fv, fn = _forme_mesaj(vechi), _forme_mesaj(nou)
        for p in [p for p in ramase_v if p[1] in fv]:
            pereche = [q for q in ramase_n if q[0] == p[0] and q[1] in fn]
            if pereche:
                ramase_v = [x for x in ramase_v if x != p]
                ramase_n = [x for x in ramase_n if x != pereche[0]]
    for (rut, mesaj), _motiv in ABATERI.items():
        if rut != nume:
            continue
        # [04.10.2026] mesajul vechi poate fi și o CONSTANTĂ NUMITĂ (`EMAIL_EXISTA`), nu doar un literal
        tinte = _forme_mesaj(mesaj)
        v = [p for p in ramase_v if p[1] in tinte]
        # [retest 08.10] abaterea = ACELAȘI cod, alt mesaj: se numără perechile noi pe codul ei, nu toate perechile noi ale
        # funcției (la `coada_depune` mai rămâne una pe 422, scoasă abia de CODURI_ADAUGATE, mai jos)
        # [Retest 2, 09.10.2026] perechile noi DECLARATE (PERECHI_ADAUGATE, scoase mai jos) nu sunt perechea abaterii: altfel o funcție
        # care are și o pereche adăugată pe același cod (`facturi_emite`: 422) n-ar mai putea purta nicio abatere de mesaj
        _adaugate = {f for (r2, m2) in PERECHI_ADAUGATE if r2 == nume for f in _forme_mesaj(m2)}
        n_cod = [p for p in ramase_n if v and p[0] == v[0][0] and p[1] not in _adaugate]
        if v and len(n_cod) == len(v):
            ramase_v = [p for p in ramase_v if p not in v]
            ramase_n = [p for p in ramase_n if p not in n_cod]
    # [04.10.2026] Refuzurile MUTATE într-un ajutor comun (aceeași stare, același cod, ridicate acum din ajutorul
    # chemat de funcție): se scot din „înainte, fără pereche”. Anti-vacuu: `test_MUTARILE_in_ajutor_chiar_cheama_ajutorul`.
    for (rut, mesaj), (_ajutor, _motiv) in PERECHI_MUTATE_IN_AJUTOR.items():
        if rut != nume:
            continue
        forme = _forme_mesaj(mesaj)
        ramase_v = [p for p in ramase_v if p[1] not in forme]
    # [07.10.2026] Același mesaj, un cod HTTP în plus, DECLARAT: perechea veche și cea nouă se scot împreună, numai dacă
    # diferă exact prin codul declarat.
    for (rut, mesaj), (cod, _motiv) in CODURI_ADAUGATE.items():
        if rut != nume:
            continue
        forme = _forme_mesaj(mesaj)
        for p in [p for p in ramase_v if p[1] in forme]:
            q = (p[0] | {cod}, p[1])
            if cod not in p[0] and q in ramase_n:
                ramase_v.remove(p)
                ramase_n.remove(q)
    # [B, 17.09.2026] Adaugarile DECLARATE (auth care nu exista in BAZA) se scot din „acum, fara
    # pereche": nu sunt drift al mutarii P7, ci functionalitate noua, fiecare cu motiv (v. sus).
    for (rut, msg_repr), _motiv in PERECHI_ADAUGATE.items():
        if rut != nume:
            continue
        forme = _forme_mesaj(msg_repr)
        ramase_n = [p for p in ramase_n if p[1] not in forme]
    return ramase_v, ramase_n


# =================================================================================================
# PROBELE
# =================================================================================================

def test_harta_acopera_tot_vocabularul():
    """O clasa de domeniu fara traducere ar iesi din aplicatie ca `500` — tacut, si cu alt mesaj."""
    from core import erori
    harta = _harta_cod()
    lipsa = [c.__name__ for c in erori.TOATE if c.__name__ not in harta]
    assert not lipsa, "clase fara cod HTTP in `main._COD_EROARE`: %s" % lipsa


def test_niciun_HTTPException_in_stratul_use_case():
    """Criteriul canonic: *un use-case nu construieste `HTTPException`* (PLAN_HARDENING.md:845)."""
    gasit = []
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.startswith("uc_") or not f.endswith(".py"):
            continue
        arb = ast.parse(io.open(os.path.join(RAD, "core", f), encoding="utf-8").read())
        for x in ast.walk(arb):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                    and x.func.id == "HTTPException":
                gasit.append("core/%s:%d" % (f, x.lineno))
    assert not gasit, "`HTTPException` construit in stratul use-case: %s" % gasit[:10]


def test_perechile_cod_mesaj_sunt_NESCHIMBATE():
    """Afirmatia care tine tot valul, confruntata functie cu functie cu starea de dinainte."""
    nou = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    dif, confruntate, perechi = confrunta(_sursa_veche(), nou, _module_uc(), _harta_cod())
    assert not dif, ("contractul HTTP s-a schimbat in %d locuri:\n    %s"
                     % (len(dif), "\n    ".join(dif[:8])))


def _apeluri(nod, harta):
    """Ce CHEAMĂ o funcție, ca multiset de nume — normalizat peste traducerea valului.

    `_uc_comun._cere_perioada(...)` și `_cere_perioada(...)` sunt același apel (se ia `.attr`), iar
    `_erori.<Clasa>(...)` se numără ca `HTTPException`, fiindcă asta a înlocuit. Apelurile pe care
    valul le ADAUGĂ prin construcție — delegarea către use-case și `_http_din` — se scad."""
    c, loc = {}, _locale(nod)
    for x in ast.walk(ast.Module(body=nod.body, type_ignores=[])):
        if not isinstance(x, ast.Call):
            continue
        f = x.func
        nume = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
        if nume is None:
            # `raise (_erori.Conflict if ... else _erori.Inexistent)(mesaj)`: clasa se alege în chiar
            # expresia de apel. E tot vocabularul, deci tot ce a înlocuit `HTTPException`.
            if _frunze_clasa(f, harta):
                c["HTTPException"] = c.get("HTTPException", 0) + 1
            continue
        # `cod = _erori.Conflict if ... else _erori.Inexistent` apoi `raise cod(mesaj)`: ridicarea se
        # face printr-un NUME LOCAL, dar clasa tot din vocabular vine. Se numără ca `HTTPException`,
        # fiindcă exact asta a înlocuit — altfel cele patru rute de coadă ar arăta ca apeluri pierdute.
        if nume in harta or (nume in loc and _frunze_clasa(loc[nume], harta)):
            nume = "HTTPException"
        c[nume] = c.get(nume, 0) + 1
    return c


def test_NICIUN_APEL_nu_s_a_pierdut_pe_drum():
    """Conservarea apelurilor: ce chema ruta înainte, cheamă și acum — învelișul plus use-case-ul.

    **De ce e nevoie de proba asta pe lângă cea de mai sus.** Perechile `(cod, mesaj)` spun ce se
    întâmplă când operațiunea REFUZĂ; nu spun nimic despre o instrucțiune care a dispărut tăcut.
    Instanța care a cerut-o: mutatorul a lăsat pe dinafară `_rate_limit_reset(request)` și
    `_rate_limit_email(_magic_rate, request)` — două gărzi anti-spam —, iar contractul de refuz a
    rămas identic, suita verde, ruff verde. *Un apel care nu se mai face nu strigă; se vede numai
    numărându-l.*
    """
    harta = _harta_cod()
    uc = _module_uc()
    nou_src = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    av, an = ast.parse(_sursa_veche()), ast.parse(nou_src)
    vechi = {n.name: n for n in av.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    nou = {n.name: n for n in an.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    dif, confruntate = [], 0
    for nume, vfn in sorted(vechi.items()):
        nfn = nou.get(nume)
        if nfn is None:
            continue
        tinta = _tinta_invelisului(nfn)
        if tinta is None:
            continue                      # n-a plecat: se compară cu el însuși, n-are ce spune
        corp = uc.get(tinta)
        if corp is None:
            dif.append("%s: învelișul trimite la %s, care nu există" % (nume, tinta))
            continue
        confruntate += 1
        inainte = _apeluri(vfn, harta)
        acum = _apeluri(nfn, harta)
        for k, v in _apeluri(corp, harta).items():
            acum[k] = acum.get(k, 0) + v
        acum.pop("_http_din", None)
        acum[tinta[1]] = acum.get(tinta[1], 0) - 1          # delegarea, adăugată de val
        if acum.get(tinta[1]) == 0:
            acum.pop(tinta[1])
        # [R187] INLOCUIRILE declarate se contabilizeaza pe numele VECHI: apelul nu s-a pierdut, i
        # s-a schimbat numele. Tabelul e pazit de `test_INLOCUIRILE_declarate_chiar_exista`.
        for (_fn, _vechi), (_nou, _m) in APELURI_INLOCUITE.items():
            if _fn == nume and acum.get(_nou):
                acum[_vechi] = acum.get(_vechi, 0) + acum[_nou]
        # [08.10.2026] corpul EXTRAS într-un ajutor: creditul = apelurile pe care ajutorul chiar le face (vezi tabelul de sus)
        if nume in APELURI_EXTRASE_IN_AJUTOR and acum.get(APELURI_EXTRASE_IN_AJUTOR[nume][0][1]):
            # creditul se dă PE APEL efectiv al ajutorului (ca la BIFA_INLOCUIRI): `portal_bon` cheamă `dir_bonuri` de două ori, cum
            # chema înainte `expanduser` (deficiența 9)
            _n_apel = acum[APELURI_EXTRASE_IN_AJUTOR[nume][0][1]]
            for k, v in _apeluri_ajutor(*APELURI_EXTRASE_IN_AJUTOR[nume][0]).items():
                acum[k] = acum.get(k, 0) + v * _n_apel
        # [lot 19, 03.10.2026] fiecare `_uc_comun.bifa(corp, x)` inlocuieste o pereche `bool(corp.get(x))` (sau, la
        # taxarea inversa, `str(corp.get(x)).strip().lower()`): creditul se da PE APEL efectiv, iar `extra` numeste
        # apelurile scoase deliberat. Anti-vacuu: `test_BIFA_INLOCUIRI_chiar_cheama_bifa`.
        if nume in BIFA_INLOCUIRI:
            _per_apel, _extra, _m = BIFA_INLOCUIRI[nume]
            for k, v in _per_apel.items():
                acum[k] = acum.get(k, 0) + v * acum.get("bifa", 0)
            for k, v in _extra.items():
                acum[k] = acum.get(k, 0) + v
        lipsa = {k: inainte[k] - acum.get(k, 0) for k in inainte if inainte[k] > acum.get(k, 0)}
        if lipsa:
            dif.append("%s: apeluri pierdute %s" % (nume, lipsa))
    assert confruntate >= 300, "doar %d funcții confruntate — universul s-a golit" % confruntate
    assert not dif, ("apeluri care nu se mai fac, în %d funcții:\n    %s"
                     % (len(dif), "\n    ".join(dif[:10])))


def test_BIFA_INLOCUIRI_chiar_cheama_bifa():
    """Anti-vacuu: o functie declarata in BIFA_INLOCUIRI cheama efectiv `_uc_comun.bifa` (altfel creditul ar scuza
    apeluri chiar pierdute)."""
    src = io.open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read()
    arb = ast.parse(src)
    fn = {n.name: n for n in arb.body if isinstance(n, ast.FunctionDef)}
    lipsa = [n for n in BIFA_INLOCUIRI if n not in fn or not any(
        isinstance(x, ast.Call) and getattr(x.func, "attr", None) == "bifa" for x in ast.walk(fn[n]))]
    assert lipsa == [], lipsa


def test_DECORATORII_rutelor_sunt_NEATINSI():
    """Textul de deasupra lui `def`, literă cu literă — decoratorii **cu comentariile lor**.

    **De ce e o probă și nu o presupunere.** Mutatorul reconstruia decoratorii din AST, iar AST-ul
    n-are comentarii: 27 de rute și-au pierdut comentariul de pe linia decoratorului. Printre ele,
    cinci purtau marcajul `[api_intern_v1]` — o **declarație citită de cod**: `core/test_ruta_fara_
    apelant` citește exact linia aia ca să știe care rute își declară singure lipsa unui ecran. Cele
    cinci au trecut din EXCLUS în ROȘU la verificator, deși declarația fusese scrisă acolo de mult.

    *Un comentariu nu e decorativ când un instrument îl citește.*
    """
    metode = METODE

    def decoratori(src):
        arb = ast.parse(src)
        linii = src.splitlines(True)
        out = {}
        for n in ast.walk(arb):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or not n.decorator_list:
                continue
            if not any(isinstance(d, ast.Call) and getattr(d.func, "attr", None) in metode
                       for d in n.decorator_list):
                continue
            out[n.name] = "".join(linii[n.decorator_list[0].lineno - 1:n.lineno - 1])
        return out

    vechi = decoratori(_sursa_veche())
    acum = decoratori(io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    comune = sorted(set(vechi) & set(acum))
    assert len(comune) >= 400, "doar %d rute comune — universul s-a golit" % len(comune)
    dif = [n for n in comune if vechi[n] != acum[n]]
    assert not dif, ("decoratori schimbați la %d rute (primele: %s). Un comentariu de pe linia "
                     "decoratorului poate fi o declarație pe care o citește un instrument."
                     % (len(dif), dif[:6]))


def test_CE_CERE_ALTCINEVA_de_la_main_exista():
    """Fiecare `main.<nume>` cerut din `core/` sau `scripts/` există — a patra pierdere tăcută.

    `core/firma_rezumat.py` cheamă `_main.pastila_firma(...)`: un nume pe care `main.py` îl importa
    pentru alții, fără să-l folosească el însuși. După ce cele 385 de corpuri au plecat, o curățenie
    automată de importuri l-a văzut „nefolosit" și l-a scos — iar lucrătorul modelului de citire a
    început să dea `AttributeError`, cu șase firme ajunse cu `control_fiscal` în stare de eroare.

    *Într-un modul care e citit din afară, «nefolosit aici» nu înseamnă «nefolosit».* Proba citește
    ACCESELE din cod, nu o listă scrisă de mână: un nume nou cerut de altcineva intră singur.
    """
    import re
    import main
    ceruti = set()
    for rad, _d, fisiere in os.walk(RAD):
        if any(x in rad for x in (".git", "venv", "__pycache__", "node_modules")):
            continue
        if os.path.basename(rad) not in ("core", "scripts"):
            continue
        for f in fisiere:
            if not f.endswith(".py") or f.startswith("test_"):
                continue
            s = io.open(os.path.join(rad, f), encoding="utf-8", errors="ignore").read()
            if not re.search(r"\bimport main\b", s):
                continue
            for m in re.finditer(r"\b_main\d*\.([A-Za-z_][A-Za-z0-9_]*)", s):
                ceruti.add((os.path.join(os.path.basename(rad), f), m.group(1)))
    # [E6, 14.09.2026] Pragul a fost 3 și a coborât la 2, iar motivul e chiar reușita: cele două
    # accese ale lui `core/firma_rezumat.py` (`pastila_firma`, `_termene_una_firma`) au dispărut
    # când stratul de sub HTTP a încetat să mai depindă de HTTP. Ce a rămas sunt cele două unelte
    # de măsură care pornesc aplicația (`_main.app`) — legitime, și singurele.
    # *Un anti-vacuum care cere ca aplicația să fie murdară se stinge exact când munca reușește*,
    # de-aia proba care contează e cea de mai jos, pe univers FABRICAT.
    assert len(ceruti) >= 2, "anti-vacuu: doar %d accese gasite — cautarea s-a rupt" % len(ceruti)
    fals = {("zt/fals.py", "nume_care_nu_exista_pe_main")}
    assert [x for x in fals if not hasattr(main, x[1])], (
        "calibrare: un nume inexistent pe `main` nu e raportat — verificarea nu verifica")
    lipsa = sorted("%s -> main.%s" % (f, n) for f, n in ceruti if not hasattr(main, n))
    assert not lipsa, ("nume cerute de la `main` care nu mai exista:\n    %s"
                       % "\n    ".join(lipsa))


def test_MUTATIE_o_garda_pierduta_la_mutare_e_prinsa():
    """Calibrarea probei de mai sus, pe propriul ei mod de eșec — și pe instanța care a cerut-o.

    Universul e fabricat: o rută care cheamă o gardă și apoi face treaba, și un înveliș care a uitat
    garda. *Exact ce s-a întâmplat cu `_rate_limit_reset`: contract de refuz identic, suită verde,
    ruff verde, și o gardă anti-spam dispărută.*"""
    harta = _harta_cod()
    vechi = ast.parse("def r(a, request):\n    garda(request)\n    return lucru(a)\n").body[0]
    corp = ast.parse("def r(a):\n    return lucru(a)\n").body[0]
    inv_bun = ast.parse("def r(a, request):\n    garda(request)\n    try:\n"
                        "        return _uc_z.r(a)\n    except E as e:\n"
                        "        raise _http_din(e)\n").body[0]
    inv_rau = ast.parse("def r(a, request):\n    try:\n"
                        "        return _uc_z.r(a)\n    except E as e:\n"
                        "        raise _http_din(e)\n").body[0]

    def lipsa(inv):
        inainte = _apeluri(vechi, harta)
        acum = _apeluri(inv, harta)
        for k, v in _apeluri(corp, harta).items():
            acum[k] = acum.get(k, 0) + v
        acum.pop("_http_din", None)
        acum["r"] = acum.get("r", 0) - 1
        return {k: inainte[k] - acum.get(k, 0) for k in inainte if inainte[k] > acum.get(k, 0)}

    assert lipsa(inv_rau) == {"garda": 1}, "garda pierdută a trecut nevăzută"
    assert not lipsa(inv_bun), "învelișul corect e raportat ca pierzând ceva: %s" % lipsa(inv_bun)


def test_ANTIVACUU_chiar_confrunta_ceva():
    """Daca `git show` da gol, daca invelisurile nu se recunosc sau daca perechile nu se citesc,
    proba de sus ar trece pe gol — verde despre o lume pe care n-o vede."""
    nou = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    _dif, confruntate, perechi = confrunta(_sursa_veche(), nou, _module_uc(), _harta_cod())
    assert confruntate >= 300, "doar %d functii confruntate — universul s-a golit" % confruntate
    assert perechi >= 400, "doar %d perechi (cod, mesaj) citite — citirea s-a rupt" % perechi


def test_MUTATIE_un_cod_schimbat_e_prins():
    """Calibrare pe propriul mod de esec: daca traducerea ar da alt cod, proba o spune?

    Universul e FABRICAT — o ruta care refuza cu 404, si un use-case care refuza cu 409. Asa
    calibrarea nu cere ca aplicatia adevarata sa fie stricata ca sa se poata masura."""
    vechi = ("from fastapi import HTTPException\n"
             "@app.get('/x')\n"
             "def ruta_x(a):\n"
             "    raise HTTPException(404, 'nu exista')\n")
    nou = ("@app.get('/x')\n"
           "def ruta_x(a):\n"
           "    try:\n"
           "        return _uc_z.ruta_x(a)\n"
           "    except _erori.EroareDeDomeniu as e:\n"
           "        raise _http_din(e)\n")
    corp = ast.parse("def ruta_x(a):\n    raise _erori.Conflict('nu exista')\n").body[0]
    dif, confruntate, _p = confrunta(vechi, nou, {("uc_z", "ruta_x"): corp}, _harta_cod())
    assert confruntate == 1, "universul fabricat nu s-a confruntat deloc"
    assert dif, "un 404 devenit 409 a trecut nevazut — comparatia nu compara"


def test_MUTATIE_un_mesaj_schimbat_e_prins():
    """A doua directie: acelasi cod, alt mesaj."""
    vechi = ("@app.get('/x')\n"
             "def ruta_x(a):\n"
             "    raise HTTPException(404, 'nu exista')\n")
    nou = ("@app.get('/x')\n"
           "def ruta_x(a):\n"
           "    try:\n"
           "        return _uc_z.ruta_x(a)\n"
           "    except _erori.EroareDeDomeniu as e:\n"
           "        raise _http_din(e)\n")
    corp = ast.parse("def ruta_x(a):\n    raise _erori.Inexistent('nu mai exista')\n").body[0]
    dif, _c, _p = confrunta(vechi, nou, {("uc_z", "ruta_x"): corp}, _harta_cod())
    assert dif, "un mesaj schimbat a trecut nevazut"


def test_MUTATIE_identitatea_nu_da_fals_pozitiv():
    """A treia directie, cea care lipseste de obicei: pe un univers NESCHIMBAT, zero diferente.
    Un comparator care striga mereu e la fel de inutil ca unul care tace mereu."""
    vechi = ("@app.get('/x')\n"
             "def ruta_x(a):\n"
             "    raise HTTPException(404, 'nu exista')\n")
    nou = vechi
    dif, confruntate, _p = confrunta(vechi, nou, {}, _harta_cod())
    assert confruntate == 1 and not dif, "comparatia vede o diferenta acolo unde nu e: %s" % dif
