# -*- coding: utf-8 -*-
"""17.5-C9 — cazurile controlate ale lotului de consolidare (decizia D5): AC200 (intervalul SPV -> ciornă), AC201 (emitentul din
metadate sau din XML-ul autentic). Importul trece prin calea normală (`core.spv_receive.importa_mesaj`), pe PostgreSQL, într-o schemă
efemeră comisă din tenant_template (importul își deschide conexiunea și comite) — rețeaua ANAF e înlocuită numai la `descarca`, cu
arhiva unui XML UBL de probă; parserul UBL, garda beneficiarului și inserarea sunt ale aplicației. Unealta de măsurare Pilot (pct.5) și
verificatorul (pct.4) au cazurile lor mai jos, în același fișier."""
import io
import os
import threading
import zipfile
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cryptography.fernet import Fernet
os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")

import pytest

from core import db as _db
from core import spv_conector as sc
from core import efactura_send as efs
from core import spv_receive as rcv
from core import tenant_provisioning as tp

RO = ZoneInfo("Europe/Bucharest")
CIF_TENANT = "14399840"          # cifra de control verificată (identitate.valideaza_cui)
EMITENT = "26766053"
ALT_VALID = "18547290"
PRIN = sc.principal_firm(1)
SCHEMA_T = "ztest_c9_spv"


def _xml(furnizor_tax=EMITENT, furnizor_legal="-/-/-", cumparator=CIF_TENANT, total="121.00", tip="380", radacina="Invoice"):
    def parte(tax, legal):
        t = ("<cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>"
             % tax) if tax is not None else ""
        lg = "<cbc:CompanyID>%s</cbc:CompanyID>" % legal if legal is not None else ""
        return t + "<cac:PartyLegalEntity><cbc:RegistrationName>FURNIZOR C9</cbc:RegistrationName>%s</cac:PartyLegalEntity>" % lg
    return ("""<?xml version="1.0" encoding="UTF-8"?>
<%s xmlns="urn:oasis:names:specification:ubl:schema:xsd:%s-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
<cbc:ID>C9-1</cbc:ID><cbc:IssueDate>2026-11-20</cbc:IssueDate><cbc:InvoiceTypeCode>%s</cbc:InvoiceTypeCode>
<cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
<cac:AccountingSupplierParty><cac:Party>%s</cac:Party></cac:AccountingSupplierParty>
<cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>CLIENT C9</cbc:RegistrationName>
<cbc:CompanyID>%s</cbc:CompanyID></cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty>
<cac:TaxTotal><cbc:TaxAmount currencyID="RON">0.00</cbc:TaxAmount></cac:TaxTotal>
<cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount currencyID="RON">%s</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
<cac:InvoiceLine><cbc:ID>1</cbc:ID><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
<cbc:LineExtensionAmount currencyID="RON">%s</cbc:LineExtensionAmount><cac:Item><cbc:Name>Serviciu</cbc:Name></cac:Item>
<cac:Price><cbc:PriceAmount currencyID="RON">%s</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
</%s>""" % (radacina, radacina, tip, parte(furnizor_tax, furnizor_legal), cumparator, total, total, total, radacina)).encode("utf-8")


class _Resp:
    def __init__(self, xml):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("f.xml", xml)
        self.content, self.status_code = b.getvalue(), 200


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def schema():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
            cur.execute(tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
    yield SCHEMA_T
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)


def _importa(schema, monkeypatch, msg, xml, stat=None):
    monkeypatch.setattr(efs, "descarca", lambda p, i, m="test": _Resp(xml))
    stat = stat if stat is not None else rcv._stat_nou()
    rcv.importa_mesaj(schema, PRIN, CIF_TENANT, msg, stat)
    return stat


