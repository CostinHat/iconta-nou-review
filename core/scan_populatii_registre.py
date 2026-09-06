# -*- coding: utf-8 -*-
"""core/scan_populatii_registre.py — CE MULȚIME DE NOTE citește fiecare registru obligatoriu, pe aceeași lună.

**Întrebarea, și de ce n-avea răspuns** (R96). Trei registre obligatorii răspund la *„ce s-a
înregistrat în luna asta"*, și dau trei răspunsuri:

  · **Fișa de cont** (14-6-22, ține locul Cărții mari) cere `status='validata'`;
  · **balanța** (`documente_api.balanta`) nu filtrează pe status deloc;
  · **registrul-jurnal** (`GET /tenants/{id}/jurnal`, 14-1-1) nu filtrează, ba chiar duce `status`
    mai departe pe fiecare rând.

Măsurat pe 08/2026: pe **8 firme din 20** mulțimile diferă; pe patru dintre ele *toate* notele lunii
sunt ciorne, deci intră în două registre și lipsesc din al treilea.

**CE FACE MODULUL ĂSTA, și atât:** dă mulțimile, ca ele să poată fi **confruntate**. Nu decide care
e cea corectă — aia e **R36** (*evidența e „ce a validat un om" sau „ce a înregistrat aplicația"?*),
o decizie care nu s-a luat. Până se ia, abaterea nu se mai poate pierde tăcut: e **declarată aici**,
iar `core/test_populatii_registre.py` cere ca declarația să fie **adevărată despre cod**.

**PE CE AXĂ SE COMPARĂ, declarat.** Numai pe **status**, pe fereastra aceleiași luni. Balanța are și
o fereastră **cumulativă** (sold inițial + rulaje până la finalul lunii) — aia e o diferență de
*perioadă*, nu de *populație*, e intenționată și n-are ce căuta în comparația asta. *O comparație
care amestecă două axe nu poate spune pe care din ele diferă.*
"""

#: Predicatul de status al fiecărui registru, așa cum e în cod — nu cum ar trebui să fie.
#: `None` = registrul nu filtrează.
PREDICAT_STATUS = {
    "fisa_cont": "validata",
    "balanta": None,
    "jurnal": None,
}

#: Abaterile ACCEPTATE azi, fiecare cu motivul. O abatere care nu e aici face gardul roșu.
#:
#: **Declarată, nu justificată.** Motivul de mai jos spune ce e, nu că e bine: alegerea aparține
#: **R36**, care e o DECIZIE nedată. Până atunci, singurul lucru care s-a schimbat e că abaterea nu
#: mai e invizibilă — și că propoziția care o justifica fals a fost scoasă din `fisa_cont`.
ABATERI_DECLARATE = {
    "fisa_cont": (
        "citește numai notele VALIDATE, deci o lună în care contabilul n-a validat încă apare "
        "GOALĂ în Cartea mare, dar plină în balanță și în registrul-jurnal. Nu e o decizie luată: "
        "e starea de azi, declarată până se răspunde la R36 — «evidența e ce a validat un om, sau "
        "ce a înregistrat aplicația?». Până atunci, abaterea e vizibilă și gardată, nu justificată."),
}


def _fereastra(an, luna):
    di = "%04d-%02d-01" % (an, luna)
    ds = "%04d-%02d-01" % (an + (luna == 12), (luna % 12) + 1)
    return di, ds


def populatii(conn, schema, an, luna):
    """`{registru: set(id-uri de note ale lunii)}` — ce admite predicatul FIECĂRUI registru.

    Se numără notele care au cel puțin o linie: toate trei registrele citesc prin
    `inregistrari_linii`, deci o notă fără linii n-ar apărea în niciunul, iar a o include aici ar
    inventa o diferență care nu există.
    """
    di, ds = _fereastra(an, luna)
    out = {}
    for reg, status in PREDICAT_STATUS.items():
        sql = (f"SELECT DISTINCT i.id FROM {schema}.inregistrari i "
               f"JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id "
               f"WHERE i.data >= %s AND i.data < %s")
        par = [di, ds]
        if status is not None:
            sql += " AND i.status = %s"
            par.append(status)
        with conn.cursor() as cur:
            cur.execute(sql, par)
            out[reg] = {r[0] for r in cur.fetchall()}
    return out


def abateri(pop):
    """`{registru: câte note îi lipsesc față de reuniune}` — numai pentru cele care chiar diferă."""
    toate = set().union(*pop.values()) if pop else set()
    return {reg: len(toate - v) for reg, v in pop.items() if toate - v}


def confrunta(conn, schema, an, luna):
    """`{pop, abateri, nedeclarate}` — `nedeclarate` gol înseamnă: ori egalitate, ori abateri scrise."""
    pop = populatii(conn, schema, an, luna)
    ab = abateri(pop)
    return {"pop": pop, "abateri": ab,
            "nedeclarate": sorted(r for r in ab if r not in ABATERI_DECLARATE)}
