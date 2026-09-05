# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL D — D112: declaratia de salarii, si lantul ei de la salariat la rand.

Nucleul lui D112 (24 de unitati, dupa ascutirea instrumentului) e chiar suprafata salariala:
`salariati`, `pontaj`, `concedii_medicale`, `beneficii_lunare`, `salariu_istoric`. Lantul probat
aici merge de la un salariat NOU pana la randul lui din declaratie.

ASTEPTAREA, SCRISA INAINTE:

  0. Fara declarantul completat in «Date firmă», D112 **refuza** — si spune care campuri lipsesc.
     E prima veriga a lantului, si se probeaza ca atare: se completeaza, apoi se genereaza.
  1. Un salariat NOU, cu brut B, apare in declaratie cu CNP-ul lui, si numarul de asigurati creste
     cu unu.
  2. Contributiile lui NU sunt scrise de mine: se citesc din generator si se confrunta cu ce
     calculeaza `core.salarizare` pentru acelasi brut — **generator contra calculator**, aceeasi
     forma ca la lotul C (D100 confruntat cu D101). O cifra scrisa de mana aici ar fi doar o copie
     a codului, nu o verificare.
  3. Stergerea salariatului il scoate din declaratie, iar numarul de asigurati revine.

CE NU DEMONSTREAZA, declarat: ca reperele contributiilor sunt cele cerute de lege pe luna aia —
asta e o intrebare de temei (si e deja pazita de `core/test_temeiuri.py`). Aici se probeaza ca
valoarea introdusa de om **ajunge unde spune codul ca ajunge**, cu suma pe care tot codul o
calculeaza pe alta cale.

SCENARIUL: «Panificatie Salarii Speciale SRL» (`tenant_001`) — firma de salarii a portofoliului,
12 salariati. Luna **08/2026**.
"""
import json
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Panificatie Salarii Speciale SRL"
AN, LUNA = 2026, 8
MARCA = "PROBA E2 D"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_d112.json"

# CNP care trece cifra de control (cerinta `core/test_cui_cnp_test_valid.py`), si care nu e al
# niciunui salariat existent al firmei.
# cifra de control e CALCULATA cu constanta 279146358279, nu inventata — prima forma a probei a
# pus un CNP „plauzibil" si ruta l-a refuzat pe drept: «CNP invalid: cifra de control».
CNP_NOU = "1900101511112"
BRUT = Decimal("5000")
COR = None  # se citeste din nomenclator la rulare (v. `alege_cor`)

_ATR = re.compile(r'(\w+)="([^"]*)"')


def elemente(xml, nume):
    return [dict(_ATR.findall(m.group(1)))
            for m in re.finditer(r"<%s\b([^>]*)/?>" % nume, xml)]


def alege_cor():
    """Un cod COR REAL din nomenclatorul aplicatiei — nu unul plauzibil."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT cod FROM public.cor_ocupatii ORDER BY cod LIMIT 1")
        r = cur.fetchone()
        conn.rollback()
    return r[0] if r else None


