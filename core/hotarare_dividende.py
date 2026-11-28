# -*- coding: utf-8 -*-
"""core/hotarare_dividende.py — funcția 501 (lotul 17.5-F5): hotărârea adunării generale a asociaților (SRL cu mai mulți asociați) sau
decizia asociatului unic privind distribuirea dividendelor, în Word editabil (.docx, OOXML scris de aplicație) și în PDF.

Comanda 17.5-F5 pct.2–5: documentul se construiește din ACEEAȘI propunere ca tabelul din formular și nota de dividende
(`uc_tenants._dividend_propus`: asociații la data hotărârii, cotele, brutul, impozitul și netul fiecăruia, contul sursă, documentul);
descărcarea nu scrie nimic (nu semnează, nu aprobă situații, nu plătește, nu creează note, nu alimentează D205). Textul și structura
urmează modelul 501 (`501_model_hotarare_dividende.docx`, SHA-256 74533c58…): varianta A (doi sau mai mulți asociați), B (asociat unic,
art. 196¹), C (dividende interimare, cu antetul, formula și semnătura din A sau B). Instrucțiunile editoriale ale modelului și câmpurile
goale nu intră în document; articolele se renumerotează.

Temeiuri (Legea 31/1990, forma cu Legea 239/2025 art. XXIV, în vigoare de la 18.12.2025; `anaf_surse/`): art. 67 alin. (2)–(2³), (3)
— dividendele numai din profituri determinate potrivit legii, proporțional cu cota de participare la capitalul vărsat; distribuirea
trimestrială pe baza situațiilor interimare, cu regularizare anuală și restituire în 60 de zile; art. 69¹ alin. (2)–(3) — activul net
cel puțin jumătate din capitalul subscris; art. 192–196¹ — adunarea și asociatul unic. Cota impozitului: cea de la data distribuirii,
adică data hotărârii (CF art. 97 alin. (7), registrul `common.COTE["impozit_dividend"]`, prin `decontari_asociati.cota_dividend`).

Limitele v1 (spuse contabilului, nu tăcute): numai SRL (SA și celelalte forme: refuz motivat); beneficiarii persoane fizice rezidente cu
CNP valid (o persoană juridică sau un CNP lipsă / invalid oprește documentul: scutirea CF art. 43 alin. (4) nu se calculează automat);
adunarea cu toți asociații prezenți și vot unanim (altă prezență se completează în Word); plafonul numerarului nu se calculează.
"""
import datetime as _dt
import io
import re
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape as _x

from core.pdf_util import bani, data_ro

#: câmpurile documentului din formularul dividendului (D4, id-urile `op-<nume>`), toate opționale pentru notă
CAMPURI = ("aprobare_anuala", "an_situatii", "data_situatii", "termen_plata", "modalitate_plata", "loc_adunare", "convocare",
           "prezenta", "vot", "administrator", "exemplare")
TITLURI_TABEL = ("Asociatul", "Cota din capitalul social", "Dividend brut (lei)", "Impozit pe dividende %s (lei)", "Dividend net (lei)")
FEL_AGA = "Hotărârea adunării generale a asociaților"
FEL_UNIC = "Decizia asociatului unic"
FORME_V1 = ("SRL",)


class LipsaDate(ValueError):
    """Documentul nu se poate produce: ce lipsește sau ce condiție legală nu e îndeplinită, unde se corectează (`camp` = id-ul din
    formular, `unde` = ecranul altfel)."""

    def __init__(self, mesaj, camp=None, unde=None):
        super().__init__(mesaj)
        self.camp, self.unde = camp, unde


