# -*- coding: utf-8 -*-
"""[lotul 10] Gărzile statice ale ecranelor de migrare (comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”).

- **423 a** — „importurile de migrare (salariați, solduri, parteneri): după salvare nu apare niciun mesaj de confirmare (aceeași clasă cu
  410)”. CAUZA: `_migMesaj` se consuma numai în meniul per firmă; pe drumul Migrare cabinet → <strat> → <firmă>, `nav.inapoiPas()` duce
  în lista stratului, care nu-l arăta (și ieșea mai târziu, în alt ecran). CLASA: orice ecran în care se REVINE după o salvare — adică
  orice funcție care deschide un pas (`nav.mergi` / `nav.deschide`) — trebuie să-l arate. Garda le enumeră din cod, deci un ecran nou
  care deschide pași fără să consume mesajul pică aici.
- **423 c** — „textul ecranului Salariați spune că importul se face doar după ce toate sunt corectate, dar salariații intră cu observații
  — textul urmează comportamentul”.
- **420** — câmpurile marcabile „de verificat” (`salariati_import_api.DE_VERIFICAT`, sursa unică) au fiecare avertismentul și câmpul de
  confirmare în Stat de plată; propunerile editabile din previzualizare.
- **426** — înlocuirea balanței cere confirmare pe ecran (`confirmaCaseta`, `inlocuieste`).
- **421 / 424 (contractul cu fereastra, făcut de W)** — fiecare previzualizare trece prin `_cadruPrev` (rezumat lipit sus, bara de
  acțiune lipită jos).
- **SalariatEdit** — „Corectează datele” trimite data nașterii, copiii școlarizați, declarația copiilor și funcția de bază.
TEMEI: N/A — UI (DS cap.27: „Un act cu efect asupra unei entități se încheie cu o confirmare vizibilă”)."""
import html.parser
import io
import os
import re

# forma ecranelor din ARBORELE SINTACTIC (acorn): apelul cu argumentele lui, elementul HTML cu atributele lui, condiția cu ramurile ei —
# nu „șirul apare undeva în fișier” (core/test_garzi_pe_text.py). Uneltele sunt cele din test_lot10b_facturi.py (refolosite, nu dublate).
from core.arbore_js import apeluri, arbore_js, elemente_html, functia, noduri

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = io.open(os.path.join(RAD, "static/js/ecrane/migrare.js"), encoding="utf-8").read()
FIR = io.open(os.path.join(RAD, "static/js/ecrane/firme.js"), encoding="utf-8").read()


def _functii(src):
    """{nume: corp} pentru funcțiile de nivel superior (`function x(` / `async function x(` / `export … function x(`)."""
    poz = [(m.start(), m.group(1)) for m in re.finditer(r"^(?:export )?(?:async )?function (\w+)\(", src, re.M)]
    return {n: src[p:(poz[i + 1][0] if i + 1 < len(poz) else len(src))] for i, (p, n) in enumerate(poz)}


F = _functii(MIG)
ARB_MIG, COD_MIG = arbore_js("migrare.js")


class _TextElement(html.parser.HTMLParser):
    """Textul elementelor `<tag class="cls">` dintr-un șablon (fără marcaj)."""

    def __init__(self, tag, cls):
        super().__init__()
        self.tag, self.cls, self.adanc, self.texte = tag, cls, 0, []

    def handle_starttag(self, tag, attrs):
        if self.adanc:
            self.adanc += 1
        elif tag == self.tag and dict(attrs).get("class") == self.cls:
            self.adanc = 1
            self.texte.append("")

    def handle_endtag(self, tag):
        if self.adanc:
            self.adanc -= 1

    def handle_data(self, data):
        if self.adanc:
            self.texte[-1] += data


def _text_elemente(fn, tag, cls):
    p = _TextElement(tag, cls)
    for t in noduri(fn, "TemplateLiteral"):
        p.feed("\x00".join(q["value"]["cooked"] or "" for q in t["quasis"]))
    p.close()
    return p.texte


def test_def_423a_orice_ecran_in_care_se_revine_arata_confirmarea():
    """MUTAȚIA: `_consumaMigMesaj(corp)` scos din `wizardSalariati` -> pică, cu ecranul numit."""
    deschid = sorted(n for n, c in F.items() if re.search(r"nav\.(mergi|deschide)\(", c))
    assert {"wizardSolduri", "wizardParteneri", "wizardSalariati", "meniuMigrare", "meniuMigrarePerFirma", "wizardFirmeStrat"} <= set(deschid)
    fara = [n for n in deschid if "_consumaMigMesaj(corp)" not in F[n]]
    assert not fara, "ecrane în care se revine după o salvare fără confirmarea ei (_consumaMigMesaj): %s" % fara