def _randuri(schema, id_mesaj=None):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id, status, cif_emitent, cif_beneficiar, data_creare, importat_la, xml_sha256 FROM %s.efactura_primite"
                        "%s ORDER BY id" % (schema, " WHERE id_mesaj_anaf=%s" if id_mesaj else ""), (id_mesaj,) if id_mesaj else None)
            return cur.fetchall()


def _msg(id_="9178305201", **k):
    m = {"id": id_, "id_solicitare": "9178305101", "data_creare": "202611261630", "tip": "FACTURA PRIMITA", "cif": CIF_TENANT}
    m.update(k)
    return m


# ───────────────────────────── AC200: t_SPV, t_ciornă și intervalul (funcțiile pure) ─────────────────────────────

def test_ac200_data_creare_forma_lista_anaf_la_minut_ora_romaniei():
    t = rcv.data_creare_spv("202611261630")
    assert t == datetime(2026, 11, 26, 16, 30, tzinfo=RO) and t.utcoffset() == timedelta(hours=2)
    assert rcv.data_creare_spv("202607011630").utcoffset() == timedelta(hours=3)          # ora de vară, același fus
    for rau in (None, "", "2026112616", "20261126163000", "202613261630", "202602301630", "2026-11-26 16:30"):
        assert rcv.data_creare_spv(rau) is None, rau                                      # lipsă / altă formă / imposibilă: necunoscută


def test_ac200_pragul_cu_sursa_precisa_la_secunda():
    t0 = datetime(2026, 11, 26, 16, 30, 0, tzinfo=RO)
    j = lambda s: rcv.interval_spv_ciorna(t0, t0 + timedelta(seconds=s), precizie_sec=1)["verdict"]
    assert (j(0), j(29 * 60 + 59), j(30 * 60), j(30 * 60 + 1)) == ("in_interval", "in_interval", "in_interval", "depasire")


def test_ac200_pragul_cu_intrarea_nativa_la_minut():
    t0 = rcv.data_creare_spv("202611261630")
    j = lambda s: rcv.interval_spv_ciorna(t0, t0 + timedelta(seconds=s))
    assert j(29 * 60)["verdict"] == "in_interval"                    # Δ real ∈ [28:01, 29:00]
    assert j(30 * 60)["verdict"] == "in_interval"                    # Δ real ∈ [29:01, 30:00]: exact 30:00 inclus
    assert j(30 * 60 + 30)["verdict"] == "nedovedit"                 # Δ real ∈ [29:31, 30:30]: precizia nu permite judecata
    assert "precizia" in j(30 * 60 + 30)["motiv"]
    assert j(31 * 60)["verdict"] == "depasire"                       # Δ real ∈ [30:01, 31:00]
    assert j(-60)["verdict"] == "nedovedit" and "inversat" in j(-60)["motiv"]


def test_ac200_peste_miezul_noptii_si_fusuri_diferite():
    t_spv = rcv.data_creare_spv("202611262350")                         # 23:50 ora României
    t_ciorna = datetime(2026, 11, 26, 22, 15, tzinfo=ZoneInfo("UTC"))   # 00:15 ora României, a doua zi
    r = rcv.interval_spv_ciorna(t_spv, t_ciorna)
    assert r["verdict"] == "in_interval" and r["delta_sec"] == 25 * 60


def test_ac200_data_lipsa_fus_necunoscut_stare_intermediara():
    t = datetime(2026, 11, 26, 16, 45, tzinfo=RO)
    assert rcv.interval_spv_ciorna(None, t)["motiv"].startswith("interval nedovedit")
    assert rcv.interval_spv_ciorna(t, None)["verdict"] == "nedovedit"
    assert rcv.interval_spv_ciorna(datetime(2026, 11, 26, 16, 30), t)["motiv"] == "interval nedovedit: fus orar necunoscut"
    assert rcv.interval_rand(t - timedelta(minutes=5), t, "descarcata")["motiv"] == "interval nedovedit: rândul n-a apărut ca ciornă"
    assert rcv.interval_rand(t - timedelta(minutes=5), t, None)["verdict"] == "nedovedit"
    assert rcv.interval_rand(t - timedelta(minutes=5), t, "ciorna")["verdict"] == "in_interval"


