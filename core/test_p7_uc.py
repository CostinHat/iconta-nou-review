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

#: [lotul 11, deficiența 440, W3a] refuzurile de date adunate cu `core.erori.ErorileFormularului`
_MOTIV_440_W3A = ("Deficiența 440 (comanda Costin 11.1 pct.16, verbatim în DECIZII „Comanda 11.1”): „toate erorile apar deodată, fiecare cu "
                  "textul ei, în casetă și lângă câmp”. Refuzurile de date se adună cu `core.erori.ErorileFormularului` și pleacă o dată, "
                  "cu `erori_campuri`; același cod.")

#: [lotul 11, deficiența 440, W3b] motivul comun al refuzurilor trecute pe „toate erorile deodată”
_MOTIV_440 = ("Lotul 11, deficiența 440 (comanda Costin 11.1 pct.16): toate erorile deodată, fiecare lângă câmpul ei — `erori_campuri`, "
              "același cod.")

#: abaterile acceptate de la „mesaj neschimbat", fiecare cu motivul ei. Orice alta abatere pica.
ABATERI = {
    ("asistent_creeaza", "EMAIL_INVALID"): _MOTIV_440,
    ("coada_adauga", "str(e)"): (
        "Lotul 11, deficiența 445 (comanda Costin 11.1): refuzul generării cu trimitere (`RefuzGenerare`: ecranul / câmpul / notele de "
        "reparat) ajunge la ecran ca obiect (`e.detaliu()`), ca în `uc_declaratii`; celelalte refuzuri rămân text — același 422."),
    ("facturi_numerotare_set", "r.get('mesaj', 'eroare')"): _MOTIV_440,
    ("produse_creeaza", "r.get('mesaj', 'produs invalid')"): _MOTIV_440,
    ("contracte_sabloane_salveaza", "mesaje.get(rez.get('cod'), 'eroare')"): _MOTIV_440,
    ("registratura_creeaza", "'Data înregistrării nu e o dată: %r (aștept AAAA-LL-ZZ).' % _d"): _MOTIV_440,
    ("coada_adauga", "r['mesaj']"): (
        "Deficiența 299 (comanda Costin 17.10.2026 7.2 pct.4, verbatim în DECIZII): același 409 „deja în coadă”, cu perioada declarată, "
        "tipul cum îl scrie formularul, cine a pregătit-o, starea și drumul („Deschide-o, sau înlocuiește-o”) — `refuz_deja_in_coada`."),
    ("factura_trimite_spv", "r.get('mesaj', 'Conectează ANAF (SPV) înainte de a trimite.')"): (
        "Deficiența 289b (lotul 6, comanda Costin 16.10.2026): același 409, refuzul are acum butonul spre Setări cont → Conectare SPV "
        "(`refuz_spre_ecran`, ținta `conectare_spv`) și spune ce lipsește în cuvintele contabilului."),
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
    ("tenant_amortizare", 'f"Amortizarea nu se poate genera pentru {den}: {e}"'): (
        "Lotul 11, deficiența 451 (comanda Costin 11.1): rândurile amortizării vin din sursa unică `amortizare_lunii.linii` (aceeași cu "
        "regenerarea pe uscat a ciornei depășite, `ciorne_depasite`); refuzul pe mijlocul fix se formulează acolo, cu numele lui, iar "
        "use-case-ul îl trece cu `str(e)` — același 422, același motiv, mesajul cu diacritice („până nu corectezi fișa lui”)."),
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
        "cererii (`confirmari`: [{amprenta, motiv}]), ci ce are de făcut. Gard: `core/test_text_afisat_limbaj.py`. [Deficiența 313, "
        "17.10.2026] constatările nu se mai numără „1 constatare/constatări”: „o confirmare scrisă pentru <N constatări>” (`common.cate`)."),
    ("vanzare_aur_investitii", "suma invalida"): (
        "G5 (`core/test_g1_cod_mesaj.py`): un input-guard telegrafic primeste constrangerea in "
        "mesaj. Codul ramane 422. Cazul a intrat in domeniul lui G5 odata cu mutarea corpului "
        "rutei din `main.py` in `core/uc_tenants.py` — regula nu s-a slabit, s-a aplicat."),
}


#: Perechi (cod, mesaj) ADAUGATE deliberat DUPA mutarea P7, cu motivul. Simetric cu APELURI_INLOCUITE:
#: garda P7 pazeste ca MUTAREA a fost verbatim; o functionalitate NOUA adaugata dupa mutare (auth) nu
#: e o abatere a mutarii, ci un adaus declarat. Anti-vacuu: `test_ADAUGARILE_declarate_chiar_exista`.
#: Cheia mesajului e ori NUMELE constantei (FARA_DREPT_PREGATIRE), ori chiar literalul (404 pe obiect).
_MOTIV_82 = ("Comanda Costin 8.2 (18.10.2026, verbatim în DECIZII „Comanda 8.2”) pct.4, regula importurilor de migrare: „orice rând citit e "
             "afișat sau semnalat cu motiv, nimic nu se înlocuiește pe tăcute, totul trece prin previzualizare înainte de salvare”.")
_MOTIV_C69 = ("Deficiența C69 (lotul 10, deciziile Costin 20.10.2026, verbatim în DECIZII „Lotul 10, C69”): bilanțul fără mare contribuabil / "
              "forma de proprietate / județ / administrator și e-Factura fără datele firmei se opresc — același 422, dar ca obiect "
              "{mesaj, ecran, camp_ecran} (butonul spre Date firmă, cu câmpul lipsă în vedere); celelalte refuzuri rămân text.")
_MOTIV_C73 = ("Deficiența C73 (lotul 10, găsită de e2e la 428, 21.10.2026): cheia naturală dublată (CUI-ul clientului, codul de inventar, "
              "exemplarul statului de plată) cădea cu 500 din `UniqueViolation`; acum refuzul numit `chei_unice.CheieDublata`, ca obiect "
              "{mesaj, cod, valoare, existent[, erori_campuri]} — 409 cu lucrul existent (clientul, exemplarul), 422 pe câmpul `cod` la mijlocul fix.")
_MOTIV_C73_U2 = ("Deficiența C73, clasa închisă peste toată schema firmei (lotul 10, U2, 21.10.2026; gardul `test_lot10_c73_chei_unice`): "
                 "codul de bare dublat (și la cursă) -> 422 pe câmpul `barcode`, cu articolul care îl are (înainte: 400 cu textul verificării "
                 "prealabile, iar cursa dădea 500); numărul dat de aplicație (registratura, registrele art.321, registrul-inventar) se reia "
                 "la cursă, iar abia după reluări pierdute la rând -> 409 numit; a doua trimitere e-Factura simultană -> 409 „deja în curs”, "
                 "înainte de încărcarea la ANAF.")
_MOTIV_C73_U3 = ("Deficiența C73 pe schema `public` (lotul 10, U3, 21.10.2026; gardul `test_lot10_c73_chei_unice::test_gardul_cheilor_unice_"
                 "public`): CUI-ul altui cabinet pe Setări cabinet (`accounting_firms_cui_key`, unic pe toată platforma) cădea cu 500 din "
                 "`UniqueViolation`; acum 422 pe câmpul `cui`, cu `CheieDublata.detaliu()` — fără să numească cabinetul care îl are.")
_MOTIV_102_8B = ("Comanda Costin 10.2 pct.8b (lotul 10, verbatim în DECIZII „Comanda 10.2”): „La refuzul «numerar + card ≠ total» mesajul nu "
                  "dă cifrele (total 231,00, încasat 200,00, diferență 31,00).” Același 400, cu cifrele (`raport_z.mesaj_plata_diferita`); "
                  "comparația pe lei în Decimal, nu în float cu toleranța 0,01.")