def test_423a_fiecare_mesaj_de_salvare_merge_pe_un_ecran_care_il_arata():
    """Fiecare `_migMesaj = …` stă într-o funcție care revine (`nav.inapoiPas()`): mesajul nu rămâne agățat pentru alt ecran."""
    cu = [n for n, c in F.items() if re.search(r"_migMesaj = (?!\"\";)", c) and n != "_consumaMigMesaj"]
    assert len(cu) >= 11, cu                           # cele 9 importuri + vectorul + decizia „gata / mai am”
    fara = [n for n in cu if "nav.inapoiPas()" not in F[n]]
    assert not fara, fara


def test_def_423c_textul_salariatilor_urmeaza_comportamentul():
    t = F["wizardSalariati"]
    assert "doar după ce toate sunt corectate" not in t
    # textul de deasupra listei (`p.mig-intro` din șablonul ecranului), propoziție cu propoziție: ce se întâmplă cu rândurile bune / respinse
    # și cu câmpurile lipsă — exact comportamentul lui `importa` (decizia Costin 14.10.2026 pct.2 + 420)
    intro = _text_elemente(functia(ARB_MIG, "wizardSalariati"), "p", "mig-intro")
    assert len(intro) == 1, intro
    assert re.split(r"(?<=\.) ", intro[0])[1:] == [
        "Fiecare rând se verifică înainte de salvare: rândurile bune intră, cele respinse (de exemplu CNP greșit) se arată cu motivul și le "
        "corectezi în fișier.",
        "Ce lipsește din fișier (norma, funcția de bază, persoanele în întreținere, scutirea) intră cu o propunere marcată „de verificat”, "
        "pe care o confirmi în Stat de plată."], intro


def test_423b_lista_salariatilor_numara_de_verificat():
    # cele două condiții pe `f.de_verificat` (numărul venit de la server), cu ramura „da” exactă: șablonul și ce interpolează
    ram = [([q["value"]["cooked"] for q in c["consequent"]["quasis"]], [COD_MIG(e) for e in c["consequent"]["expressions"]])
           for c in noduri(functia(ARB_MIG, "wizardSalariati"), "ConditionalExpression") if COD_MIG(c["test"]) == "f.de_verificat"]
    assert ram == [([" · ", " date de verificat în Stat de plată (butonul „De verificat”)"],
                    ['f.de_verificat === 1 ? "unul are" : f.de_verificat + " au"']),
                   ([" · ", " de verificat"], ["f.de_verificat"])], ram


def test_421_424_toate_previzualizarile_au_rezumatul_sus_si_actiunea_jos():
    prev = sorted(n for n in F if n.startswith("previzualizeaza"))
    assert len(prev) == 9, prev
    fara = [n for n in prev if "_cadruPrev(" not in F[n]]
    assert not fara, fara
    assert elemente_html(functia(ARB_MIG, "_cadruPrev")) == [("div", {"class": "rezumat-fix"}), ("div", {"class": "bara-fixa"})]


def test_420_propunerile_sunt_campuri_editabile_cu_eticheta():
    fn = functia(ARB_MIG, "previzualizeazaSalariati")
    # elementele de formular scrise în șablon: câmpul propus și eticheta lui (`${n}` = „\x00”, numărul rândului)
    assert sorted((a.get("data-propus"), a.get("aria-label")) for _t, a in elemente_html(fn) if a.get("data-propus")) == [
        ("ore_zi", "Ore pe zi — rândul \x00"), ("tip_norma", "Norma de lucru — rândul \x00")]
    # funcția de bază: `selectDaNu(atribute, valoare, eticheta)` — selectul cu `data-propus` și eticheta lui
    assert apeluri(fn, COD_MIG, "selectDaNu") == [
        ('`id="mig-fbaza-${n}" data-rand="${n}" data-propus="functie_baza"`', "r.functie_baza", "`Funcția de bază — rândul ${n}`")]