# ───────────────────────────── AC200 + AC201 pe calea normală, PostgreSQL ─────────────────────────────

def test_ac200_momentele_persistente_si_reluarea_nu_le_rescrie(schema, monkeypatch):
    st = _importa(schema, monkeypatch, _msg(), _xml())
    (id1, stare, emit, ben, dc, imp, sha), = _randuri(schema)
    assert (stare, emit, ben) == ("ciorna", EMITENT, CIF_TENANT) and st["ciorna"] == 1
    assert dc == rcv.data_creare_spv("202611261630")                    # t_SPV din lista ANAF, cu fusul ei
    st2 = _importa(schema, monkeypatch, _msg(data_creare="202611270900"), _xml())   # recitirea aceluiași index
    assert _randuri(schema) == [(id1, stare, emit, ben, dc, imp, sha)] and st2["deja"] == 1
    with _db.get_conn() as c:                                           # validarea nu rescrie primul moment
        with c.cursor() as cur:
            from core import repo_efactura
            repo_efactura.marcheaza_primita_validata(cur, schema, None, "628", id1)
    assert _randuri(schema)[0][4:6] == (dc, imp)


def test_ac200_data_creare_lipsa_ramane_necunoscuta(schema, monkeypatch):
    _importa(schema, monkeypatch, _msg(data_creare=None), _xml())
    r = _randuri(schema)[0]
    assert r[4] is None and rcv.interval_rand(r[4], r[5], r[1])["verdict"] == "nedovedit"


def test_ac200_doua_procesari_concurente_o_singura_ciorna(schema, monkeypatch):
    bariera = threading.Barrier(2)

    def descarca(p, i, m="test"):
        bariera.wait(timeout=10)            # ambele procesări trec de verificarea „deja importat” înainte de inserare
        return _Resp(_xml())
    monkeypatch.setattr(efs, "descarca", descarca)
    stats = [rcv._stat_nou(), rcv._stat_nou()]
    fire = [threading.Thread(target=rcv.importa_mesaj, args=(schema, PRIN, CIF_TENANT, _msg(), s)) for s in stats]
    [f.start() for f in fire]
    [f.join() for f in fire]
    assert len(_randuri(schema)) == 1
    assert sum(s["ciorna"] for s in stats) == 1 and sum(s["deja"] for s in stats) == 1   # contoarele urmează inserarea reală


@pytest.mark.parametrize("caz, meta, xml, emitent_asteptat", [
    ("ambele_valabile", {"cif_emitent": EMITENT}, _xml(), EMITENT),
    ("emitent_lipsa_xml_valid_legal_dash", {}, _xml(furnizor_tax="RO" + EMITENT, furnizor_legal="-/-/-"), EMITENT),
    ("prefix_ro_in_metadate", {"cif_emitent": "RO" + EMITENT}, _xml(), EMITENT),
    ("emitent_necunoscut", {}, _xml(furnizor_tax="-/-/-", furnizor_legal="-/-/-"), ""),
    ("cif_cu_cifra_de_control_gresita", {"cif_emitent": "26766054"}, _xml(furnizor_tax="26766054", furnizor_legal=None), ""),
    ("doua_valori_incompatibile_in_xml", {}, _xml(furnizor_tax=EMITENT, furnizor_legal=ALT_VALID), ""),
    ("metadate_contra_xml", {"cif_emitent": ALT_VALID}, _xml(), ""),
    ("furnizorul_din_xml_e_cumparatorul", {}, _xml(furnizor_tax=CIF_TENANT, furnizor_legal=None), ""),
    ("document_corectie_valoare_negativa", {}, _xml(tip="381", total="-1.00"), EMITENT),
], ids=lambda v: v if isinstance(v, str) and len(v) < 40 else "")
def test_ac201_emitentul_pe_calea_normala(schema, monkeypatch, caz, meta, xml, emitent_asteptat):
    st = _importa(schema, monkeypatch, _msg(**meta), xml)
    (rid, stare, emit, ben, _dc, _imp, _sha), = _randuri(schema)
    assert (stare, emit, ben) == ("ciorna", emitent_asteptat, CIF_TENANT), caz
    assert st.get("emitent_nedovedit", 0) == (0 if emitent_asteptat else 1), caz