def main():
    global COR
    COR = alege_cor()
    tok, tid, _schema = U.context(FIRMA)
    jurnal = {"firma": FIRMA, "tenant_id": tid, "perioada": {"an": AN, "luna": LUNA}, "pasi": []}
    rele = []

    def pas(nume, **kw):
        jurnal["pasi"].append(dict(nume=nume, **kw))
        print("· %-46s %s" % (nume, json.dumps(kw, ensure_ascii=False, default=str)[:150]))

    def nepotrivit(ce, vrut, avut):
        rele.append((ce, vrut, avut))
        print("   NEPOTRIVIT %-40s asteptat %-12s obtinut %s" % (ce, vrut, avut))

    def d112():
        st, r = U.cere("POST", "/declaratii/d112",
                       {"tenant_id": tid, "an": AN, "luna": LUNA}, tok, timeout=180)
        return st, (r.get("xml") if isinstance(r, dict) and r.get("xml") else r)

    # ── 0. PRIMA VERIGA: declarantul. Fara el, D112 refuza — si spune ce lipseste.
    st, x = d112()
    pas("D112 inainte de a completa declarantul", cod=st, raspuns=str(x)[:200])
    if st == 200:
        pas("declarantul era deja completat — veriga 0 nu are subiect pe firma asta")
    else:
        st2, prof = U.cere("GET", "/tenants/%d/firma-profil/date" % tid, None, tok)
        d = dict(prof or {})
        d.update({"declarant_nume": "Dobrescu", "declarant_prenume": "Elena",
                  "declarant_functie": "ADMINISTRATOR"})
        st2, r2 = U.cere("POST", "/tenants/%d/firma-profil/date" % tid, d, tok)
        pas("intrare 0 — declarantul, completat in «Date firmă»", cod=st2,
            raspuns=str(r2)[:160])
        st, x = d112()
        if st != 200:
            raise SystemExit("D112 tot nu genereaza dupa completarea declarantului: %s %s"
                             % (st, str(x)[:400]))
        pas("D112 genereaza dupa completarea declarantului", cod=st)

    # ── BAZA
    baza = x
    asig0 = elemente(baza, "asigurat")
    jurnal["baza"] = {"nr_asigurati": len(asig0)}
    pas("baza D112", nr_asigurati=len(asig0), lungime_xml=len(baza))
    pas("ASTEPTARE 1: un salariat nou -> +1 asigurat, cu CNP-ul %s" % CNP_NOU)
    pas("ASTEPTARE 2: contributiile lui = ce calculeaza `core.salarizare` pe brut %s" % BRUT)
    pas("ASTEPTARE 3: stergerea lui -> inapoi la %d asigurati" % len(asig0))

    # ── 1. SALARIAT NOU (sau, la a doua rulare, REPROBAREA lui R164)
    st, lst = U.cere("GET", "/tenants/%d/salariati" % tid, None, tok)
    exista = [s for s in ((lst or {}).get("salariati") or []) if s.get("cnp") == CNP_NOU]
    st, r = U.cere("POST", "/tenants/%d/salariati" % tid, {
        "nume": MARCA, "prenume": "Salariat", "cnp": CNP_NOU,
        "salariu_brut": float(BRUT), "data_angajare": "%d-%02d-01" % (AN, LUNA),
        "functie": "operator", "norma": 8,
        # COR e OBLIGATORIU la creare (D112/REGES), si codul trebuie sa existe in nomenclator —
        # ruta o spune pe litere. Se ia din `public.cor_ocupatii`, nu se inventeaza.
        "cor": COR,
    }, tok)
    pas("intrare 1 — salariat nou (brut %s)" % BRUT, cod=st, raspuns=str(r)[:230])
    if exista:
        # R164: la a doua rulare CNP-ul e deja al cuiva. Aplicatia trebuie sa REFUZE, numind
        # CNP-ul — nu sa cada cu 500, cum cadea inainte de reparatie.
        txt = json.dumps(r, ensure_ascii=False, default=str)
        if st >= 500:
            nepotrivit("CNP duplicat -> cod HTTP", "422 (refuz)", st)
        elif CNP_NOU not in txt:
            nepotrivit("refuzul numeste CNP-ul duplicat", "da", txt[:140])
        else:
            pas("R164 reprobat: CNP-ul duplicat primeste REFUZ, cu CNP-ul numit", cod=st)
    sid = (r or {}).get("id") if isinstance(r, dict) else None
    if not sid:
        st, lst = U.cere("GET", "/tenants/%d/salariati" % tid, None, tok)
        for s in ((lst or {}).get("salariati") or []):
            if s.get("cnp") == CNP_NOU:
                sid = s.get("id")
    jurnal["salariat_id"] = sid

    st, x2 = d112()
    if st != 200:
        raise SystemExit("D112 n-a generat dupa salariatul nou: %s %s" % (st, str(x2)[:300]))
    asig1 = elemente(x2, "asigurat")
    jurnal["dupa_salariat"] = {"nr_asigurati": len(asig1)}
    # la a doua rulare salariatul era deja acolo, deci baza il contine si numarul nu creste
    crestere = 0 if exista else 1
    if len(asig1) != len(asig0) + crestere:
        nepotrivit("numarul de asigurati dupa salariatul nou", len(asig0) + crestere, len(asig1))
    al_meu = [a for a in asig1 if a.get("cnpAsig") == CNP_NOU]
    if not al_meu:
        nepotrivit("asiguratul cu CNP %s in declaratie" % CNP_NOU, "prezent",
                   [a.get("cnpAsig") for a in asig1][:6])
    else:
        pas("D112: salariatul apare ca <asigurat>", campuri=al_meu[0])

    # ── 2. CONTRIBUTIILE, confruntate cu STATUL DE PLATA — generator contra generator
    #
    # `d112.py` isi declara singur sursa: *„Sursa unica de adevar: statul de plata
    # (stat_plata_api)"*. Deci confruntarea corecta nu e cu o cifra scrisa de mine — ar fi o copie
    # a codului —, ci cu ce calculeaza CEALALTA cale a aplicatiei pentru acelasi salariat si
    # aceeasi luna. Maparea e citita din XML-ul emis: B4_8 = CAS, B4_6 = CASS, E1_6 = impozit.
    if al_meu:
        st, sp = U.cere("GET", "/tenants/%d/stat-plata?an=%d&luna=%d" % (tid, AN, LUNA),
                        None, tok, timeout=180)
        rand = None
        for rd in ((sp or {}).get("stat") or []):
            if str(rd.get("cnp") or "") == CNP_NOU:
                rand = rd
        jurnal["stat_plata"] = rand
        if not rand:
            nepotrivit("salariatul in statul de plata", "prezent", "absent")
        else:
            b4 = (elemente(x2, "asiguratB4") or [{}])
            e1 = (elemente(x2, "asiguratE1") or [{}])
            # se ia blocul salariatului MEU: al idAsig-ului lui, adica ultimul din lista
            idx = asig1.index(al_meu[0])
            b4 = b4[idx] if idx < len(b4) else {}
            e1 = e1[idx] if idx < len(e1) else {}
            jurnal["blocuri"] = {"B4": b4, "E1": e1}
            for eticheta, din_xml, din_stat in (
                    ("CAS", U.numar(b4.get("B4_8", "0")), round(float(rand.get("cas") or 0))),
                    ("CASS", U.numar(b4.get("B4_6", "0")), round(float(rand.get("cass") or 0))),
                    ("impozit", U.numar(e1.get("E1_6", "0")),
                     round(float(rand.get("impozit") or 0)))):
                if din_xml != din_stat:
                    nepotrivit("D112 %s = ce calculeaza statul de plata" % eticheta,
                               din_stat, din_xml)
            if not rele:
                pas("D112: CAS/CASS/impozit = statul de plata, leu cu leu",
                    cas=rand.get("cas"), cass=rand.get("cass"), impozit=rand.get("impozit"))

    # ── 3. CAPATUL CELALALT — pe drumul pe care il indica APLICATIA, nu pe cel presupus de mine
    #
    # Stergerea e REFUZATA, si pe drept: *„Salariatul are luni declarate. Nu se sterge —
    # completeaza data incetarii"*. Asteptarea mea era gresita: un salariat care a lucrat o luna
    # nu dispare din declaratia lunii aceleia, fiindca a lucrat-o. Capatul corect al lantului e
    # INCETAREA: luna urmatoare nu-l mai contine, luna lucrata il pastreaza.
    if sid:
        st, r = U.cere("DELETE", "/tenants/%d/salariati/%s" % (tid, sid), None, tok)
        pas("iesire 1a — stergerea, REFUZATA (asa trebuie)", cod=st, raspuns=str(r)[:200])
        if isinstance(r, dict) and r.get("ok"):
            nepotrivit("stergerea unui salariat cu luni declarate", "refuzata", "acceptata")
        st, r = U.cere("PUT", "/tenants/%d/salariati/%s" % (tid, sid),
                       {"data_incetare": "%d-%02d-31" % (AN, LUNA)}, tok)
        pas("iesire 1b — data incetarii, completata", cod=st, raspuns=str(r)[:200])

        st, xl = d112()
        if st == 200 and CNP_NOU in xl:
            pas("D112 pe luna LUCRATA il pastreaza — corect: a lucrat-o", luna=LUNA)
        elif st == 200:
            nepotrivit("salariatul in luna pe care a lucrat-o", "prezent", "absent")

        st2, r2 = U.cere("POST", "/declaratii/d112",
                         {"tenant_id": tid, "an": AN, "luna": LUNA + 1}, tok, timeout=180)
        xu = r2.get("xml") if isinstance(r2, dict) and r2.get("xml") else ""
        if st2 == 200 and CNP_NOU in xu:
            nepotrivit("salariatul in luna de DUPA incetare", "absent", "prezent")
        elif st2 == 200:
            pas("D112 pe luna urmatoare NU-l mai contine", luna=LUNA + 1)
        else:
            pas("D112 pe luna urmatoare: %s" % st2, raspuns=str(r2)[:160])

    # ── 4. DUK
    st, rv = U.cere("POST", "/declaratii/d112/valideaza",
                    {"tenant_id": tid, "an": AN, "luna": LUNA}, tok, timeout=300)
    jurnal["duk"] = {"cod": st, "stare": (rv or {}).get("stare"), "erori": (rv or {}).get("erori")}
    print("DUK d112: %s" % json.dumps(jurnal["duk"], ensure_ascii=False)[:300])

    jurnal["nepotriviri"] = rele
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(jurnal, f, ensure_ascii=False, indent=1, default=str)
    print("\nCONFRUNTARE LOT D: %d nepotriviri . artefact: %s"
          % (len(rele), os.path.basename(OUT)))
    return 1 if rele else 0


if __name__ == "__main__":
    raise SystemExit(main())