def _d(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _data(v):
    try:
        return _dt.date.fromisoformat(str(v or "")[:10])
    except ValueError:
        return None


def _lei(x):
    return bani(x) + " lei"


# ───────────────────────── datele firmei și condițiile ─────────────────────────
def profil_firma(cur, schema):
    cur.execute('SELECT nume, cui, reg_com, adresa, oras, judet, declarant_nume, declarant_prenume, patron_nume, tip_firma, '
                'forma_juridica, capital_subscris, capital_varsat FROM "%s".firma_profil WHERE id = 1' % schema)
    r = cur.fetchone()
    return dict(r) if r else {}


def administrator_sugerat(profil):
    """Administratorul împuternicit, sugerat din profil (reprezentantul legal; altfel declarantul) — editabil în formular."""
    p = (profil.get("patron_nume") or "").strip()
    if p:
        return p
    return " ".join(x for x in ((profil.get("declarant_nume") or "").strip(), (profil.get("declarant_prenume") or "").strip()) if x)


def forma_juridica(profil):
    return (profil.get("forma_juridica") or profil.get("tip_firma") or "").strip().upper().replace(".", "")


def capitaluri_proprii(sold):
    """Activul net = total active − total datorii = capitalurile proprii (conturile 10x, 11x, 12x, 14x, cu semnul lor: 117 / 1171 debitor
    = pierdere reportată, 129 debitor = repartizarea profitului). `sold` = `bilant_api.sold_la` ({cont: (debitor, creditor)})."""
    t = Decimal("0")
    for k, (d, c) in sold.items():
        if str(k)[:2] in ("10", "11", "12", "14"):
            t += Decimal(str(c)) - Decimal(str(d))
    return t


def _sold(sold, *prefixe):
    return sum((Decimal(str(c)) - Decimal(str(d)) for k, (d, c) in sold.items() if str(k).startswith(prefixe)), Decimal("0"))


def conditii(cur, schema, profil, data_hot, brut, interimar, aprobare, an_sit, data_sit, unic):
    """Condițiile datate (pct.5) pe datele firmei: activul net față de jumătate din capitalul subscris (art. 69¹ alin. (2)–(3)), pentru
    interimar profitul trimestrului minus distribuirile interimare ale anului (art. 67 alin. (2²)), profitul anului aprobat. Întoarce
    {activ_net, jumatate, data_referinta, profit_an, interimare_an, profit_interimar, disponibil_interimar}; LipsaDate la refuz."""
    from core import bilant_api as _ba
    cap = profil.get("capital_subscris")
    if cap in (None, ""):
        raise LipsaDate("Lipsesc date: capitalul social subscris al firmei nu e completat. Completează-l în Date firmă → Profil "
                        "(capital subscris), apoi descarcă din nou.", unde="Date firmă → Profil")
    cap = _d(cap)
    jumatate = cap / 2
    if interimar:
        if data_sit is None:
            raise LipsaDate("Lipsesc date: scrie data situațiilor financiare interimare (sfârșitul trimestrului) pe care se distribuie "
                            "dividendele interimare (Legea 82/1991 art. 19 alin. (3¹)).", camp="op-data_situatii")
        if data_sit > data_hot:
            raise LipsaDate("Situațiile interimare (%s) nu pot fi după data hotărârii (%s)." % (data_ro(data_sit), data_ro(data_hot)),
                            camp="op-data_situatii")
        if (data_sit.month, data_sit.day) not in ((3, 31), (6, 30), (9, 30)):
            raise LipsaDate("Situațiile interimare se întocmesc la sfârșitul unui trimestru încheiat (31.03, 30.06 sau 30.09); data "
                            "scrisă (%s) nu e sfârșit de trimestru (Legea 31/1990 art. 67 alin. (2²))." % data_ro(data_sit),
                            camp="op-data_situatii")
        ref = data_sit
    else:
        ref = _dt.date(an_sit, 12, 31) if aprobare and an_sit else _dt.date(data_hot.year - 1, 12, 31)
    sold = _ba.sold_la(cur, schema, ref)
    if sold is None:   # soldurile preluate sunt după data situațiilor: aplicația nu are situațiile acelei date
        sold = _ba.sold_la(cur, schema, data_hot)
        ref_efectiv = data_hot
        if sold is None:
            raise LipsaDate("Lipsesc date: activul net la %s nu se cunoaște în aplicație (soldurile preluate sunt după această dată). "
                            "Verifică data hotărârii." % data_ro(ref), camp="op-data_hotarare")
    else:
        ref_efectiv = ref
    an = capitaluri_proprii(sold)
    out = {"activ_net": an, "jumatate": jumatate, "capital": cap, "data_referinta": ref_efectiv, "data_situatii_cerute": ref}
    if an < jumatate:
        raise LipsaDate("Distribuirea nu se poate face: activul net la %s este de %s, sub jumătate din capitalul social subscris (%s). "
                        "Legea 31/1990 art. 69¹ alin. (%s): „%s”" % (
                            data_ro(ref_efectiv), _lei(an), _lei(jumatate), "3" if interimar else "2",
                            "dividendele interimare se distribuie numai dacă activul net nu este inferior jumătății capitalului subscris"
                            if interimar else "nu se distribuie dividende dacă activul net este sau ar deveni inferior jumătății capitalului subscris"),
                        camp="op-brut")
    an_calc = an_sit if aprobare and an_sit else None
    out["profit_an"] = profit_exercitiu(cur, schema, an_calc) if an_calc else None
    yr = (data_sit or data_hot).year
    out["interimare_an"] = interimare_distribuite(cur, schema, an_calc or yr)
    if interimar:
        pi = rezultat_cumulat(cur, schema, data_sit)
        if pi is None:
            raise LipsaDate("Lipsesc date: profitul cumulat la %s nu se poate calcula (evidența anului nu e întreagă în aplicație)."
                            % data_ro(data_sit), camp="op-data_situatii")
        pierdere = max(Decimal("0"), -_sold(sold, "117"))
        out["profit_interimar"] = pi
        out["disponibil_interimar"] = pi - pierdere - out["interimare_an"]
        if brut > out["disponibil_interimar"]:
            raise LipsaDate("Dividendul interimar brut de %s depășește disponibilul trimestrului: profitul cumulat la %s este %s, pierderea "
                            "reportată de acoperit %s, iar în anul %d s-au distribuit deja interimar %s; disponibil %s. Legea 31/1990 art. 67 "
                            "alin. (2²)." % (_lei(brut), data_ro(data_sit), _lei(pi), _lei(pierdere), yr, _lei(out["interimare_an"]),
                                             _lei(max(out["disponibil_interimar"], Decimal("0")))), camp="op-brut")
    return out


def restituirea_imprumutului_blocata(cur, schema, data):
    """[17.5-F6, T7] Legea 31/1990 art. 67 alin. (2⁴) (forma Legii 239/2025, de la 18.12.2025): „Societățile care, pe baza situațiilor
    financiare anuale, aprobate potrivit legii, au o valoare a activului net diminuată la mai puțin de jumătate din valoarea capitalului social
    subscris nu pot restitui … asociaților … împrumuturile luate de la aceștia.” Situațiile anuale de referință: 31.12 al anului dinaintea
    restituirii; activul net = capitalurile proprii (`capitaluri_proprii`) din soldurile la acea dată. -> mesajul refuzului sau None.
    Limitele v1: fără situațiile acelei date în aplicație (soldurile preluate sunt după ea) sau fără capitalul subscris completat, restituirea
    nu se blochează (nu se presupune o valoare), iar refuzul cere o operație nouă numai dacă interdicția e dovedită pe datele firmei."""
    from core import bilant_api as _ba
    if data < _dt.date(2025, 12, 18):
        return None   # interdicția se aplică restituirilor de la intrarea în vigoare a Legii 239/2025
    ref = _dt.date(data.year - 1, 12, 31)
    profil = profil_firma(cur, schema)
    cap = profil.get("capital_subscris")
    sold = _ba.sold_la(cur, schema, ref)
    if cap in (None, "") or sold is None:
        return None
    an, jum = capitaluri_proprii(sold), _d(cap) / 2
    if an >= jum:
        return None
    return ("Restituirea împrumutului către asociat nu se poate înregistra: pe baza situațiilor financiare anuale la %s, activul net este de %s, "
            "sub jumătate din capitalul social subscris (%s). Legea 31/1990 art. 67 alin. (2⁴): societățile cu activul net diminuat la mai puțin "
            "de jumătate din capitalul subscris „nu pot restitui acționarilor sau asociaților … împrumuturile luate de la aceștia”. Primirea "
            "unui împrumut rămâne permisă; restituirea devine posibilă după reîntregirea activului net." % (data_ro(ref), _lei(an), _lei(jum)))


def profit_disponibil(cur, schema, la):
    """Regula de disponibilitate a funcției 501, una singură pentru propunere, M1 (502) și cabinet: profitul nerepartizat la data `la`
    = soldul creditor al conturilor 117 / 1171 (`bilant_api.sold_la`: solduri preluate + note validate; un sold debitor, adică pierderea
    reportată, îl scade) minus dividendele deja propuse din ele în note nevalidate (inclusiv reclasificarea 117 = 1171). Legea 31/1990
    art. 67 alin. (3): „Nu se vor putea distribui dividende decât din profituri determinate potrivit legii.” -> Decimal sau None când
    soldurile la `la` nu se cunosc (data e înaintea soldurilor preluate)."""
    from core import bilant_api as _ba, repo_contabilitate as _rc, repo_operatiuni as _ro
    sold = _ba.sold_la(cur, schema, la)
    if sold is None:
        return None
    # aceleași conturi ca sursa notei (`uc_tenants._sursa_profitului`): analiticul 1171 și sinteticul 117 fără analitic, cu semnul lor
    disp = sum((Decimal(str(c)) - Decimal(str(d)) for k, (d, c) in sold.items() if str(k).startswith("1171") or str(k) == "117"), Decimal("0"))
    for cont in ("1171", "117"):
        for x in _rc.dividende_nevalidate_din(cur, schema, cont):
            disp -= Decimal(str(x["suma"] if isinstance(x, dict) else x[2]))
    disp -= sum((Decimal(str(x["suma"])) for x in _ro.dividende_117_nevalidate(cur, schema)), Decimal("0"))
    return disp


#: documentele de distribuire a dividendelor, cum stau în `inregistrari.document_ref` („<Fel> nr <n> din zz.ll.aaaa”)
_RX_HOTARARE = re.compile(r"^(%s|%s) nr (\S{1,20}) din ([0-9]{2})\.([0-9]{2})\.([0-9]{4})" % (re.escape(FEL_AGA), re.escape(FEL_UNIC)))


def ultima_hotarare(cur, schema):
    """Ultima hotărâre / decizie de distribuire a dividendelor pe care o poartă o notă a firmei (orice stare a notei), după dată:
    {fel, numar, data (date)} sau None."""
    cur.execute('SELECT DISTINCT btrim(document_ref) AS d FROM "%s".inregistrari WHERE document_ref LIKE %%s OR document_ref LIKE %%s'
                % schema, (FEL_AGA + " nr %", FEL_UNIC + " nr %"))
    gasite = []
    for r in cur.fetchall():
        m = _RX_HOTARARE.match(str(r["d"] if isinstance(r, dict) else r[0]))
        if m:
            try:
                gasite.append((_dt.date(int(m.group(5)), int(m.group(4)), int(m.group(3))), m.group(2), m.group(1)))
            except ValueError:
                continue
    if not gasite:
        return None
    d, nr, fel = max(gasite)
    return {"fel": fel, "numar": nr, "data": d}


def rezumat_cabinet(cur, schema, azi):
    """[17.5-F6, Cabinet 3 a)] Rezumatul pe firmă al funcției 501 pentru secțiunea «Consultanță» a cabinetului: firma intră în lista
    «Hotărâri AGA» când are profit nerepartizat disponibil la zi (aceleași reguli ca propunerea 501: `profit_disponibil` și condiția
    datată a art. 69¹ alin. (2), `conditii`) și nicio hotărâre de distribuire în anul calendaristic curent. v1: numai SRL. Numai citiri."""
    profil = profil_firma(cur, schema)
    ultima = ultima_hotarare(cur, schema)
    out = {"an": azi.year, "eligibil": False, "disponibil": None, "motiv": None,
           "ultima": {"numar": ultima["numar"], "data": ultima["data"].isoformat(), "fel": ultima["fel"]} if ultima else None}
    if forma_juridica(profil) not in FORME_V1:
        out["motiv"] = "forma juridică în afara v1 (numai SRL)"
        return out
    disp = profit_disponibil(cur, schema, azi)
    if disp is None:
        out["motiv"] = "profitul nerepartizat la zi nu se cunoaște (soldurile preluate sunt după această dată)"
        return out
    out["disponibil"] = str(_d(disp))
    if disp <= 0:
        out["motiv"] = "fără profit nerepartizat disponibil (117 / 1171)"
        return out
    if ultima and ultima["data"].year == azi.year:
        out["motiv"] = "hotărârea de distribuire a anului %d e făcută" % azi.year
        return out
    try:
        conditii(cur, schema, profil, azi, disp, False, False, None, None, False)
    except LipsaDate as e:
        out["motiv"] = str(e)
        return out
    out["eligibil"] = True
    return out


def _rulaje_an(cur, schema, an, pana_la):
    from core import bilant_api as _ba
    ref = _ba.data_soldurilor(cur, schema)
    inceput = _dt.date(an, 1, 1)
    if ref is not None and ref >= inceput:   # evidența anului nu e întreagă în aplicație: rezultatul nu se fabrică
        return None
    cur.execute('SELECT l.cont_debit, l.cont_credit, l.suma FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i ON i.id = '
                'l.inregistrare_id WHERE i.status = \'validata\' AND i.data BETWEEN %%s AND %%s' % (schema, schema), (inceput, pana_la))
    v = Decimal("0")
    for r in cur.fetchall():
        r = dict(r)
        s = Decimal(str(r["suma"]))
        if str(r["cont_credit"]).startswith("7"):
            v += s
        if str(r["cont_debit"]).startswith("7"):
            v -= s
        if str(r["cont_debit"]).startswith("6"):
            v -= s
        if str(r["cont_credit"]).startswith("6"):
            v += s
    return v


def profit_exercitiu(cur, schema, an):
    """Profitul net al exercițiului `an` din rulajele claselor 6 și 7 (impozitul pe profit, 691, e o cheltuială), sau None dacă
    evidența anului nu e întreagă în aplicație (preluare după 01.01). Valoarea necunoscută nu se scrie ca zero."""
    return _rulaje_an(cur, schema, an, _dt.date(an, 12, 31))


def rezultat_cumulat(cur, schema, la):
    return _rulaje_an(cur, schema, la.year, la)


def interimare_distribuite(cur, schema, an):
    """Dividendele interimare repartizate în anul `an` (463 = 456, note validate și ciorne)."""
    cur.execute('SELECT COALESCE(sum(l.suma), 0) AS s FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i ON i.id = '
                'l.inregistrare_id WHERE l.cont_debit LIKE %%s AND l.cont_credit LIKE %%s AND EXTRACT(YEAR FROM i.data) = %%s'
                % (schema, schema), ("463%", "456%", an))
    r = cur.fetchone()
    return Decimal(str((dict(r) if not isinstance(r, tuple) else {"s": r[0]})["s"] or 0))


# ───────────────────────── datele documentului ─────────────────────────
def date_document(cur, schema, propunere, corp):
    """Datele hotărârii din propunerea comună (`_dividend_propus`) și câmpurile documentului din formular. LipsaDate la orice lipsă."""
    from core.identitate import valideaza_cnp
    profil = profil_firma(cur, schema)
    fj = forma_juridica(profil)
    if fj not in FORME_V1:
        raise LipsaDate("Hotărârea de distribuire a dividendelor se generează în această versiune numai pentru societățile cu "
                        "răspundere limitată (SRL), inclusiv cu asociat unic; firma are forma juridică «%s», fără model în aplicație. "
                        "Pregătește hotărârea după actul constitutiv." % (fj or "necompletată"), unde="Date firmă → Profil")
    nota = propunere["nota"]
    parti = nota["parti"]
    unic = len(parti) == 1
    from core import decontari_asociati as _da
    for p in parti:
        if _da.persoana_juridica(p.get("cnp")):   # [17.5-F6, corecția 1 pct.1] aceeași regulă ca tabelul propunerii și nota
            raise LipsaDate("Beneficiarul «%s» e persoană juridică (CUI %s): regimul dividendelor către o persoană juridică (impozit reținut sau "
                            "scutire, Codul fiscal art. 43 alin. (4)) nu se calculează în aplicație, deci hotărârea nu se produce: ar reține o "
                            "sumă greșită. Stabilește regimul și pregătește hotărârea în afara aplicației." % (p["nume"], p.get("cnp")),
                            unde="Date firmă → Asociați")
        ok, motiv = valideaza_cnp(p.get("cnp"))
        if not ok:
            raise LipsaDate("Beneficiarul «%s» nu e identificat ca persoană fizică rezidentă: CNP-ul %s. Un CNP lipsă, invalid sau străin nu "
                            "arată că beneficiarul e o persoană juridică română. Clarifică identitatea asociatului în Date firmă → Asociați; "
                            "pentru o persoană juridică rezidentă verifică scutirea din Codul fiscal art. 43 alin. (4) — aplicația nu o "
                            "calculează și nu produce o hotărâre care ar reține o sumă greșită." % (p["nume"], motiv), unde="Date firmă → Asociați")
    numar = str(corp.get("numar_hotarare") or "").strip()
    data_hot = _data(corp.get("data_hotarare"))
    if not numar:
        raise LipsaDate("Scrie numărul hotărârii (adunarea asociaților sau decizia asociatului unic).", camp="op-numar_hotarare")
    interimar = bool(propunere["interimar"])
    aprobare_txt = str(corp.get("aprobare_anuala") or "").strip()
    if not interimar and aprobare_txt not in ("da", "nu"):
        raise LipsaDate("Alege dacă hotărârea aprobă și situațiile financiare anuale (da / nu).", camp="op-aprobare_anuala")
    aprobare = (aprobare_txt == "da") and not interimar
    an_sit = None
    if aprobare:
        try:
            an_sit = int(str(corp.get("an_situatii") or "").strip())
        except ValueError:
            raise LipsaDate("Scrie anul situațiilor financiare anuale aprobate.", camp="op-an_situatii")
        if an_sit >= data_hot.year:
            raise LipsaDate("Situațiile financiare anuale aprobate sunt ale unui exercițiu încheiat: anul %d nu e înaintea hotărârii (%s)."
                            % (an_sit, data_ro(data_hot)), camp="op-an_situatii")
    termen = _data(corp.get("termen_plata"))
    if termen is None:
        raise LipsaDate("Scrie termenul de plată a dividendelor.", camp="op-termen_plata")
    if termen < data_hot:
        raise LipsaDate("Termenul de plată (%s) nu poate fi înaintea hotărârii (%s)." % (data_ro(termen), data_ro(data_hot)), camp="op-termen_plata")
    modalitate = str(corp.get("modalitate_plata") or "").strip()
    if modalitate not in ("virament", "numerar"):
        raise LipsaDate("Alege modalitatea de plată (virament sau numerar).", camp="op-modalitate_plata")
    if modalitate == "numerar":   # [17.5-F6, pct.6 (501)] plafonul datat al plății în numerar către o persoană fizică, verificat la alegere
        from core import casa as _casa
        peste = [p for p in parti if Decimal(str(p["net"])) > _casa.PLAFON_PF]
        if peste:
            raise LipsaDate("Plata în numerar nu se poate alege: dividendul net %s depășește plafonul zilnic de %s pentru plățile în numerar "
                            "către o persoană fizică (Legea 70/2015 art. 4 alin. (1): „… dividende … se efectuează cu încadrarea în plafonul "
                            "zilnic de 10.000 lei către/de la o persoană”), iar plata fragmentată a unei sume mai mari e interzisă (art. 4 "
                            "alin. (2)). Alege plata prin virament." % ("; ".join("al lui %s (%s)" % (p["nume"], _lei(p["net"])) for p in peste),
                                                                    _lei(_casa.PLAFON_PF)), camp="op-modalitate_plata")
    admin = re.sub(r"\s+", " ", str(corp.get("administrator") or "")).strip()
    if not admin:
        raise LipsaDate("Scrie administratorul împuternicit să ducă la îndeplinire hotărârea.", camp="op-administrator")
    try:
        exemplare = int(str(corp.get("exemplare") or "").strip())
    except ValueError:
        exemplare = 0
    if exemplare < 1:
        raise LipsaDate("Scrie numărul de exemplare originale.", camp="op-exemplare")
    loc = convocare = None
    if not unic:   # adunarea: locul, prezența și votul reale, confirmate de contabil (nimic presupus)
        loc = re.sub(r"\s+", " ", str(corp.get("loc_adunare") or "")).strip()
        if not loc:
            raise LipsaDate("Scrie locul adunării generale (de exemplu „sediul societății”).", camp="op-loc_adunare")
        if str(corp.get("prezenta") or "") != "toti":
            raise LipsaDate("Confirmă prezența: aplicația pregătește hotărârea când toți asociații sunt prezenți; altă prezență se "
                            "consemnează în documentul Word, după actul constitutiv (Legea 31/1990 art. 193).", camp="op-prezenta")
        if str(corp.get("vot") or "") != "unanimitate":
            raise LipsaDate("Confirmă votul: aplicația pregătește hotărârea adoptată cu unanimitate; alt rezultat al votului se "
                            "consemnează în documentul Word (Legea 31/1990 art. 192 alin. (1)).", camp="op-vot")
        convocare = re.sub(r"\s+", " ", str(corp.get("convocare") or "")).strip() or None
    data_sit = _data(corp.get("data_situatii")) if interimar else None
    cond = conditii(cur, schema, profil, data_hot, propunere["brut"], interimar, aprobare, an_sit, data_sit, unic)
    sediu = ", ".join(x for x in ((profil.get("adresa") or "").strip(), (profil.get("oras") or "").strip(),
                                  ("jud. " + profil["judet"].strip()) if (profil.get("judet") or "").strip() else "") if x)
    return {
        "varianta": "C" if interimar else ("B" if unic else "A"), "unic": unic, "interimar": interimar,
        "firma": {"nume": profil.get("nume") or "", "cui": profil.get("cui") or "", "reg_com": profil.get("reg_com") or "",
                  "sediu": sediu, "capital_subscris": cond["capital"],
                  "capital_varsat": _d(profil["capital_varsat"]) if profil.get("capital_varsat") not in (None, "") else None},
        "fel": FEL_UNIC if unic else FEL_AGA, "numar": numar, "data_hotarare": data_hot,
        "asociati": [{"nume": p["nume"], "cota": _cota_txt(p["cota"]), "brut": _d(p["brut"]), "impozit": _d(p["impozit"]),
                      "net": _d(p["net"])} for p in parti],
        "brut": _d(propunere["brut"]), "impozit": _d(nota["impozit"]), "net": _d(nota["net"]), "cota": propunere["cota_text"],
        "sursa": propunere["cont_sursa"], "aprobare": aprobare, "an_situatii": an_sit, "data_situatii": data_sit,
        "termen_plata": termen, "modalitate": modalitate, "loc": loc, "convocare": convocare,
        "administrator": admin, "exemplare": exemplare, **cond}


def _cota_txt(c):
    q = Decimal(str(c))
    q = q.quantize(Decimal(1)) if q == q.to_integral_value() else q.normalize()
    return str(q).replace(".", ",") + "%"


def nume_fisier(d, ext):
    baza = "Decizie_asociat_unic" if d["unic"] else "Hotarare_AGA"
    return "%s_dividende_nr_%s_%s.%s" % (baza, re.sub(r"[^0-9A-Za-z-]", "", d["numar"]) or "x", d["data_hotarare"].strftime("%Y%m%d"), ext)


# ───────────────────────── textul documentului (comun Word și PDF) ─────────────────────────
def continut(d):
    """Documentul ca listă de blocuri: ("titlu"|"subtitlu"|"p"|"pb"|"centru"|"tabel"|"semnaturi", conținut). Aceleași blocuri dau Word-ul
    și PDF-ul, deci aceleași date."""
    f, nume, hot = d["firma"], d["firma"]["nume"], data_ro(d["data_hotarare"])
    b = [("pb", nume), ("p", "Sediul: %s" % f["sediu"]) if f["sediu"] else None,
         ("p", " · ".join(x for x in ("Nr. de ordine în registrul comerțului: %s" % f["reg_com"] if f["reg_com"] else "",
                                       "CUI: %s" % f["cui"] if f["cui"] else "") if x)),
         ("p", "Capital social subscris: %s" % _lei(f["capital_subscris"]) +
               (" · vărsat: %s" % _lei(f["capital_varsat"]) if f["capital_varsat"] is not None else ""))]
    b = [x for x in b if x and x[1]]
    unic = d["unic"]
    b.append(("titlu", "DECIZIA ASOCIATULUI UNIC" if unic else "HOTĂRÂREA ADUNĂRII GENERALE A ASOCIAȚILOR"))
    b.append(("centru", "nr. %s din %s" % (d["numar"], hot)))
    if d["interimar"]:
        b.append(("centru", "privind distribuirea de dividende interimare"))
    if unic:
        a = d["asociati"][0]
        b.append(("p", "Subsemnatul/Subsemnata %s, asociat unic al societății %s, exercitând atribuțiile adunării generale a asociaților "
                       "potrivit art. 196¹ alin. (1) din Legea societăților nr. 31/1990, republicată, cu modificările și completările "
                       "ulterioare," % (a["nume"], nume)))
    else:
        conv = (", convocată potrivit art. 195 din Legea societăților nr. 31/1990, republicată, cu modificările și completările "
                "ulterioare, și actului constitutiv (%s)" % d["convocare"]) if d["convocare"] else ""
        b.append(("p", "Adunarea generală a asociaților societății %s, întrunită la %s în data de %s%s, cu participarea asociaților care "
                       "reprezintă întregul capital social, în prezența următorilor asociați:" % (nume, d["loc"], hot, conv)))
        for i, a in enumerate(d["asociati"], 1):
            b.append(("p", "%d. %s, deținând %s din capitalul social;" % (i, a["nume"], a["cota"])))
        b.append(("p", "reprezentând 100% din capitalul social,"))
    b.append(("p", "având în vedere:"))
    if d["interimar"]:
        tr = (d["data_situatii"].month - 1) // 3 + 1
        b.append(("p", "– situațiile financiare interimare întocmite la data de %s, la sfârșitul trimestrului %d al exercițiului financiar "
                       "%d, care evidențiază un profit net cumulat de la începutul exercițiului de %s;"
                       % (data_ro(d["data_situatii"]), tr, d["data_situatii"].year, _lei(d["profit_interimar"]))))
        b.append(("p", "– prevederile art. 67 alin. (2)–(2³) și art. 69¹ alin. (3) din Legea nr. 31/1990,"))
    else:
        if d["aprobare"]:
            b.append(("p", "– situațiile financiare anuale ale exercițiului financiar %d%s;" % (
                d["an_situatii"], (", care evidențiază un profit net de %s" % _lei(d["profit_an"])) if d["profit_an"] is not None else "")))
        if d["sursa"] in ("1171", "117"):
            b.append(("p", "– profitul nerepartizat al exercițiilor financiare anterioare, disponibil la data hotărârii;"))
        b.append(("p", "– prevederile art. 67, art. 69, art. 69¹ și art. 194 alin. (1) lit. a) din Legea nr. 31/1990,"))
    if not unic:
        b.append(("p", "cu votul asociaților care reprezintă 100% din capitalul social, potrivit art. 192 alin. (1) și art. 193 alin. (1) "
                       "din Legea nr. 31/1990,"))
    b.append(("titlu", "DECID:" if unic else "HOTĂRĂȘTE:"))
    art = []
    tabel = ("tabel", {"titluri": [t % d["cota"] if "%s" in t else t for t in TITLURI_TABEL],
                       "randuri": [[a["nume"], a["cota"], bani(a["brut"]), bani(a["impozit"]), bani(a["net"])] for a in d["asociati"]],
                       "total": ["Total", "100%", bani(d["brut"]), bani(d["impozit"]), bani(d["net"])]})
    sursa_txt = ("profitul net al exercițiului financiar %d" % d["an_situatii"]) if (
        d["aprobare"] and d["profit_an"] is not None and d["profit_an"] >= d["brut"] and d["sursa"] not in ("1171", "117")) \
        else "profitul nerepartizat al exercițiilor financiare anterioare"
    destinatar = "asociatul unic" if unic else "asociați"
    if d["interimar"]:
        art.append("Se aprobă situațiile financiare interimare ale societății întocmite la data de %s, care evidențiază un profit net de %s."
                   % (data_ro(d["data_situatii"]), _lei(d["profit_interimar"])))
        art.append(("Se aprobă distribuirea de dividende interimare brute în sumă totală de %s, din profitul exercițiului financiar curent "
                    "determinat pe baza situațiilor financiare interimare, proporțional cu cota de participare la capitalul social vărsat, "
                    "astfel:" % _lei(d["brut"]), tabel))
    else:
        if d["aprobare"]:
            art.append("Se aprobă situațiile financiare anuale ale societății pentru exercițiul financiar încheiat la 31 decembrie %d%s." % (
                d["an_situatii"], (", care evidențiază un profit net de %s" % _lei(d["profit_an"])) if d["profit_an"] is not None else ""))
        art.append(("Se aprobă distribuirea către %s a dividendelor brute în sumă totală de %s, din %s, proporțional cu cota de participare "
                    "la capitalul social vărsat, potrivit art. 67 alin. (2) din Legea nr. 31/1990, astfel:" % (destinatar, _lei(d["brut"]), sursa_txt), tabel))
        if d["aprobare"] and d["interimare_an"] > 0:
            dif = d["brut"] - d["interimare_an"]
            sens = ("se plătește %s" % ("asociatului unic" if unic else "asociaților")) if dif > 0 else ("se restituie societății" if dif < 0 else
                                                                                                         "este zero")
            art.append("Dividendele interimare distribuite în cursul exercițiului financiar %d, în sumă de %s, se regularizează față de "
                       "dividendul anual de %s. Diferența de %s %s%s, potrivit art. 67 alin. (2) și (2²) din Legea nr. 31/1990." % (
                           d["an_situatii"], _lei(d["interimare_an"]), _lei(d["brut"]), _lei(abs(dif)), sens,
                           " în termen de 60 de zile de la data aprobării situațiilor financiare anuale" if dif != 0 else ""))
    art.append("Impozitul pe dividende se calculează și se reține de societate la plata dividendelor, cu cota în vigoare la data "
               "distribuirii, de %s, și se virează la bugetul de stat potrivit Codului fiscal." % d["cota"])
    art.append("Dividendele%s se plătesc până la data de %s, %s." % (
        " interimare" if d["interimar"] else "", data_ro(d["termen_plata"]),
        "prin virament în contul bancar indicat de fiecare asociat" if d["modalitate"] == "virament"
        else "în numerar, la casieria societății, în limitele prevăzute de lege"))
    if d["interimar"]:
        art.append("Dividendele interimare se regularizează prin situațiile financiare anuale ale exercițiului financiar %d. Diferențele "
                   "rezultate din regularizare se plătesc asociaților sau, după caz, se restituie societății de către asociați, în termen de "
                   "60 de zile de la data aprobării situațiilor financiare anuale (art. 67 alin. (2) și (2²) din Legea nr. 31/1990). Până la "
                   "regularizarea acestor diferențe, societatea nu acordă împrumuturi asociaților sau altor persoane afiliate (art. 67 "
                   "alin. (2³))." % d["data_situatii"].year)
    sit = "interimare" if d["interimar"] else ("anuale ale exercițiului financiar %d" % d["data_situatii_cerute"].year
                                               if d["data_referinta"] == d["data_situatii_cerute"] else "la data hotărârii")
    art.append("%s că, potrivit situațiilor financiare %s, activul net al societății (totalul activelor minus totalul datoriilor) este de %s, "
               "cel puțin egal cu jumătate din capitalul social subscris (%s). Distribuirea respectă art. 69 și art. 69¹ din Legea nr. 31/1990."
               % ("Constat" if unic else "Adunarea constată", sit if not d["interimar"] else "interimare", _lei(d["activ_net"]),
                  _lei(d["jumatate"])))
    art.append("Se împuternicește %s, administrator al societății, să ducă la îndeplinire prezenta %s." % (
        d["administrator"], "decizie" if unic else "hotărâre"))
    for i, a in enumerate(art, 1):
        if isinstance(a, tuple):
            b.append(("p", "Art. %d. %s" % (i, a[0])))
            b.append(a[1])
        else:
            b.append(("p", "Art. %d. %s" % (i, a)))
    if unic:
        b.append(("p", "Prezenta decizie a fost consemnată în scris la data adoptării, %s, potrivit art. 196¹ alin. (2) din Legea nr. 31/1990, "
                       "în %d exemplare originale." % (hot, d["exemplare"])))
        b.append(("semnaturi", ("Asociat unic,", [d["asociati"][0]["nume"]])))
    else:
        b.append(("p", "Prezenta hotărâre a fost adoptată astăzi, %s, și s-a întocmit în %d exemplare originale." % (hot, d["exemplare"])))
        b.append(("semnaturi", ("Asociați:", [a["nume"] for a in d["asociati"]])))
    return b


# ───────────────────────── Word (OOXML scris direct, fără bibliotecă) ─────────────────────────
_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


def _run(t, bold=False):
    rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, _x(t))