def test_ac201_xml_neparsabil_cu_beneficiar_in_metadate(schema, monkeypatch):
    _importa(schema, monkeypatch, _msg(cif_beneficiar=CIF_TENANT, cif_emitent=EMITENT), b"<Invoice><neinchis>")
    (rid, stare, emit, ben, *_), = _randuri(schema)
    assert (stare, emit, ben) == ("descarcata", EMITENT, CIF_TENANT)


@pytest.mark.parametrize("caz, meta, xml", [
    ("beneficiar_din_alta_firma_in_metadate", {"cif_beneficiar": ALT_VALID, "cif_emitent": EMITENT}, _xml()),
    ("cumparator_cu_alt_cif_in_xml", {}, _xml(cumparator=ALT_VALID)),
    ("xml_neparsabil_fara_beneficiar", {}, b"<Invoice><neinchis>"),
], ids=lambda v: v if isinstance(v, str) else "")
def test_ac201_zero_scrieri_in_firma_gresita(schema, monkeypatch, caz, meta, xml):
    st = _importa(schema, monkeypatch, _msg(**meta), xml)
    assert _randuri(schema) == [] and st["scurgere_evitata"] == 1, caz
    assert rcv.pe_rezultat(rcv._stat_nou(), st, 1)["refuzate"] == 1


def test_ac201_emitent_din_surse_pur():
    f = rcv.emitent_din_surse
    assert f({"cif_emitent": EMITENT}, _xml(furnizor_tax=None, furnizor_legal=None), CIF_TENANT) == (EMITENT, "metadate", None)
    assert f({}, _xml(), CIF_TENANT) == (EMITENT, "xml", None)
    assert f({}, b"nu e xml", CIF_TENANT) == (None, "niciuna", "XML-ul nu se poate citi")
    cod, sursa, motiv = f({"cif_emitent": ALT_VALID}, _xml(), CIF_TENANT)
    assert cod is None and sursa == "contradictie" and EMITENT in motiv and ALT_VALID in motiv


# ───────────────────────────── pct.5: unealta de măsurare Pilot (scripts/masurare_pilot.py), probe sintetice ─────────────────────────────
# O probă sintetică validează unealta; nu satisface o dependență reală. Codul de probă „P900” nu e în numitorul celor 45.
import csv as _csv
import hashlib as _hl
import json as _json
import sys as _sys

_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import masurare_pilot as mp  # noqa: E402

COMMIT_P = "a" * 40


def _inventar(cod="P900", rezolutii=mp.REZOLUTII):
    return [{"cod": cod, "criteriu": cr, "rezolutie": z, "firma": "F1 Comert Stoc SRL", "rol": "contabil", "ruta": "Parteneri",
             "stare": "listă", "document_perioada": "-", "gest": "deschide Parteneri", "dimensiune": "eticheta butonului",
             "cheie": "dom:#pt-nou|text", "operator": "egal", "asteptat": "+ Fișă de partener"} for cr in mp.CRITERII for z in rezolutii]