PERECHI_ADAUGATE = {
    ('casa_adauga', "{'mesaj': rez['eroare'], 'erori_campuri': rez['erori_campuri'], 'cod': rez.get('cod')}"): _MOTIV_440_W3A,
    ('chitanta_emite', '_amef.detaliu(_amef_e) if _amef_e is not None and len(er.campuri) == 1 else er.detaliu()'): _MOTIV_440_W3A,
    ('chitanta_emite', '_amef.detaliu(_amef.refuz_nedeclarata())'): _MOTIV_440_W3A,
    ('factura_creeaza', 'e.detaliu()'): _MOTIV_440_W3A,
    ('salariat_beneficiu_lunar', "{'mesaj': r['eroare'], 'erori_campuri': r['erori_campuri']} if r.get('erori_campuri') else r['eroare']"): _MOTIV_440_W3A,
    ('vanzare_ic', "'Livrarea intracomunitară nu s-a înregistrat: nota contabilă a facturii nu s-a putut scrie (%s). Nimic nu s-a scris.' % ((_contare.get('afirmatie') or {}).get('motiv') or _contare.get('cod') or 'contarea facturii lipsește')"): _MOTIV_440_W3A,
    ('vector_salveaza', "{'mesaj': _mesaj, 'erori_campuri': rez.get('erori_campuri') or [{'camp': _camp, 'mesaj': _mesaj}]}"): _MOTIV_440_W3A,
    ("contracte_sabloane_salveaza", "{'mesaj': rez['mesaj'], 'erori_campuri': rez['erori_campuri']}"): _MOTIV_440,
    ("contracte_sabloane_salveaza", "{'mesaj': _m, 'erori_campuri': [{'camp': 'c-nume', 'mesaj': _m}]}"): _MOTIV_440,
    ("cv_transfer", "{'mesaj': rez['eroare'], 'erori_campuri': rez['erori_campuri']}"): _MOTIV_440,
    ("produse_actualizeaza", "{'mesaj': r['mesaj'], 'erori_campuri': r['erori_campuri']}"): _MOTIV_440,
    ("tenant_creeaza", "_er.detaliu()"): _MOTIV_440,
    ("produse_actualizeaza", "r['mesaj']"): "Lotul 11, 449: refuzul categoriei cotei 0% (produse_api.verifica_categoria) e al datelor — 400 cu motivul, nu 404 «produs inexistent».",
    ("horeca_raport_z", "_rz.mesaj_plata_diferita(total, rz.numerar, rz.card)"): _MOTIV_102_8B,
    ("tenant_amortizare", "'Amortizarea lunii e deja generată, cu exact sumele registrului de acum (nota %s, ciornă) — o vezi și o "
                          "validezi în Registru jurnal; o a doua generare n-ar schimba nimic.' % _et.nota(cur, schema, ciorna_veche)"): (
        "Comanda Costin 11.1 pct.23 (lotul 11, verbatim în DECIZII „Comanda 11.1”): „«Generează amortizarea» activ pe luni deja "
        "amortizate”. A doua generare cu exact sumele ciornei existente se refuză numit (400), în loc să întoarcă tăcut aceeași ciornă; "
        "amortizarea restantă păstrează numărarea „deja generate” (`refuza_aceeasi=False`)."),
    ("cv_barcode_set", "e.detaliu()"): _MOTIV_C73_U2,
    ("registratura_creeaza", "e.detaliu()"): _MOTIV_C73_U2,
    ("registre_art321_adauga", "e.detaliu()"): _MOTIV_C73_U2,
    ("registru_inventar_adauga", "e.detaliu()"): _MOTIV_C73_U2,
    ("factura_trimite_spv", "r['mesaj']"): _MOTIV_C73_U2,
    ("factura_trimite_spv", "dict(din_ef)"): (
        "Lotul 11, C86 (subagentul Q, comanda Costin 11.1): factura EMISĂ venită din XML-ul e-Factura e deja transmisă de emitent (OUG "
        "120/2021 art.4 alin.(3) și (6)); „Trimite în SPV” se refuză numit (409, `FACTURA_DIN_EFACTURA`, `efactura_trimitere.refuz_din_efactura`), "
        "înaintea conexiunii SPV — altfel XML-ul refăcut din cantitate × preț ar dubla factura în SPV. Gardul: `core/test_lot11_q_c86.py`."
        " [lotul 11, AT] Detaliul e afirmația tipată întreagă (`fapt` despre factură, cu `cod` și `mesaj`), nu reîmpachetată ca proză."),
    ("factura_trimite_spv", "dict(r)"): (
        "Lotul 11, C86: același refuz, venit din poarta 0 a lui `efactura_trimitere.trimite` (pentru orice apelant al orchestrării)."),
    ("client_creeaza", "e.detaliu()"): _MOTIV_C73,
    ("client_actualizeaza", "e.detaliu()"): _MOTIV_C73,
    ("achizitie_necorporala", "e.detaliu()"): _MOTIV_C73,
    ("nota_inventariere", "e.detaliu()"): _MOTIV_C73,
    ("tenant_stat_emite", "e.detaliu()"): _MOTIV_C73,
    ("eu_cabinet_set", "e.detaliu()"): _MOTIV_C73_U3,
    ("s1005_xml", "e.detaliu() if isinstance(e, RefuzGenerare) else str(e)"): _MOTIV_C69,
    ("s1005_valideaza", "e.detaliu() if isinstance(e, RefuzGenerare) else str(e)"): _MOTIV_C69,
    ("s1003_xml", "e.detaliu() if isinstance(e, RefuzGenerare) else str(e)"): _MOTIV_C69,
    ("s1003_valideaza", "e.detaliu() if isinstance(e, RefuzGenerare) else str(e)"): _MOTIV_C69,
    ("factura_trimite_spv", "e.detaliu() if getattr(e, 'ecran', None) else str(e)"): _MOTIV_C69,
    ("declaratie_genereaza", "e.detaliu() if isinstance(e, RefuzGenerare) else str(e)"): (
        "Deficiența 431 (comanda Costin 10.1, 20.10.2026, verbatim în DECIZII „Comanda 10.1”): „mesajul de refuz trimite la ce lipsește” — "
        "refuzul generatorului cu trimitere (`erori.RefuzGenerare`: nota de dividende în ciornă, Date firmă → Asociați) ajunge la ecran ca "
        "obiect {mesaj, note, ecran, camp_ecran}; celelalte refuzuri rămân text (același 422)."),
    ("declaratie_valideaza", "e.detaliu() if isinstance(e, RefuzGenerare) else str(e)"): (
        "Deficiența 431 (comanda Costin 10.1, 20.10.2026): aceeași trimitere ca la `declaratie_genereaza` — pasul 2 al Declarațiilor "
        "generează prin ruta de validare, deci refuzul D205 cu nota de deschis vine pe aici (422, obiect în loc de text)."),
    # [lotul 11, 440, K] perechea lui 425 (`{'mesaj': MESAJ_METODA_STOC, 'erori_campuri': [...]}`) a ieșit: metoda lipsă se refuză acum în
    # colector (`_er.camp("metoda_stoc", MESAJ_METODA_STOC)` + `_er.refuza()`), cu celelalte erori ale balanței — tot 422, pe câmpul metodei
    ("solduri_salveaza", "str(e)"): (
        "Deficiența 426 (comanda Costin 10.1, 20.10.2026): „al doilea import de balanță … o înlocuiește pe prima fără avertisment” — fără "
        "confirmarea înlocuirii (`inlocuieste`), `BalantaExistenta` devine 409 cu totalurile vechi și noi (`solduri_api.text_inlocuire`)."),
    ("parteneri_salveaza", "str(e)"): (
        "Deficiența 426, clasa (comanda Costin 10.1, 20.10.2026): soldurile pe parteneri existente se înlocuiau tăcut (DELETE + INSERT) — "
        "fără `inlocuieste`, `migrare_api.InlocuireNeconfirmata` devine 409 cu totalurile vechi și noi (`solduri_parteneri_api.text_inlocuire`)."),
    ("mijloace_import_salveaza", "str(e)"): (
        "Deficiența 426, clasa (comanda Costin 10.1, 20.10.2026): registrul mijloacelor fixe se înlocuia tăcut — fără `inlocuieste`, 409 cu "
        "valoarea de intrare și amortizarea preluată, vechi și noi, și notele de amortizare înregistrate (`mijloace_fixe_import_api.text_inlocuire`)."),
    ("istoric_import_salveaza", "str(e)"): (
        "Deficiența 426, clasa (comanda Costin 10.1, 20.10.2026): istoricul declarațiilor preluat se înlocuia tăcut — fără `inlocuieste`, 409 "
        "cu declarațiile și perioadele vechi și noi și depunerile prin iConta din anii lor (`istoric_declaratii_import_api.text_inlocuire`)."),
    ("asociati_import_salveaza", "str(e)"): (
        "Deficiența 426, clasa (comanda Costin 10.1, 20.10.2026): importul asociaților fără dată de cesiune (corectura) înlocuia tăcut "
        "structura (DELETE + INSERT) — fără `inlocuieste`, 409 cu structura veche și nouă, cotele și notele de dividende care se împart "
        "după ea (`asociati_import_api.text_inlocuire`)."),
    ("salariati_import_salveaza", "str(e)"): (
        "Deficiența 426, clasa (comanda Costin 10.1, 20.10.2026): fișele salariaților existenți (același CNP) se suprascriau tăcut (ON CONFLICT "
        "DO UPDATE) — fără `inlocuieste`, 409 cu cine se actualizează și statele de plată deja emise (`salariati_import_api.text_inlocuire`)."),
    ("proforma_transforma", "{'ok': False, 'cod': facturi_api.COD_INTREABA_MARFA, 'mesaj': str(e)}"): (
        "C63 (decizia Costin 19.10.2026, DECIZII „Închiderea lotului 9” pct.2): „la transformarea în factură se pune aceeași întrebare ca "
        "la orice factură, «Pleacă marfa acum?»”. Factura născută din proformă / aviz cu articol de stoc cere răspunsul ca emiterea din "
        "formular — 422 structurat cu codul `INTREABA_PLEACA_MARFA`, nimic scris; ecranul pune întrebarea și retrimite."),
    ("proforma_transforma", "_cs.detaliu_metoda_stoc(e)"): (
        "C63 (decizia Costin 19.10.2026, DECIZII „Închiderea lotului 9” pct.2): cu articolul trecut pe factură, refuzul metodei de stoc "
        "(nedeclarată / global-valoric cu ieșire pe articol) poate apărea și aici: 422 structurat spre Date firmă, ca la emitere."),
    ("achizitie_neinregistrat", "refuz"): (
        "Deficiența 402 (comanda Costin 9.2, 19.10.2026, verbatim în DECIZII „Comanda 9.2”): borderoul de achiziție identifică vânzătorul "
        "persoană fizică (domiciliul, actul de identitate) și, pe un cont de stoc, cere articolul și cantitatea (OMFP 2634/2015 anexa 1 "
        "pct.2 și pct.6) — refuz numit cu câmpurile lui (422)."),
    ("facturi_storno", "refuz"): (
        "Deficiența 419 (comanda Costin 9.3, 19.10.2026): stornarea facturii care a descărcat stocul cere răspunsul „marfa se întoarce în "
        "stoc?” (`retur`), iar un `retur` care nu e da/nu se refuză — 422, cu întrebarea și câmpul ei."),
    ("retete_import_incarca", "'fișierul nu conține niciun rând de rețetă'"): (
        _MOTIV_82 + " Deficiența 375: un fișier fără niciun rând de rețetă se refuză numit (400), nu se previzualizează gol."),
    ("retete_import_salveaza", "str(e)"): (
        _MOTIV_82 + " Deficiența 375: salvarea refăce potrivirea și verificarea; niciun rând bun -> refuz numit (422), nimic scris."),
    # [lotul 11, 440, K] perechea lui 343 (`MESAJ_CONT_IN_AFARA % …`) a ieșit ca pereche: conturile din afara planului se refuză acum în
    # colector (`_er.fara_camp(MESAJ_CONT_IN_AFARA % …)` + `_er.refuza()`), împreună cu metoda de stoc lipsă — același 422
    ("asistent_creeaza", "mesaj_din_cod(_r.get('cod'))"): (
        "Deficiența 319 (comanda Costin 17.10.2026 7.2): invitația poartă și „Poate depune” și firmele alocate; refuzul lui "
        "`set_permisiuni` / `atribuie_firma` (firmă din alt cabinet) oprește invitația întreagă, în aceeași tranzacție cu contul (400)."),
    ("coada_adauga", "'Declarația de înlocuit nu mai e în coadă (a fost depusă, retrasă sau înlocuită între timp).'"): (
        "Deficiența 299: „Înlocuiește” pe un element care între timp a ieșit din coadă — refuz numit (409), nu o a doua declarație activă."),
    ("coada_depune", '{"cod": cod, "mesaj": r["mesaj"], "coada_id": coada_id, "actiune": "Generează din nou"}'): (
        "Deficiența 297: refuzul depunerii pentru declarația DEPĂȘITĂ (aprobarea implicită a depunătorului, apoi depunerea) — 409 "
        "structurat, cu „Generează din nou”."),
    ("coada_depune", '{"cod": _c, "mesaj": _ap["mesaj"], "coada_id": coada_id, "actiune": "Generează din nou"}'): (
        "Deficiența 297: ca la aprobare — declarația DEPĂȘITĂ nu se depune la ANAF; 409 structurat, cu „Generează din nou”."),
    ("coada_aproba", '{"cod": cod, "mesaj": r["mesaj"], "coada_id": coada_id, "actiune": "Generează din nou"}'): (
        "Deficiența 297 (comanda Costin 17.10.2026 7.2 pct.3): declarația DEPĂȘITĂ (datele-sursă s-au schimbat după generare) nu se "
        "aprobă — 409 structurat, cu drumul „Generează din nou”. Gardul: `core/test_297_298_surse_declaratie.py`."),
    ("coada_respinge", "MESAJ_RENUNTA_ALTUI"): (
        "Deficiența 293 (lotul 6, completarea Costin 16.10.2026, verbatim în DECIZII): „Pe o declarație a altcuiva, fără dreptul de "
        "depunere, nu se oferă nicio acțiune în afară de vizualizare; serverul refuză la fel.” Fără validarea în doi, renunțarea (403) e a "
        "celui care a pregătit-o sau a celui care o depune. Gardul: `core/test_293_renunta_altui.py`."),
    ("registru_fiscal_citeste", "str(e)"): (
        "C41 (lotul 6, găsit de garda 285): registrul pe profit trece prin `d101.genereaza` pe conexiunea firmei; refuzul motivat al "
        "generatorului (date de firmă lipsă, `ValueError`) e 422, ca la S1005 — nu cădere. Gardul: `core/test_registru_fiscal_conexiune.py`."),
    ("factura_primita_valideaza", "REFUZ_TERT_PLATITOR"): (
        "Deficiența 273c (lotul 6, comanda Costin 16.10.2026): „Câmpurile pe care importul nu le preia (terț plătitor, categorie) se "
        "semnalează pe factură ca «de completat»; terțul plătitor intră în D394.” Validarea cere tipul furnizorului (422 numit)."),
    ("factura_trimite_spv", "refuz_spre_ecran(r.get('mesaj'), COD_SPV_FARA_DREPT, 'conectare_spv')"): (
        "Deficiența 289 (lotul 6, comanda Costin 17.10.2026, verbatim în DECIZII): „SPV fără drept: fereastra firmei și refuzul «Trimite "
        "în SPV» spun exact asta, cu ce e de făcut.” Certificatul fără drept pe CUI-ul firmei e alt refuz decât „neconectat” (409, "
        "`COD_SPV_FARA_DREPT`, același buton spre Conectare SPV). Gardul: `core/test_spv_lot6.py`."),
    ("factura_primita_valideaza", "REFUZ_CATEGORIE_331"): (
        "Deficiența 273c: la factura primită cu taxare inversă (linii „AE”), validarea cere categoria produsului art.331 (codul D394)."),
    ("raportari_imagine", "str(e)"): (
        "C36 (15.10.2026): refuzul tipului (415) și al mărimii (413) vine din `fisiere_private.verifica`, cu numele fișierului și "
        "tipurile permise în cuvinte (`FisierRefuzat`), tradus în aceeași clasă de domeniu. Gardul: `core/test_fisiere_private.py`."),
    ("login", "_il.MESAJ_NECONFIRMAT"): (
        'Lotul 4 (comanda Costin 15.10.2026 pct.2, verbatim în DECIZII „Lotul 4”): „Până la confirmare nu se poate loga”. Login-ul eșuat al unei înregistrări libere neconfirmate, cu parola corectă a cererii, spune „confirmă emailul” (401) în loc de „email sau parolă greșite”. Gardul: `core/test_inregistrare_libera.py`, e2e `frontend_test/e2e/e2e_inregistrare_libera.py`.'),
    ("achizitie_ic", "str(e)"): (
        "Deficiența C7 generalizată (10.10.2026): refuzul motivat al creării facturii (`creeaza_factura` ridică `ValueError` — cod partener, serie, cotă) ieșea 500; tradus în 422, ca la `factura_creeaza`. Gardul: `test_refuz_generator_422::test_refuzul_emiterii_nu_ajunge_la_contabil_ca_500`."),
    ("achizitie_necorporala", "str(e)"): (
        "Deficiența C7 generalizată (10.10.2026): refuzul motivat al creării facturii (`creeaza_factura` ridică `ValueError` — cod partener, serie, cotă) ieșea 500; tradus în 422, ca la `factura_creeaza`. Gardul: `test_refuz_generator_422::test_refuzul_emiterii_nu_ajunge_la_contabil_ca_500`."),
    ("achizitie_neinregistrat", "str(e)"): (
        "Deficiența C7 generalizată (10.10.2026): refuzul motivat al creării facturii (`creeaza_factura` ridică `ValueError` — cod partener, serie, cotă) ieșea 500; tradus în 422, ca la `factura_creeaza`. Gardul: `test_refuz_generator_422::test_refuzul_emiterii_nu_ajunge_la_contabil_ca_500`."),
    # [lotul 11, 440, K] scoasă: (tenant_plan_conturi_adauga, 'Analiticul se scrie după contul sintetic, cu cifre după sep) — refuzul trece acum prin colectorul `ErorileFormularului` (perechea declarată de W3a / W3b)
    # [lotul 11, 440, K] scoasă: (tenant_plan_conturi_adauga, 'Simbolul contului are cel mult 10 caractere — s-a primit %r) — refuzul trece acum prin colectorul `ErorileFormularului` (perechea declarată de W3a / W3b)
    ("coada_adauga", "_blocaj"): (
        "Deciziile Costin 08.10.2026, U1 (+ completarea: D300, D394, D390) și V1 (D406): „«Trimite în coadă» e blocat” când TVA-ul "
        "D300 nu se potrivește cu rulajele 4427 / 4426 (TVA_DIFERA_DE_BALANTA), respectiv când totalurile GeneralLedgerEntries nu sunt "
        "rulajele balanței (D406_DIFERA_DE_BALANTA). Refuz 422 structurat, înaintea validatorului DUK. [§6 pct.7, R36] „compară "
        "validat cu validat; dacă există ciorne în lună, dau doar avertisment, nu blocaj” — cele două refuzuri au devenit unul "
        "(`_blocaj`, din `decizie_poarta`), ridicat numai fără ciorne în perioadă."),
    ("coada_adauga", "_bl_note"): (
        "Deficiența 436 (comanda Costin 10.2 pct.6, 21.10.2026, verbatim în DECIZII): „când declarația știe că are cifra greșită din note "
        "nevalidate, depunerea se blochează până la validare, cu motivul lângă buton, la toate declarațiile.” Refuz 422 structurat "
        "(NOTE_NEVALIDATE, notele numite, așteptarea de la 284), la declarațiile calculate din evidența validată "
        "(`coada_api.DECLARATII_DIN_EVIDENTA`)."),
    ("factura_contabilizeaza", "_nl.detaliu_refuz(e)"): (
        "Decizia Costin 08.10.2026, pct.2: „la contarea facturii se propune legarea cu NIR-ul nelegat de la același furnizor "
        "(preselecție permisă — dedusă din date, vizibilă, modificabilă). Dacă contabilul nu leagă, confirmă explicit «altă "
        "livrare»; nu se blochează.” Factura de marfă (371, global-valoric) cu NIR „fără factură” nelegat la același furnizor se "
        "refuză (422) STRUCTURAT — `cod` NIR_DE_LEGAT / NIR_NELEGABIL / COST_DIFERIT_DE_FACTURA, candidații, propunerea — până "
        "când omul alege NIR-ul sau „altă livrare”; înainte se conta tăcut și 371 se încărca de două ori."),
    ("factura_primita_valideaza", "_nl.detaliu_refuz(e)"): (
        "Decizia Costin 08.10.2026, pct.2 (aceeași ca la `factura_contabilizeaza`), pe calea SPV: alegerea NIR-ului se cere ÎNAINTE "
        "de validare — refuzul (422, structurat) anulează tot actul, ca factura să nu rămână validată fără notă."),
    # [lotul 11, 456] refuzul seriei lipsă a plecat din `chitanta_emite` în ajutorul comun cu Casa (`chitanta_serie_sau_refuz`)
    ("chitanta_serie_sau_refuz", 'refuz_spre_ecran(prefix + MESAJ_SERIE_CHITANTA_LIPSA, COD_SERIE_CHITANTA_LIPSA, "date_firma", "OMFP 2634/2015 anexa 1 pct.24")'): (
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
    # [lotul 11, 440, K] scoasă: (chitanta_emite, _amef.detaliu(e)) — refuzul trece acum prin colectorul `ErorileFormularului` (perechea declarată de W3a / W3b)
    # [lotul 11, 440, K] scoasă: (chitanta_emite, 'Data chitanței: %r nu e o dată din calendar. Se așteaptă fo) — refuzul trece acum prin colectorul `ErorileFormularului` (perechea declarată de W3a / W3b)
    # [lotul 11, 440, K] scoasă: (tenant_creeaza, {'mesaj': EMAIL_INVALID, 'erori_campuri': [{'camp': 'email_c) — refuzul trece acum prin colectorul `ErorileFormularului` (perechea declarată de W3a / W3b)
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
_MOTIV_VALIDARI_L4 = ("Lotul 4 (15.10.2026, DECIZII „Lotul 4”): verificările formularului de înregistrare (bifa termenilor, parola, "
                      "emailul) sunt comune căii cu invitație și celei libere, deci stau în `uc_auth._valideaza_formularul`, chemat "
                      "de `register` înaintea oricărei scrieri — același refuz, același cod (400).")
_MOTIV_C36 = ("C36 / 270d (comanda Costin 15.10.2026, verbatim în DECIZII „Lotul 5”): capturile sesizărilor nu se mai scriu în directorul "
              "servit public (`<static>/raportari`, deschise fără autentificare), ci în depozitul privat `core/fisiere_private.py` — "
              "`salveaza` verifică tipul DUPĂ CONȚINUT și limita (`verifica`), scrie fișierul și rândul lui din `public.fisiere_private` "
              "(în locul lui `raportari_api.adauga_atasament` și al tabelei `raportari_atasamente`). Gardul: `core/test_fisiere_private.py`.")
PERECHI_MUTATE_IN_AJUTOR = {
    ("raportari_imagine", "'Doar capturi de ecran (PNG, JPG, WEBP).'"): ("salveaza", _MOTIV_C36),
    ("raportari_imagine", "'Imaginea e prea mare (max 8MB).'"): ("salveaza", _MOTIV_C36),
    ("raportari_imagine", "mesaj_din_cod(r.get('cod'))"): ("salveaza", _MOTIV_C36 + " Refuzul `MESAJ_INEXISTENT` al lui "
                                                           "`adauga_atasament` a ieșit cu el: mesajul e verificat mai sus (404), în aceeași tranzacție."),
    ("register", "'Trebuie să accepți Termenii și condițiile pentru a crea contul.'"): ("_valideaza_formularul", _MOTIV_VALIDARI_L4),
    ("register", "_nucleu.PAROLA_MESAJ"): ("_valideaza_formularul", _MOTIV_VALIDARI_L4),
    ("register", "EMAIL_INVALID"): ("_valideaza_formularul", _MOTIV_VALIDARI_L4),
    ("register", "'Termenii și condițiile nu se pot citi acum, deci acordul tău nu s-ar putea consemna. Contul NU a fost creat. "
                 "Încearcă din nou peste câteva minute.'"): ("_valideaza_formularul", _MOTIV_VALIDARI_L4),
    ("register", "r['mesaj']"): ("_register_cu_invitatie", (
        "Lotul 4 (15.10.2026, DECIZII „Lotul 4”): refuzul crearii contului (`inregistreaza_cabinet`, ex. emailul deja inregistrat) "
        "pe calea cu invitatie sta in `uc_auth._register_cu_invitatie`, chemat de `register` — acelasi refuz, acelasi cod (400).")),
    ("asistent_creeaza", "EMAIL_EXISTA"): ("_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("client_acces_creeaza", "EMAIL_EXISTA"): ("_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
    ("portal_adauga_acces", "EMAIL_EXISTA"): ("_refuza_email_ocupat", _MOTIV_EMAIL_OCUPAT),
}


#: Perechi (cod, mesaj) SCOASE deliberat din funcție — refuzul nu mai are ce refuza acolo (operația lui a plecat în altă rută). Anti-vacuu:
#: `test_SCOASELE_perechi_chiar_lipsesc`.
PERECHI_SCOASE = {
    ("registratura_creeaza", "mesaje.get(rez.get('cod'), 'eroare')"): _MOTIV_440 + " Refuzurile de date ale înregistrării se adună în "
                                                                       "colector (`ErorileFormularului`), fiecare lângă câmpul ei.",
    ('achizitie_necorporala', "nomenclator_cerut('tip', TIPURI)"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('achizitie_necorporala', "f'Durata normală de funcționare (luni) obligatorie pentru {tip} (durata contractului/de utilizare, art. 28(9))'"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('chitanta_emite', "'suma trebuie să fie > 0'"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('facturi_emite', "'Denumirea beneficiarului e obligatorie pe factură. Completeaz-o înainte de emitere.'"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('salariat_beneficiu_lunar', "r['eroare']"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('tenant_plan_conturi_adauga', "'Completează atât simbolul, cât și denumirea contului.'"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('tenant_plan_conturi_adauga', "'Simbolul contului începe cu cifra clasei (1-9), ca toate conturile din planul general — am primit %r. Dacă e un analitic, scrie-l după contul sintetic (de exemplu 4111.01).' % simbol"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('tenant_plan_conturi_adauga', "'Simbolul contului se scrie din cifre, cu separator pentru analitic (`.`, `_`, `-`, `/`) — am primit %r.' % simbol"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('vanzare_ic', "'Lipsește codul de TVA al clientului. Fără el livrarea intracomunitară nu se poate verifica în VIES și nu ajunge în D390.'"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ('vector_salveaza', "{'mesaj': _mesaj, 'erori_campuri': [{'camp': _camp, 'mesaj': _mesaj}]}"): _MOTIV_440_W3A + " Înlocuită de colector (ErorileFormularului).",
    ("horeca_raport_z", "'numerar + card trebuie să fie egal cu totalul pe cote'"): _MOTIV_102_8B + " Pereche înlocuită (PERECHI_ADAUGATE).",
    ("cv_barcode_set", "rez['eroare']"): _MOTIV_C73_U2 + " Verificarea prealabilă (400 „codul de bare există deja la alt articol”) a ieșit: "
                                         "dublura o refuză constrângerea, prin `chei_unice.refuza_dublura`, cu articolul numit (PERECHI_ADAUGATE).",
    ("s1005_xml", "str(e)"): _MOTIV_C69 + " Pereche înlocuită de expresia cu `RefuzGenerare` (PERECHI_ADAUGATE).",
    ("s1005_valideaza", "str(e)"): _MOTIV_C69 + " Pereche înlocuită de expresia cu `RefuzGenerare` (PERECHI_ADAUGATE).",
    ("s1003_xml", "str(e)"): _MOTIV_C69 + " Pereche înlocuită de expresia cu `RefuzGenerare` (PERECHI_ADAUGATE).",
    ("s1003_valideaza", "str(e)"): _MOTIV_C69 + " Pereche înlocuită de expresia cu `RefuzGenerare` (PERECHI_ADAUGATE).",
    ("factura_trimite_spv", "str(e)"): _MOTIV_C69 + " Pereche înlocuită de `e.detaliu() if getattr(e, 'ecran', None) else str(e)`.",
    ("declaratie_genereaza", "str(e)"): (
        "Deficiența 431 (comanda Costin 10.1, 20.10.2026): „mesajul de refuz trimite la ce lipsește” — refuzul generatorului nu mai e "
        "numai text: `e.detaliu() if isinstance(e, RefuzGenerare) else str(e)` (PERECHI_ADAUGATE), același cod 422."),
    ("declaratie_valideaza", "str(e)"): (
        "Deficiența 431 (comanda Costin 10.1, 20.10.2026): ca la `declaratie_genereaza` — refuzul D205 cu nota de deschis ajunge ca obiect; "
        "pereche înlocuită de expresia cu `RefuzGenerare` (PERECHI_ADAUGATE), același cod 422."),
    ("rip_import_incarca", "'import eșuat: ' + str(rez['erori'][0].get('motiv', 'eroare la scriere'))"): (
        _MOTIV_82 + " Deficiența 372: previzualizarea nu mai scrie, deci nu mai poate eșua la scriere; refuzul scrierii e în "
        "`rip_import_salveaza` (`DateInvalide`, 422), după ce contabilul a văzut rândurile."),
}


def test_SCOASELE_perechi_chiar_lipsesc():
    """Anti-vacuu pe PERECHI_SCOASE: perechea declarată scoasă nu mai e ridicată de funcția din stratul use-case."""
    harta = _harta_cod()
    uc_dupa_nume = {nume: nod for (_mod, nume), nod in _module_uc().items()}
    for (fn_nume, msg_repr), motiv in PERECHI_SCOASE.items():
        assert len(motiv) > 80
        corp = uc_dupa_nume.get(fn_nume)
        assert corp is not None, "%s: funcția declarată nu există în stratul use-case" % fn_nume
        assert not (_forme_mesaj(msg_repr) & {p[1] for p in perechi_noi(corp, harta)}), (
            "%s: perechea declarată scoasă (%s) e tot acolo" % (fn_nume, msg_repr))


def test_MUTARILE_in_ajutor_chiar_cheama_ajutorul():
    """Anti-vacuu: o mutare declarată fără apelul ajutorului ar scuza un refuz PIERDUT."""
    import ast as _ast
    from core import scan_sql_efectiv as _ef
    for (fn_nume, _mesaj), (ajutor, motiv) in PERECHI_MUTATE_IN_AJUTOR.items():
        assert len(motiv) > 80
        _cale, _nod = _ef.functia(fn_nume)
        chemate = {x.func.attr if isinstance(x.func, _ast.Attribute) else x.func.id for x in _ast.walk(_nod)
                   if isinstance(x, _ast.Call) and isinstance(x.func, (_ast.Attribute, _ast.Name))}   # [lotul 4] și ajutor local
        assert ajutor in chemate, "%s: mutarea declarată în %s nu e în cod" % (fn_nume, ajutor)


_MOTIV_430D = (
    "Lotul 10, deficiența 430d (comanda Costin 20.10.2026: pe nota de dividende „scrie «sursa: facturile»”) — clasa: notele scrise "
    "din Operațiuni speciale își scriu sursa lor, `operatiuni` („operațiunile speciale”), prin `repo_contabilitate.nota_operatiune_ciorna`"
    "; același INSERT (data, descriere, ciornă) și același document intern numerotat ca `nota_facturi_ciorna` / `nota_banca_ciorna` / "
    "`nota_casa_ciorna` / `nota_salarii_ciorna`, plus documentul extern când operația îl are (hotărârea AGA, 430c).")

#: Apeluri INLOCUITE deliberat, cu motivul. Nu sunt pierderi: numele s-a schimbat, iar inlocuitorul
#: face STRICT MAI MULT decat cel vechi. Orice alt apel dispărut pica in continuare.
APELURI_INLOCUITE = {
    ("achizitie_agricultor", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("decontare_valuta", "nota_banca_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_tva_incasare", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("export_extracomunitar", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("import_extracomunitar", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_asociati", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_avans", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_bacsis", "nota_casa_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_chirie", "nota_facturi_ciorna_2"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_contract_special", "nota_salarii_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_credit", "nota_banca_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_decont_deplasare", "nota_casa_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_inventariere", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_leasing", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_lichidare", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_obiect_inventar", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_ong", "nota_casa_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_perisabilitati", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_productie", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_provizion_ep", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_sgr", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_sponsorizare_ep", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("nota_subventie", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("reevaluare_imobilizare", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("vanzare_agricultor", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("vanzare_aur_investitii", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("vanzare_marja", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("vanzare_marja_turism", "nota_facturi_ciorna"): ("nota_operatiune_ciorna", _MOTIV_430D),
    ("solduri_incarca", "extrage_balanta"): (
        "extrage_balanta_detaliat",
        _MOTIV_82 + " Deficiențele 343–344: previzualizarea balanței poartă numărul rândului din fișier, coloanele recunoscute, rândurile "
        "ignorate cu motivul lor — `extrage_balanta_detaliat` face tot ce făcea `extrage_balanta`, plus astea."),
    ("rip_import_incarca", "extrage_operatiuni"): (
        "extrage",
        _MOTIV_82 + " Deficiența 372: `rip_migrare_api.extrage` întoarce FIECARE rând citit, cu valorile din fișier lângă cele "
        "interpretate (data 2026-13-01 nu mai ajunge la baza de date), în loc de operațiunile deja filtrate."),
    ("bon_aproba", "round"): (
        "_q",
        "Deficiența 280 (lotul 6, comanda Costin 16.10.2026, verbatim în DECIZII): valoarea fără TVA a liniei bonului (× factor) e o sumă "
        "NOUĂ care intră în notă — rotunjire aritmetică (`common._q`, ROUND_HALF_UP), nu `round()` la par. Gardul: "
        "`core/test_rotunjire_fiscala.py::test_rotunjirea_in_toata_aplicatia_e_aritmetica_sau_motivata`."),
    ("banca_rec_import", "parse_extras"): (
        "citeste_extras",
        "Deficiența 277 / 276b (lotul 6): importul extrasului citește și contul și soldurile (`banca_parser.citeste_extras`), nu numai "
        "tranzacțiile; `parse_extras` a rămas numai lista tranzacțiilor din `citeste_extras`."),
    ("reset_parola_cere", "strip"): (
        "nume_de_salut",
        "Deficiența 269 (Lotul 5, 15.10.2026: „salutul ia ultimul cuvânt din nume”): numele din salutul emailului de resetare vine din "
        "funcția comună `common.nume_de_salut` (prenumele scris separat, altfel numele întreg) — `.strip()` e în interiorul ei."),
    ("s1005_valideaza", "TemporaryDirectory"): (
        "valideaza",
        "Deficiența 222 (comanda Costin 10.10.2026, caseta brută «ok»): directorul temporar al validării bilanțului (`TemporaryDirectory`) trăiește acum în `duk.valideaza` (`mkdtemp` + `rmtree` în `finally`), sursa unică a validatorului — un apel `valideaza` îl înlocuiește."),
    ("s1003_valideaza", "TemporaryDirectory"): (
        "valideaza",
        "Deficiența 222 (comanda Costin 10.10.2026, caseta brută «ok»): directorul temporar al validării bilanțului (`TemporaryDirectory`) trăiește acum în `duk.valideaza` (`mkdtemp` + `rmtree` în `finally`), sursa unică a validatorului — un apel `valideaza` îl înlocuiește."),
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
    # [lotul 11, C78] perechea R187 („vanzare_ic”, nota_facturi_ciorna -> nota_facturi_cu_factura) a ieșit: nota proprie nu se mai
    # scrie deloc — vezi APELURI_SCOASE (contarea de la emitere e singura notă a facturii)
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
    ("declaratii_tipuri", "get"): (
        "periodicitate_firma",
        "Deficiența C2 (10.10.2026): selectorul oferea D406 lunar neplătitorului (OPANAF 1783/2021 anexa 4 pct.3: trimestrial). "
        "`_vec.get(\"tip_decont\")` nu mai e citit în use-case: `periodicitate_firma` primește vectorul întreg și citește din el "
        "`tip_decont` ȘI `platitor_tva` (`common.perioada_d406_tip`) — aceeași citire, plus plătitorul."),
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
    "factura_primita_valideaza": (("core/uc_tenants.py", "_factura_importata"), "Lotul 11, C79 (subagentul Y): importul facturii din XML trece numai prin `uc_tenants._factura_importata` — `_factura_din_parsat` (facturi + linii, dedup) ȘI TVA-ul pe cote al facturii (BG-23, `factura_tva_cote`), de pe care se contează și se declară TVA-ul (CF art.299 alin.(1) lit.a). Gardul: `core/test_lot11_y_tva_primita.py::test_importul_trece_numai_prin_factura_importata`."),
    "import_efactura": (("core/uc_tenants.py", "_factura_importata"), "Lotul 11, C79 (subagentul Y): importul facturii din XML trece numai prin `uc_tenants._factura_importata` — `_factura_din_parsat` (facturi + linii, dedup) ȘI TVA-ul pe cote al facturii (BG-23, `factura_tva_cote`), de pe care se contează și se declară TVA-ul (CF art.299 alin.(1) lit.a). Gardul: `core/test_lot11_y_tva_primita.py::test_importul_trece_numai_prin_factura_importata`."),
    'tenant_amortizare': (("core/amortizare_lunii.py", "linii"), (
        "Lotul 11, deficiența 451 (comanda Costin 11.1 pct.6): corpul buclei rândurilor amortizării (`repo_mijloace_fixe.de_amortizat`, "
        "`amortizare_luna` pe metoda reală — CF art.28 —, `append`, `float`) a plecat în `amortizare_lunii.linii`, sursa unică cu "
        "regenerarea pe uscat a ciornei depășite (`ciorne_depasite`). Gardul: `core/test_r36_evidenta.py -k amortiz`.")),
    'facturi_emite': (("core/facturi_api.py", "poarta_marfa_ceruta"), (
        "C63 (decizia Costin 19.10.2026, DECIZII „Închiderea lotului 9” pct.2): condiția întrebării „Pleacă marfa acum?” (factură, linie "
        "cu articol, nu din bon) e una singură pentru emitere și transformare: `facturi_api.poarta_marfa_ceruta` (`any(...)` a plecat "
        "acolo). Gardul: `core/test_c63_proforma_transformata.py::test_c63_conditia_intrebarii_e_una_singura`.")),
    'coada_adauga': (("core/uc_coada.py", "_anunta_validatorii"), (
        'Deficiența 339 (comanda Costin 8.1, 18.10.2026, DECIZII „Comanda 8.1”): „de validat” pentru o declarație pleacă numai cu validarea în doi efectivă (`patru_ochi_stare(...)["efectiv"]`), iar o excepție la trimitere se scrie în jurnal; anunțul a ieșit din corp în `uc_coada._anunta_validatorii`. Gardul: `core/test_339_340_notificari.py`.')),
    'asistent_creeaza': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'cabinet_solicitari_raspunde': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'client_acces_creeaza': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'magic_link_cere': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'pachet_poveste_set': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'portal_adauga_acces': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'portal_schimba_email': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    'reset_parola_cere': (("core/observare.py", "trimite_email_html_sau_semnaleaza"), (
        'C34 (15.10.2026, DECIZII „Lotul 2” pct.4): `trimite_email_html` întoarce `False` la eșec și nu aruncă; trimiterea și semnalarea eșecului (`esec_secundar`) stau acum în `observare.trimite_email_html_sau_semnaleaza` — sursa unică. Gardul: `core/test_email_html_rezultat.py`, `core/test_esec_trimitere_email.py`.')),
    "s1005_valideaza": (("core/duk.py", "valideaza"), (
        "Deficiența 222 (comanda Costin 10.10.2026): „mesajul de confirmare apare ca o casetă brută «ok»” — bilanțul rula DUKIntegrator separat și trimitea conținutul fișierului DUK („ok”) ca „erori”, afișate într-o casetă sub „Validare fără erori”. Validarea trece prin sursa unică `duk.valideaza` (fișierul temporar, rularea, citirea rezultatului și normalizarea „ok” trăiesc acolo).")),
    "s1003_valideaza": (("core/duk.py", "valideaza"), (
        "Deficiența 222 (comanda Costin 10.10.2026): „mesajul de confirmare apare ca o casetă brută «ok»” — bilanțul rula DUKIntegrator separat și trimitea conținutul fișierului DUK („ok”) ca „erori”, afișate într-o casetă sub „Validare fără erori”. Validarea trece prin sursa unică `duk.valideaza` (fișierul temporar, rularea, citirea rezultatului și normalizarea „ok” trăiesc acolo).")),
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


#: [15.10.2026, lotul 4] Corpul extras în MAI MULTE ajutoare: `register` (înregistrarea cu invitație SAU liberă, cu confirmare) are
#: verificările formularului, calea invitației și pașii de după cont (bun venit, anunț, firma din CUI) în ajutoare ale aceluiași modul,
#: folosite și de `confirma_inregistrarea` (fără dubluri). Creditul se dă în ORDINEA de aici: un ajutor chemat dintr-unul de mai sus
#: primește creditul după acela (pe apel efectiv, ca în tabelul de sus). Anti-vacuu: `test_EXTRAGERILE_declarate_chiar_cheama_ajutorul`.
_MOTIV_LOTUL_4 = ('Lotul 4 (comanda Costin 15.10.2026, verbatim în DECIZII „Lotul 4”): înregistrarea liberă cu confirmarea emailului. '
                  '`register` are acum două căi (invitația, ca în lotul 2; formularul liber, care devine o cerere în așteptare); '
                  'verificările formularului (`_valideaza_formularul`), calea invitației (`_register_cu_invitatie`) și pașii de după '
                  'contul nou (`_dupa_cont_nou`, `_anunta_cabinet_nou`) sunt ajutoare comune cu confirmarea (`confirma_inregistrarea`). '
                  'Trimiterea emailului: `observare.trimite_email_html_sau_semnaleaza` (C34).')
APELURI_EXTRASE_IN_AJUTOARE = {
    "chitanta_emite": ((("core/uc_tenants.py", "chitanta_serie_sau_refuz"), ("core/uc_tenants.py", "chitanta_scrie")), (
        "Lotul 11, deficiența 456 (comanda Costin 11.3 pct.3, verbatim în DECIZII): „încasarea în numerar de la o firmă se salvează fără "
        "chitanță. Emite automat chitanța, cu seria firmei și PDF.” Seria firmei (cu refuzul numit spre Date firmă) și scrierea chitanței "
        "(cu factura încasată integral) au plecat din `chitanta_emite` în `uc_tenants.chitanta_serie_sau_refuz` / `chitanta_scrie`, "
        "ajutoarele comune cu încasarea facturii din Casă (`casa_adauga` -> `chitante_pe_incasare`). Gardul: "
        "`core/test_lot11_a455_chitanta_incasare.py`.")),
    "nota_asociati": ((("core/uc_tenants.py", "_dividend_propus"),), (
        "Lotul 10, deficiența 430 (comanda Costin 20.10.2026): nota de dividende se face din datele firmei — asociații și cotele la data "
        "hotărârii, contul care are profitul și verificarea că dividendul nu-l depășește, împărțirea pe asociați, hotărârea ca document. "
        "Calculul (`nota_dividend`, data, felul anual / interimar prin `bifa`) a plecat în `uc_tenants._dividend_propus`, ajutorul comun "
        "cu propunerea afișată înainte de generare (`dividende_impartire`). Gardul: `core/test_lot10_dividende.py`.")),
    "proforma_transforma": ((("core/uc_tenants.py", "linii_din_proforma"), ("core/uc_tenants.py", "antet_din_proforma")), (
        "C63 (Code, 19.10.2026, DECIZII „Lotul 9: C57–C64”): liniile și antetul facturii născute din proformă / aviz se citesc în "
        "`uc_tenants.linii_din_proforma` / `antet_din_proforma` (cele 8 `.get` au plecat acolo, cu adresa, localitatea, județul, "
        "unitatea, contul de venit și articolul). Gardul: `core/test_c63_proforma_transformata.py`.")),
    "raportari_imagine": ((("core/fisiere_private.py", "salveaza"),), _MOTIV_C36),
    "register": ((("core/uc_auth.py", "_valideaza_formularul"), ("core/uc_auth.py", "_register_cu_invitatie"),
                  ("core/uc_auth.py", "_dupa_cont_nou"), ("core/uc_auth.py", "_anunta_cabinet_nou"),
                  ("core/observare.py", "trimite_email_html_sau_semnaleaza")),
                 _MOTIV_LOTUL_4),
}

#: [17.10.2026, lotul 7] Apeluri făcute de MAI PUȚINE ori, deliberat: (funcție, apel) -> (câte mai puțin, motivul). Mai strâns decât
#: APELURI_SCOASE (apelul rămâne, numai numărul scade cu exact cât e declarat). Anti-vacuu: `test_REDUCERILE_declarate_chiar_sunt_in_cod`.
_MOTIV_CF_CUI = ("Lotul 11, decizia Costin 10.3 pct.4 (CUI-ul fără „RO” și fără spații): normalizarea locală a codului fiscal a trecut în "
                 "`cui_forma.stocare` (o singură formă, cu paritatea Python–SQL); gardul core/test_lot11_cf_cui_forma_unica.py.")
APELURI_REDUSE = {
    ("cv_barcode_set", "get"): (1, _MOTIV_C73_U2 + " `rez.get(\"eroare\")` a ieșit cu verificarea prealabilă: `set_barcode` nu mai "
                                "întoarce refuzul ca valoare, ridică `CheieDublata`; rămâne `corp.get(\"barcode\")`."),
    ("rip_import_incarca", "str"): (1, _MOTIV_82 + " Deficiența 372: mesajul „import eșuat: …” (din eșecul scrierii) a ieșit odată cu "
                                    "scrierea; rămâne `str(e)` pe fișierul necitit."),
    ("rip_import_incarca", "HTTPException"): (1, _MOTIV_82 + " Deficiența 372: refuzul 422 la eșecul scrierii a ieșit din previzualizare "
                                              "(e în `rip_import_salveaza`, `DateInvalide`); rămân refuzurile fișierului necitit / gol."),
    ("declaratii_tipuri", "tipuri"): (1, (
        "Deficiența 301 (comanda Costin 17.10.2026 7.2, verbatim în DECIZII): declarațiile pe care forma firmei nu le poate datora nici nu "
        "apar în selector. Lista tipurilor se citește O DATĂ, filtrată după forma firmei, și aceeași listă dă `tipuri` și `periodicitate` "
        "(înainte: `declaratii_api.tipuri()` de două ori, nefiltrat).")),
    # [lotul 11, 443, comanda Costin 11.1 pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”] „contravaloare
    # factura …” de pe chitanță: lipirea de mână (`str(r[0]) + nrtxt` după `nrtxt.startswith(str(r[0]))`) a ieșit; o face `pdf_util.serie_nr`
    # [lotul 11, W3a] („chitanta_emite”, „str”) scos: `str` a revenit la 3 apeluri (colectorul 440 refolosește conversia)
    ('achizitie_neinregistrat', 'ValueError'): (2, _MOTIV_440_W3A + " Refuzurile de date nu mai ridică unul câte unul: se adună în colector."),
    ('tenant_plan_conturi_adauga', 'HTTPException'): (3, _MOTIV_440_W3A + " Refuzurile de date nu mai ridică unul câte unul: se adună în colector."),
    ("bon_facturi_candidate", "strip"): (2, _MOTIV_CF_CUI),   # [lotul 11, CF] 3 -> 1: rămâne un `strip`
}

#: [15.10.2026, lotul 4] Apeluri SCOASE deliberat, cu motivul. Anti-vacuu: `test_SCOASELE_declarate_chiar_lipsesc`.
APELURI_SCOASE = {
    # [lotul 11, subagentul CF; decizia Costin 10.3 pct.4: „CUI-ul se păstrează fără «RO» și fără spații”] normalizarea locală a codului
    # fiscal (`.strip().upper().replace("RO", "")`, un dialect care scotea „RO” de oriunde din text) a trecut în forma unică
    # `cui_forma.stocare`; gardul: `core/test_lot11_cf_cui_forma_unica.py`
    ("_anaf_tva_check", "strip"): _MOTIV_CF_CUI,
    ("_anaf_tva_check", "replace"): _MOTIV_CF_CUI,
    ("bon_facturi_candidate", "replace"): _MOTIV_CF_CUI,
    ("bon_facturi_candidate", "upper"): _MOTIV_CF_CUI,
    ("register", "replace"): _MOTIV_CF_CUI,
    # [lotul 11, 440 / W3a, K] scoase de tot (nu reduse): toate `ValueError`-urile de date ale funcției au trecut în colector
    ("achizitie_ic", "ValueError"): _MOTIV_440_W3A + " Toate cele 3 refuzuri de date se adună în colector (`ErorileFormularului`).",
    ("achizitie_necorporala", "ValueError"): _MOTIV_440_W3A + " Toate cele 3 refuzuri de date se adună în colector (`ErorileFormularului`).",
    ("achizitie_taxare_inversa", "ValueError"): _MOTIV_440_W3A + " Ambele refuzuri de date se adună în colector (`ErorileFormularului`).",
    # [lotul 11, C78] nota proprie a livrării intracomunitare dubla contarea de la emitere (4111 = 707 de două ori pe aceeași factură)
    ("vanzare_ic", "nota_facturi_ciorna"): (
        "Deficiența C78 (lotul 11): `vanzare_ic` scria, după `emite_factura`, încă o notă 4111 = 707 pe aceeași factură (R187: "
        "`nota_facturi_cu_factura`, înlocuitorul acestui apel) — venitul și creanța dublate. Nota livrării e acum contarea făcută la "
        "emitere (`facturi_api._conteaza_la_creare`, `fres[\"contare\"][\"inregistrare_id\"]`); OMFP 2634/2015 pct.58 lit.c. Gardul: "
        "`core/test_lot11_x_c78_vanzare_ic.py`."),
    ("vanzare_ic", "adauga_linie_client"): (
        "Deficiența C78 (lotul 11): rândul 4111 = 707 al notei proprii a livrării intracomunitare a ieșit odată cu nota — rândul e scris "
        "de contarea de la emitere (`contare_facturi.contabilizeaza`, pe contul de venit al liniei). Gardul: "
        "`core/test_lot11_x_c78_vanzare_ic.py`."),
    ("horeca_raport_z", "abs"): (_MOTIV_102_8B + " `abs(float(total) - …) > 0.01` a ieșit: egalitatea se verifică exact, în Decimal "
                                 "(`raport_z.mesaj_plata_diferita` primește sumele)."),
    ("solduri_incarca", "round"): (_MOTIV_82 + " Totalurile previzualizării se adună acum în `Decimal` (nu `round()` pe float), "
                                   "aceeași regulă ca restul sumelor de bani."),
    ("mijloace_import_incarca", "round"): (_MOTIV_82 + " Totalul valorii de intrare se adună în `Decimal`, nu prin `round()` pe float; "
                                           "reconcilierea cu balanța (359) e în `reconciliere_balanta`."),
    ("rip_import_incarca", "get"): (_MOTIV_82 + " Deficiența 372: previzualizarea nu mai scrie, deci nu mai citește rezultatul scrierii "
                                    "(`rez.get(...)`) — salvarea e `rip_import_salveaza`."),
    ("rip_import_incarca", "get_conn"): (_MOTIV_82 + " Deficiența 372: previzualizarea nu deschide nicio conexiune; scrierea și marcajul "
                                         "stratului au trecut în `rip_import_salveaza`, după ce contabilul a văzut rândurile."),
    ("rip_import_incarca", "importa"): (_MOTIV_82 + " Deficiența 372: `importa` se cheamă din `rip_import_salveaza`, după previzualizare, "
                                        "și reverifică fiecare rând înainte de scriere."),
    ("rip_import_incarca", "seteaza_status"): (_MOTIV_82 + " Deficiența 372: marcajul stratului RIP (gata / în lucru) se pune la salvare "
                                               "(`rip_import_salveaza`), nu la citirea fișierului."),
    ("raportari_imagine", "lower"): (_MOTIV_C36 + " Tipul nu se mai ia din `content_type` (pe care îl trimite browserul, deci îl "
                                     "poate minți) — `lower()` pe el a ieșit."),
    ("raportari_imagine", "HTTPException"): (_MOTIV_C36 + " Cele două refuzuri separate (415 tip, 413 mărime) sunt acum UNUL, cu clasa "
                                             "aleasă după `FisierRefuzat.cod`; refuzul 400 al lui `adauga_atasament` a ieșit cu el."),
    ("raportari_imagine", "get"): (_MOTIV_C36 + " Au ieșit `harta_extensiilor.get(tip)` (extensia se ia din tipul citit din conținut) "
                                   "și `r.get(...)` pe rezultatul lui `adauga_atasament`."),
    ("raportari_imagine", "adauga_atasament"): (_MOTIV_C36 + " Rândul se scrie în `public.fisiere_private`, din `salveaza`."),
    ("raportari_imagine", "mesaj_din_cod"): (_MOTIV_C36 + " Era mesajul refuzului lui `adauga_atasament`."),
    ("register", "_trimite_brevo"): (
        "Lotul 4 pct.4 (comanda Costin 15.10.2026): alerta internă „cont nou de cabinet” (`observare._trimite_brevo`, text fără date, "
        "către ICONTA_ALERTA_EMAIL) e înlocuită de anunțul cerut — un email HTML către superadmin, cu cabinetul și calea "
        "(`_anunta_cabinet_nou`, prin `trimite_email_html_sau_semnaleaza`)."),
    ("register", "strftime"): (
        "Lotul 4 (DS cap.4, verificatorul BACKEND_UI_BRUT): data din anunțul de cabinet nou — destinată omului — se formatează prin "
        "formatorul canonic `pdf_util.data_ro(..., \"cu_ora\")`, nu cu `strftime` local; alerta veche avea `strftime` pe o dată ISO."),
    ("register", "trebuie_trimisa"): (
        "Lotul 4 pct.4 (comanda Costin 15.10.2026: „La fiecare cabinet nou confirmat primesc un email de anunț”): alerta „cont nou de "
        "cabinet” trecea prin pragul anti-flood de 15 minute din memoria procesului (`observare.trebuie_trimisa`) — al doilea cabinet "
        "din același sfert de oră nu mai era anunțat. Anunțul (`_anunta_cabinet_nou`) pleacă acum la FIECARE cabinet."),
    ("chitanta_emite", "startswith"): (
        "Deficiența 443 (comanda Costin 11.1 pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”): verificarea "
        "„numărul facturii conține deja seria” de pe chitanță a ieșit odată cu lipirea de mână — o face `pdf_util.serie_nr`."),
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
    """Anti-vacuu: o extragere declarată fără apelul ajutorului (sau cu un ajutor inexistent) ar scuza apeluri pierdute. Pentru
    tabelul cu mai multe ajutoare: primul e chemat de funcție, fiecare următor de funcție sau de unul dintre ajutoarele dinaintea lui."""
    import ast as _ast
    from core import scan_sql_efectiv as _ef
    for fn_nume, (perechi, motiv) in APELURI_EXTRASE_IN_AJUTOARE.items():
        assert len(motiv) > 80
        _cale, _nod = _ef.functia(fn_nume)
        chemate = {x.func.attr if isinstance(x.func, _ast.Attribute) else x.func.id for x in _ast.walk(_nod)
                   if isinstance(x, _ast.Call) and isinstance(x.func, (_ast.Attribute, _ast.Name))}
        for cale, ajutor in perechi:
            assert ajutor in chemate, "%s: extragerea declarată în %s nu e chemată nici de funcție, nici de un ajutor de mai sus" % (
                fn_nume, ajutor)
            ale_lui = _apeluri_ajutor(cale, ajutor)
            assert ale_lui, "%s: ajutorul %s nu cheamă nimic" % (fn_nume, ajutor)
            chemate |= set(ale_lui)
    for fn_nume, ((cale, ajutor), motiv) in APELURI_EXTRASE_IN_AJUTOR.items():
        assert len(motiv) > 80
        assert _apeluri_ajutor(cale, ajutor), "%s: ajutorul %s nu cheamă nimic" % (fn_nume, ajutor)
        _cale, _nod = _ef.functia(fn_nume)
        # ajutorul poate fi în alt modul (`_uc_comun.controale_inchidere(...)`) sau în același (`campuri_rezultat(...)`, retest 08.10)
        chemate = {x.func.attr if isinstance(x.func, _ast.Attribute) else x.func.id for x in _ast.walk(_nod)
                   if isinstance(x, _ast.Call) and isinstance(x.func, (_ast.Attribute, _ast.Name))}
        assert ajutor in chemate, "%s: extragerea declarată în %s nu e în cod" % (fn_nume, ajutor)


def test_SCOASELE_declarate_chiar_lipsesc():
    """Anti-vacuu pe APELURI_SCOASE: apelul declarat scos lipsește din funcție ȘI din ajutoarele ei declarate (altfel tabelul ar scuza
    o pierdere care nu s-a întâmplat — sau ar ascunde una care s-a întors)."""
    import ast as _ast
    from core import scan_sql_efectiv as _ef
    for (fn_nume, apel), motiv in APELURI_SCOASE.items():
        assert len(motiv) > 80
        _cale, _nod = _ef.functia(fn_nume)
        toate = {x.func.attr if isinstance(x.func, _ast.Attribute) else x.func.id for x in _ast.walk(_nod)
                 if isinstance(x, _ast.Call) and isinstance(x.func, (_ast.Attribute, _ast.Name))}
        for cale, ajutor in APELURI_EXTRASE_IN_AJUTOARE.get(fn_nume, ((),))[0]:   # [lotul 6] fără ajutoare: nicio pereche (era `(None, None)`)
            if cale:
                toate |= set(_apeluri_ajutor(cale, ajutor))
        assert apel not in toate, "%s: apelul declarat scos (%s) e tot acolo" % (fn_nume, apel)


def test_REDUCERILE_declarate_chiar_sunt_in_cod():
    """Anti-vacuu pe APELURI_REDUSE: apelul e făcut acum EXACT cu `n` mai puțin decât în BAZA (nici scos de tot — atunci e o scoatere —,
    nici înapoi la numărul vechi — atunci declarația ar scuza o pierdere viitoare)."""
    harta, uc = _harta_cod(), _module_uc()
    vechi = {n.name: n for n in ast.parse(_sursa_veche()).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    nou = {n.name: n for n in ast.parse(io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()).body
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for (fn, apel), (n, motiv) in APELURI_REDUSE.items():
        assert len(motiv) > 80 and n > 0
        inainte = _apeluri(vechi[fn], harta).get(apel, 0)
        acum = _apeluri(uc[_tinta_invelisului(nou[fn])], harta).get(apel, 0)
        assert acum >= 1 and acum == inainte - n, (fn, apel, inainte, acum, n)


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
    'f"ANAF indisponibil sau a refuzat cererea: {e}"': ("anaf_api.mesaj_indisponibil(e)",
        "Deficiența 317 (comanda Costin 17.10.2026 7.2): același 502, fără textul bibliotecii HTTP pe ecran — ANAF a refuzat (cu codul "
        "lui) sau n-a răspuns. Gardul: `core/test_317_320_alerta_notificari.py`."),
    '"ANAF indisponibil: %s" % e': ("anaf_api.mesaj_indisponibil(e)",
        "Deficiența 317: același 502 la verificarea CUI, fără textul bibliotecii HTTP."),
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
    # [lotul 10, deficiența 402, clasa 410 — comanda Costin 10.2 pct.7b: „refuzurile ... spun doar «articolul» / «cantitatea»”] mesajul de
    # lângă câmp e o frază întreagă (gardul: `core/test_lot10b_402_mesaje_camp.py`); același refuz, același cod
    "Constant(value='an'), Constant(value='cerut, nu poate lipsi')": ("Constant(value='an'), Constant(value='Scrie anul rândului.')",
        "Deficiența 402, clasa 410 (comanda Costin 10.2 pct.7b): mesajul de câmp e o frază întreagă; același 400."),
    "Constant(value='exercitiu'), Constant(value='cerut, nu poate lipsi')": (
        "Constant(value='exercitiu'), Constant(value='Scrie exercițiul financiar (anul).')",
        "Deficiența 402, clasa 410 (comanda Costin 10.2 pct.7b): mesajul de câmp e o frază întreagă; același 400."),
    "Constant(value='cerut de normă, nu poate lipsi')": ("Constant(value='Completează câmpul cu o valoare validă: registrul o cere.')",
        "Deficiența 402, clasa 410 (comanda Costin 10.2 pct.7b): mesajul de câmp e o frază întreagă; același 400."),
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
    # [04.10.2026] mesajul vechi poate fi și o CONSTANTĂ NUMITĂ (`EMAIL_EXISTA`), nu doar un literal
    # [retest 08.10] abaterea = ACELAȘI cod, alt mesaj: se numără perechile noi pe codul ei, nu toate perechile noi ale
    # funcției (la `coada_depune` mai rămâne una pe 422, scoasă abia de CODURI_ADAUGATE, mai jos)
    # [Retest 2, 09.10.2026] perechile noi DECLARATE (PERECHI_ADAUGATE, scoase mai jos) nu sunt perechea abaterii: altfel o funcție
    # care are și o pereche adăugată pe același cod (`facturi_emite`: 422) n-ar mai putea purta nicio abatere de mesaj
    # [lotul 6, 16.10.2026] abaterile ACELEIAȘI funcții pe ACELAȘI cod se socotesc împreună: două mesaje rescrise pe 409
    # (`factura_trimite_spv`: diacriticele „deja trimisă” + refuzul SPV cu țintă de ecran) cereau fiecare o singură pereche nouă pe
    # cod, iar fiecare vedea două — deci nicio pereche nu se mai putea declara
    _tinte = set().union(*[_forme_mesaj(m) for (rut, m) in ABATERI if rut == nume]) if any(rut == nume for (rut, _m) in ABATERI) else set()
    _adaugate = {f for (r2, m2) in PERECHI_ADAUGATE if r2 == nume for f in _forme_mesaj(m2)}
    for _cod in sorted({p[0] for p in ramase_v if p[1] in _tinte}, key=str):
        v = [p for p in ramase_v if p[1] in _tinte and p[0] == _cod]
        n_cod = [p for p in ramase_n if p[0] == _cod and p[1] not in _adaugate]
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
    for (rut, mesaj), _motiv in PERECHI_SCOASE.items():
        if rut == nume:
            ramase_v = [p for p in ramase_v if p[1] not in _forme_mesaj(mesaj)]
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
        # [15.10.2026, lotul 4] corpul extras în mai multe ajutoare, creditate în ordine (vezi APELURI_EXTRASE_IN_AJUTOARE)
        for _cale_a, _ajutor in (APELURI_EXTRASE_IN_AJUTOARE.get(nume, ((), ""))[0]):
            _n_apel = acum.get(_ajutor, 0)
            # un ajutor din stratul use-case se numără ca ruta (refuzurile `_erori.*` = HTTPException, prin aceeași hartă); unul
            # din afara lui, ca în tabelul cu un singur ajutor
            _cheie_uc = (os.path.basename(_cale_a)[:-3], _ajutor)
            _ale = (_apeluri(uc[_cheie_uc], harta) if _cheie_uc in uc else _apeluri_ajutor(_cale_a, _ajutor))
            for k, v in _ale.items():
                acum[k] = acum.get(k, 0) + v * _n_apel
        for (_fn, _apel), _m in APELURI_SCOASE.items():
            if _fn == nume:
                inainte.pop(_apel, None)
        for (_fn, _apel), (_n, _m) in APELURI_REDUSE.items():
            if _fn == nume:
                inainte[_apel] = inainte.get(_apel, 0) - _n
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

    def noduri(n):
        # [lotul 10, 430] și ajutoarele din `uc_tenants` în care corpul a fost EXTRAS declarat (creditul de mai sus le numără la fel)
        ajut = [a for c, a in APELURI_EXTRASE_IN_AJUTOARE.get(n, ((), ""))[0] if c == "core/uc_tenants.py" and a in fn]
        return [fn[n]] + [fn[a] for a in ajut]
    lipsa = [n for n in BIFA_INLOCUIRI if n not in fn or not any(
        isinstance(x, ast.Call) and getattr(x.func, "attr", None) == "bifa" for nod in noduri(n) for x in ast.walk(nod))]
    assert lipsa == [], lipsa


#: [17.10.2026] Decoratori schimbați DELIBERAT, cu motivul (textul dintre decorator și `def`). Anti-vacuu: fiecare intrare chiar diferă de
#: BAZA — altfel se scoate.
DECORATORI_SCHIMBATI = {
    "tenant_amortizare": (
        "Deficiența 311 (comanda Costin 17.10.2026 7.2 pct.4, verbatim în DECIZII): „generarea amortizării (lunară și restantă) la «Poate "
        "pregăti»”. Comentariul de sub decorator spunea că ruta scrie nota `validata` DIRECT, motivul pentru „Poate valida” — fals de la "
        "R55 (26.08.2026: scrie CIORNA). Comentariul spune acum ce face ruta și de ce dreptul e „Poate pregăti”; nu e o declarație citită "
        "de vreun instrument (`grep -rn \"R55, 26.08.2026\" core scripts` — numai acest test)."),
}


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
    dif = [n for n in comune if vechi[n] != acum[n] and n not in DECORATORI_SCHIMBATI]
    assert all(vechi.get(n) != acum.get(n) for n in DECORATORI_SCHIMBATI), "o schimbare declarată nu mai e schimbare — scoate-o"
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