def _par(t, stil=None, bold=False, centru=False):
    ppr = ""
    if stil or centru:
        ppr = "<w:pPr>%s%s</w:pPr>" % ('<w:pStyle w:val="%s"/>' % stil if stil else "", '<w:jc w:val="center"/>' if centru else "")
    return "<w:p>%s%s</w:p>" % (ppr, _run(t, bold))


def _celula(t, latime, dreapta=False, bold=False):
    return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr><w:p><w:pPr>%s</w:pPr>%s</w:p></w:tc>'
            % (latime, '<w:jc w:val="right"/>' if dreapta else "", _run(t, bold)))


_LATIMI = (2600, 1700, 1700, 1900, 1700)


def _tabel(t):
    grila = "".join('<w:gridCol w:w="%d"/>' % w for w in _LATIMI)
    rand = lambda cel, bold=False: "<w:tr>%s</w:tr>" % "".join(_celula(c, w, i > 0, bold) for i, (c, w) in enumerate(zip(cel, _LATIMI)))  # noqa: E731
    return ('<w:tbl><w:tblPr><w:tblStyle w:val="TabelHotarare"/><w:tblW w:w="9600" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            '<w:tblBorders>%s</w:tblBorders></w:tblPr><w:tblGrid>%s</w:tblGrid>%s%s%s</w:tbl>' % (
                "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="808080"/>' % x for x in ("top", "left", "bottom", "right", "insideH", "insideV")),
                grila, rand(t["titluri"], True), "".join(rand(r) for r in t["randuri"]), rand(t["total"], True)))