def _martor(d, rand, commit=COMMIT_P, **schimbari):
    """Martorul unei celule, ca `masoara_celula` (fără browser): captura, JSON-ul și rândul din manifest."""
    nume = mp.nume_martor(rand["cod"], rand["criteriu"], rand["rezolutie"])
    cap = d / (nume[:-5] + ".png")
    cap.write_bytes(("captura %s %s" % (nume, commit)).encode())
    m = {"cod": rand["cod"], "criteriu": rand["criteriu"], "rezolutie": rand["rezolutie"], "commit": commit, "firma": rand["firma"],
         "rol": rand["rol"], "ruta": rand["ruta"], "stare": rand["stare"], "document_perioada": "-", "gest": rand["gest"],
         "dimensiune": rand["dimensiune"], "ecran_desenat": True, "selector_gasit": True, "lipsa_confirmata": False,
         "observat": "+ Fișă de partener", "captura": {"cale": cap.name, "sha256": _hl.sha256(cap.read_bytes()).hexdigest()},
         "consola_erori": [], "motiv_neexecutat": ""}
    m.update(schimbari)
    (d / nume).write_text(_json.dumps(m, ensure_ascii=False), encoding="utf-8")
    with open(d / "martori.sha256", "a", encoding="utf-8") as f:
        f.write("%s  %s\n" % (_hl.sha256((d / nume).read_bytes()).hexdigest(), nume))


def _grila(tmp_path, schimbari=None):
    inv = _inventar()
    for r in inv:
        _martor(tmp_path, r, **((schimbari or {}).get((r["criteriu"], r["rezolutie"])) or {}))
    return mp.judeca(inv, str(tmp_path), COMMIT_P)


def test_unealta_12_celule_valide_cod_inchis(tmp_path):
    celule, rez = _grila(tmp_path)
    assert len(celule) == 12 and all(c["rezultat"] == "1" for c in celule) and mp.cod_iesire(celule) == 0
    assert rez["P900"]["inchis"] and rez["P900"]["scor_istoric_5"] == 10
    assert all(c["versiune"] == COMMIT_P and len(c["martor_sha256"]) == 64 and len(c["captura_sha256"]) == 64 for c in celule)


def test_unealta_o_celula_0_observata_si_una_neexecutata_impiedica_inchiderea(tmp_path):
    celule, rez = _grila(tmp_path, {("Design", "603x590"): {"observat": "Descarcă PDF"},
                                    ("Stabilitate", "1366x768"): {"motiv_neexecutat": "martorul F179 real lipsește (acțiunea lui Costin)"}})
    pe = {(c["criteriu"], c["rezolutie"]): c for c in celule}
    assert pe[("Design", "603x590")]["rezultat"] == "0" and pe[("Stabilitate", "1366x768")]["rezultat"] == "-"
    assert "F179" in pe[("Stabilitate", "1366x768")]["motiv"]
    assert not rez["P900"]["inchis"] and mp.cod_iesire(celule) == 1
    assert any("P900/Design/603x590=0" in b for b in rez["P900"]["blocante"])        # raportul numește celula
    assert rez["P900"]["scor_istoric_5"] == 9                                          # scorul istoric (5 criterii) e separat de închidere


def test_unealta_selector_si_ecran_lipsa_dau_neexecutat(tmp_path):
    celule, _ = _grila(tmp_path, {("Funcțional", "1366x768"): {"selector_gasit": False, "observat": None},
                                  ("Aspect", "1366x768"): {"ecran_desenat": False},
                                  ("Aspect", "603x590"): {"ruta": "Clienți"},
                                  ("Funcțional", "603x590"): {"selector_gasit": False, "lipsa_confirmata": True}})
    pe = {(c["criteriu"], c["rezolutie"]): c for c in celule}
    assert pe[("Funcțional", "1366x768")]["rezultat"] == "-" and "selectorul" in pe[("Funcțional", "1366x768")]["motiv"]
    assert pe[("Aspect", "1366x768")]["motiv"] == "ecranul nu s-a desenat"
    assert pe[("Aspect", "603x590")]["motiv"].startswith("rută greșită")
    assert pe[("Funcțional", "603x590")]["rezultat"] == "0"     # lipsa confirmată independent e defect măsurabil