def test_420_fiecare_camp_de_verificat_are_avertisment_si_confirmare_in_stat():
    """Sursa unică `DE_VERIFICAT`: un câmp marcabil nou fără avertisment / fără câmp de confirmare în Stat de plată -> pică."""
    from core.salariati_import_api import DE_VERIFICAT
    avert = FIR[FIR.index("function _avertDeVerificat"):FIR.index("function formularSalariatNou")]
    panou = FIR[FIR.index('corp.querySelectorAll("[data-verif]").forEach((b) => b.addEventListener("click"'):]
    panou = panou[:panou.index("[lot 19 pct.4c] Suspendari")]
    for c in DE_VERIFICAT:
        assert 'dv.includes("%s")' % c in avert, c
        assert 'dv.includes("%s")' % c in panou, c


def test_426_inlocuirea_balantei_cere_confirmare_pe_ecran():
    fn = functia(ARB_MIG, "previzualizeazaSolduri")
    # [426, clasa] confirmarea trece prin helperele comune ale înlocuirii (`_confirmaInlocuirea` / `_inlocuire409`, care cheamă
    # `confirmaCaseta` cu `date.avertisment_inlocuire` și deschid aceeași confirmare pe 409); gardul de clasă: test_lot10_inlocuire_clasa.py
    assert apeluri(fn, COD_MIG, "_casetaInlocuire") == [("date",)]
    assert apeluri(fn, COD_MIG, "_arataInlocuirea") == [("corp", "date")]      # [lotul 11, 446] avertismentul o dată, galben
    assert apeluri(fn, COD_MIG, "_confirmaInlocuirea") == [("eroare", "date", '"Înlocuiesc balanța"', "salveaza",
                                                             '"Înlocuiești balanța de deschidere a firmei cu cea din fișier?"')]
    assert apeluri(fn, COD_MIG, "_inlocuire409") == [("e", "inlocuieste", "eroare", '"Înlocuiesc balanța"', "salveaza")]
    # confirmarea ajunge la server: `salveaza(inlocuieste)` trimite câmpul în corpul cererii POST …/solduri
    assert [COD_MIG(p) for p in functia(fn, "salveaza")["params"]] == ["inlocuieste"]
    post = [c["arguments"] for c in noduri(fn, "CallExpression") if COD_MIG(c["callee"]) == "api.post"]
    assert [(COD_MIG(a[0]), [(COD_MIG(p["key"]), COD_MIG(p["value"])) for p in a[1]["properties"]]) for a in post] == [
        ("`/tenants/${firma.tenant_id}/solduri`", [("randuri", "randuri"), ("data_referinta", "data_referinta"),
                                                    ("inlocuieste", "inlocuieste"), ("metoda_stoc", "metoda ? metoda.value : null")])]


def test_salariat_edit_corecteaza_datele_trimite_campurile_deducerilor():
    i = FIR.index("Corectează datele salariatului")
    bloc = FIR[i:FIR.index("[decizia Costin 14.10.2026 pct.3–4, verbatim în DECIZII] câmpurile importate fără valoare", i)]
    for camp in ('functie_baza: daNu(corp.querySelector("#ed-fbaza"))', 'declaratie_copii: daNu(corp.querySelector("#ed-declcopii"))',
                 "deduceri.data_nastere", "deduceri.copii_scolarizati", '"#ed-fbaza", "#ed-declcopii"'):
        assert camp in bloc, camp
    # clasa 410: confirmarea după salvare — apelul `arataMesaj(zona statului, <text>, "ok")`, cu textul exact după numele salariatului
    arb_fir, cod_fir = arbore_js("firme.js")
    conf = [c["arguments"][1] for c in noduri(arb_fir, "CallExpression") if cod_fir(c["callee"]) == "arataMesaj"
            and [cod_fir(a) for a in c["arguments"][0:3:2]] == ['corp.querySelector("#sp-date-zona")', '"ok"']]
    # [lotul 12, C133] textul e urmat de efectul corecturii scutirii în D112 (`șablon + (rez.efect_d112 ? " " + … : "")`): partea șablon
    # e operandul stâng, efectul — operandul drept, condiționat de răspunsul serverului
    sabl = [a["left"] if a["type"] == "BinaryExpression" else a for a in conf]
    assert [[q["value"]["cooked"] for q in a["quasis"]][-1] for a in sabl] == [
        ": datele corectate s-au salvat; statul se calculează cu ele."], [cod_fir(a) for a in conf]
    assert [(a["right"]["type"], cod_fir(a["right"]["test"])) for a in conf] == [
        ("ConditionalExpression", "rez && rez.scutire_corectata && rez.efect_d112")], [cod_fir(a) for a in conf]
    import main
    for camp in ("data_nastere", "copii_scolarizati", "declaratie_copii", "functie_baza"):
        assert camp in main.SalariatEdit.model_fields, camp