def docx(d):
    """Documentul Word (.docx), pachet OPC valid: [Content_Types].xml, _rels/.rels, word/document.xml, word/styles.xml, docProps. Text și
    tabel editabile, fără protecție, fără conținut înglobat."""
    corp = []
    for fel, v in continut(d):
        if fel == "titlu":
            corp.append(_par(v, "Titlu", bold=True, centru=True))
        elif fel == "centru":
            corp.append(_par(v, centru=True))
        elif fel == "pb":
            corp.append(_par(v, bold=True))
        elif fel == "p":
            corp.append(_par(v))
        elif fel == "tabel":
            corp.append(_tabel(v))
            corp.append(_par(""))
        elif fel == "semnaturi":
            corp.append(_par(v[0], bold=True))
            for n in v[1]:
                corp.append('<w:p><w:pPr><w:tabs><w:tab w:val="left" w:pos="4800"/></w:tabs></w:pPr>%s<w:r><w:tab/></w:r>%s</w:p>'
                            % (_run(n), _run("______________________________")))
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
            'w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>')
    document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document %s><w:body>%s%s</w:body></w:document>' % (
        _NS, "".join(corp), sect)
    stiluri = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:styles %s><w:docDefaults><w:rPrDefault><w:rPr>'
               '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="22"/><w:lang w:val="ro-RO"/></w:rPr></w:rPrDefault>'
               '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:pPrDefault></w:docDefaults>'
               '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
               '<w:style w:type="paragraph" w:styleId="Titlu"><w:name w:val="Titlu hotarare"/><w:basedOn w:val="Normal"/><w:pPr>'
               '<w:spacing w:before="240" w:after="120"/><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
               '<w:style w:type="table" w:styleId="TabelHotarare"><w:name w:val="Tabel hotarare"/><w:tblPr><w:tblCellMar>'
               '<w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style></w:styles>' % _NS)
    tipuri = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
              '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            '</Relationships>')
    drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:title>%s</dc:title><dc:creator>iConta</dc:creator><dc:language>ro-RO</dc:language></cp:coreProperties>'
            % _x("%s nr. %s din %s" % (d["fel"], d["numar"], data_ro(d["data_hotarare"]))))
    app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
           '<Application>iConta</Application></Properties>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nume, text in (("[Content_Types].xml", tipuri), ("_rels/.rels", rels), ("word/document.xml", document),
                           ("word/_rels/document.xml.rels", drels), ("word/styles.xml", stiluri), ("docProps/core.xml", core),
                           ("docProps/app.xml", app)):
            z.writestr(zipfile.ZipInfo(nume, (2026, 1, 1, 0, 0, 0)), text.encode("utf-8"))
    return buf.getvalue()