def test_unealta_inventar_invalid_o_rezolutie_rand_dublu(tmp_path):
    assert any("nu are cele 12 celule" in e for e in mp.valideaza_inventar(_inventar(rezolutii=("1366x768",))))
    dublu = _inventar()
    assert any("celulă dublă" in e for e in mp.valideaza_inventar(dublu + dublu[:1]))
    with pytest.raises(mp.Refuz):
        mp.judeca(dublu + dublu[:1], str(tmp_path), COMMIT_P)


def test_unealta_captura_sau_martor_de_pe_alt_commit_si_martor_lipsa(tmp_path):
    celule, _ = _grila(tmp_path, {("Conformitate", "1366x768"): {"commit": "b" * 40},
                                  ("Conformitate", "603x590"): {"captura": {"cale": "alta.png", "sha256": "0" * 64}}})
    pe = {(c["criteriu"], c["rezolutie"]): c for c in celule}
    assert "alt commit" in pe[("Conformitate", "1366x768")]["motiv"] and pe[("Conformitate", "1366x768")]["rezultat"] == "-"
    assert pe[("Conformitate", "603x590")]["motiv"] == "captura lipsește"
    os.remove(tmp_path / mp.nume_martor("P900", "Simplitate", "603x590"))
    celule, _ = mp.judeca(_inventar(), str(tmp_path), COMMIT_P)
    assert {(c["criteriu"], c["rezolutie"]): c for c in celule}[("Simplitate", "603x590")]["motiv"] == "martor lipsă"


def test_unealta_martor_alterat_refuza(tmp_path):
    _grila(tmp_path)
    p = tmp_path / mp.nume_martor("P900", "Design", "1366x768")
    p.write_text(p.read_text(encoding="utf-8").replace("+ Fișă de partener", "+ Fișă de partener "), encoding="utf-8")
    with pytest.raises(mp.Refuz, match="martor alterat"):
        mp.judeca(_inventar(), str(tmp_path), COMMIT_P)


def test_unealta_cli_coduri_de_iesire_si_bilant(tmp_path):
    inv = tmp_path / "inventar.tsv"
    mp.scrie_tsv(str(inv), mp.COLOANE_INVENTAR, _inventar())
    d = tmp_path / "m"
    d.mkdir()
    for r in _inventar():
        _martor(d, r)
    assert mp.main(["valideaza", str(inv)]) == 0
    assert mp.main(["judeca", str(inv), str(d), COMMIT_P, str(tmp_path / "c1.tsv")]) == 0
    _martor(d, _inventar()[0], observat="altceva")                # aceeași celulă re-măsurată, 0
    assert mp.main(["judeca", str(inv), str(d), COMMIT_P, str(tmp_path / "c2.tsv")]) == 1
    (tmp_path / "num.txt").write_text("P900\n", encoding="utf-8")
    b = mp.bilant(mp.citeste_tsv(str(tmp_path / "c1.tsv")), mp.citeste_tsv(str(tmp_path / "c2.tsv")), {"P900"})
    assert b["I0"] == ["P900"] and b["I1"] == [] and b["redeschise"] == ["P900"] and b["NET"] == -1
    assert b["schimbari"][0]["fel"] == "pierdere: defect probat" and b["schimbari"][0]["celula"] == "P900/Funcțional/1366x768"
    b2 = mp.bilant(mp.citeste_tsv(str(tmp_path / "c1.tsv")), [], {"P900"})        # retest fără măsurare: martor lipsă, nu defect
    assert b2["schimbari"][0]["fel"] == "pierdere: martor lipsă" and b2["NET"] == -1
    bad = tmp_path / "rau.tsv"
    mp.scrie_tsv(str(bad), mp.COLOANE_INVENTAR, _inventar(rezolutii=("603x590",)))
    assert mp.main(["valideaza", str(bad)]) == 2 and mp.main(["judeca", str(bad), str(d), COMMIT_P, str(tmp_path / "x.tsv")]) == 2
