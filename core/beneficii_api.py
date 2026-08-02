# -*- coding: utf-8 -*-
"""core/beneficii_api.py — beneficii extrasalariale ONE-OFF pe luna (F133 Faza 2).

Tichete de vacanta (2a) si cadou (2b) NU sunt config permanent ca tichetele de masa -
sunt sume acordate intr-o luna anume. Se stocheaza per (salariat, an, luna, tip).

Tratament fiscal (verificat la sursa 2026):
- vacanta: CASS 10% + impozit 10%, FARA CAS/CAM. 6 salarii minime/an = nivelul MAXIM care
  poate fi acordat potrivit legii (OUG 8/2009 art.1), NU un plafon de scutire: voucherele
  SE impoziteaza (10% + CASS 10%) inclusiv sub acest nivel.
- cadou (2b): sub 300 lei/eveniment = neimpozabil; peste = taxat integral ca salariu.
"""
from decimal import Decimal
from psycopg2.extras import RealDictCursor

TIPURI = ("vacanta", "cadou", "cultural")
# [F133 Faza 2b1] evenimentele cadou. Cele 4 LEGALE (<=300 lei = neimpozabil); 'altul' = nelegal
# (taxabil integral). Peste plafon sau nelegal -> taxabil (Faza 2b2; in 2b1 doar SEMNAL).
EVENIMENTE_CADOU = ("paste", "craciun", "8martie", "1iunie", "altul")
EVENIMENTE_LEGALE = ("paste", "craciun", "8martie", "1iunie")
PLAFON_CADOU = 300  # lei / persoana / eveniment (neimpozabil)


def seteaza(conn, schema, salariat_id, an, luna, tip, valoare, eveniment=""):
    """Upsert un beneficiu one-off (salariat/an/luna/tip/eveniment). valoare 0 -> sterge randul.
    eveniment: obligatoriu pt cadou (unul din EVENIMENTE_CADOU); gol pt vacanta."""
    if tip not in TIPURI:
        return {"eroare": "tip beneficiu necunoscut: %r" % tip}
    eveniment = (eveniment or "").strip()
    if tip == "cadou":
        if eveniment not in EVENIMENTE_CADOU:
            return {"eroare": "evenimentul cadoului e obligatoriu (paste/craciun/8martie/1iunie/altul)"}
    elif tip == "cultural":
        # [TICHETE CULTURALE] Legea 165/2018 art.21(1): lunar (eveniment gol) SAU ocazional (pe eveniment).
        if eveniment not in ("", "ocazional"):
            return {"eroare": "tichetul cultural e lunar (eveniment gol) sau ocazional (eveniment='ocazional')"}
    else:
        eveniment = ""  # non-cadou/non-cultural nu are eveniment
    try:
        v = Decimal(str(valoare or 0))
    except Exception:
        return {"eroare": "valoare invalida"}
    if v < 0:
        return {"eroare": "valoarea nu poate fi negativa"}
    if tip == "cultural" and v > 0:
        # [GARD] plafon semestrial indexat (verdict 16). Fereastra GRI (oct.2025-mar.2026) sau semestru
        # fara ordin confirmat -> BLOCAT motivat, NU se calculeaza tacit cu 240/470. + valoare nominala
        # multiplu de 10, max = plafon lunar/eveniment (Legea 165/2018 art.22(2), verdict 15).
        import datetime as _dtc
        from core import common as _cm
        _ocaz = (eveniment == "ocazional")
        try:
            _plaf, _sursa = _cm.plafon_cultural(_dtc.date(int(an), int(luna), 1), ocazional=_ocaz)
        except _cm.PlafonCulturalIndisponibil as _e:
            return {"eroare": str(_e)}
        if v % 10 != 0:
            return {"eroare": "valoarea tichetului cultural = multiplu de 10 lei (Legea 165/2018 art.22(2))"}
        if v > _plaf:
            return {"eroare": "valoarea %s depaseste plafonul %s/%s pentru %s-%s (%s)"
                    % (v, _plaf, ("eveniment" if _ocaz else "luna"), an, luna, _sursa)}
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {schema}.salariati WHERE id = %s", (salariat_id,))
        if not cur.fetchone():
            return None
        if v == 0:
            cur.execute(f"DELETE FROM {schema}.beneficii_lunare "
                        f"WHERE salariat_id=%s AND an=%s AND luna=%s AND tip=%s AND eveniment=%s",
                        (salariat_id, an, luna, tip, eveniment))
        else:
            cur.execute(f"""INSERT INTO {schema}.beneficii_lunare (salariat_id, an, luna, tip, valoare, eveniment)
                            VALUES (%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (salariat_id, an, luna, tip, eveniment)
                            DO UPDATE SET valoare = EXCLUDED.valoare""",
                        (salariat_id, an, luna, tip, v, eveniment))
    conn.commit()
    return {"ok": True}


def lista_luna(conn, schema, an, luna, tip):
    """{salariat_id: total(float)} pentru o luna si un tip (pt stat). Agregat pe salariat
    (cadoul poate avea mai multe evenimente/luna -> SUM)."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT salariat_id, COALESCE(SUM(valoare),0) FROM {schema}.beneficii_lunare
                        WHERE an=%s AND luna=%s AND tip=%s GROUP BY salariat_id""", (an, luna, tip))
        return {sid: float(v) for sid, v in cur.fetchall()}


def cadou_detalii_luna(conn, schema, an, luna):
    """Per salariat: [{eveniment, valoare, taxabil}] pt cadou. taxabil = eveniment NELEGAL
    ('altul') SAU valoare > plafon (300) -> necesita taxare ca salariu (Faza 2b2; 2b1 semnaleaza)."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT salariat_id, eveniment, valoare FROM {schema}.beneficii_lunare
                        WHERE an=%s AND luna=%s AND tip='cadou' ORDER BY salariat_id, eveniment""",
                    (an, luna))
        out = {}
        for sid, ev, val in cur.fetchall():
            val = float(val)
            taxabil = (ev not in EVENIMENTE_LEGALE) or (val > PLAFON_CADOU)
            out.setdefault(sid, []).append({"eveniment": ev, "valoare": val, "taxabil": taxabil})
        return out


def total_an(conn, schema, salariat_id, an, tip, pana_luna=12):
    """Suma acordata unui salariat intr-un an (pt plafonul anual - vacanta 6 sal.minime).
    pana_luna: cumulat pana la luna inclusiv (pt verificare la momentul acordarii)."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT COALESCE(SUM(valoare),0) FROM {schema}.beneficii_lunare
                        WHERE salariat_id=%s AND an=%s AND tip=%s AND luna<=%s""",
                    (salariat_id, an, tip, pana_luna))
        return float(cur.fetchone()[0])


def exces_vacanta_luna(cumul_curent, cumul_anterior, plafon_an):
    """[D3] Portiunea din tichetele de vacanta ale LUNII care depaseste plafonul ANUAL (6 sal.minime),
    incremental (OUG 8/2009 art.1 - plafon ANUAL, pe cumulat). cumul_curent = total vacanta pana la luna
    curenta INCLUSIV; cumul_anterior = pana la luna trecuta."""
    return max(0.0, float(cumul_curent) - float(plafon_an)) - max(0.0, float(cumul_anterior) - float(plafon_an))