# ───────────────────────── PDF (reportlab, fonturile DejaVu din core/pdf_fonturi.py) ─────────────────────────
def pdf(d):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from core.pdf_fonturi import font, init_fonturi
    init_fonturi()
    reg, gros = font("sans")
    st = {"p": ParagraphStyle("p", fontName=reg, fontSize=10, leading=13.5, alignment=TA_JUSTIFY, spaceAfter=5),
          "pb": ParagraphStyle("pb", fontName=gros, fontSize=10.5, leading=14, alignment=TA_LEFT, spaceAfter=3),
          "titlu": ParagraphStyle("t", fontName=gros, fontSize=12, leading=16, alignment=TA_CENTER, spaceBefore=8, spaceAfter=4),
          "centru": ParagraphStyle("c", fontName=reg, fontSize=10, leading=13.5, alignment=TA_CENTER, spaceAfter=6)}
    cel = {a: ParagraphStyle("cel" + str(a), fontName=reg, fontSize=9, leading=11.5, alignment=a) for a in (TA_LEFT, TA_RIGHT)}
    celb = {a: ParagraphStyle("celb" + str(a), fontName=gros, fontSize=9, leading=11.5, alignment=a) for a in (TA_LEFT, TA_RIGHT)}
    esc = lambda t: _x(t)  # noqa: E731
    elem = []
    for fel, v in continut(d):
        if fel in st:
            elem.append(Paragraph(esc(v), st[fel]))
        elif fel == "tabel":
            lat = [52 * mm, 30 * mm, 30 * mm, 34 * mm, 30 * mm]
            al = lambda i: TA_LEFT if i == 0 else TA_RIGHT  # noqa: E731
            date = [[Paragraph(esc(c), celb[al(i)]) for i, c in enumerate(v["titluri"])]]
            date += [[Paragraph(esc(c), cel[al(i)]) for i, c in enumerate(r)] for r in v["randuri"]]
            date.append([Paragraph(esc(c), celb[al(i)]) for i, c in enumerate(v["total"])])
            t = Table(date, colWidths=lat, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
            elem += [Spacer(1, 3), t, Spacer(1, 8)]
        elif fel == "semnaturi":
            elem.append(Spacer(1, 10))
            elem.append(Paragraph(esc(v[0]), st["pb"]))
            t = Table([[Paragraph(esc(n), cel[TA_LEFT]), "______________________________"] for n in v[1]], colWidths=[80 * mm, 90 * mm])
            t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), reg), ("FONTSIZE", (0, 0), (-1, -1), 10),
                                   ("TOPPADDING", (0, 0), (-1, -1), 12)]))
            elem.append(t)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
                            title="%s nr. %s din %s" % (d["fel"], d["numar"], data_ro(d["data_hotarare"])), author="iConta")
    doc.build(elem)
    return buf.getvalue()
