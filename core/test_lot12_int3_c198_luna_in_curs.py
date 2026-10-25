# -*- coding: utf-8 -*-
"""C198 (lotul 12, găsită de Code la fx3) — „Descarcă gestiunea lunii” (Stocuri) și „Descarcă gestiunea GV <luna> (notă ciornă)” (după
nota raportului Z) se ofereau pe luna în curs și abia apoi primeau refuzul C187 (`uc_comun._cere_luna_incheiata`: „Descărcarea gestiunii
lunii 10/2026 se contează după ce luna se încheie”). CLAUDE.md §9: „Nimic precompletat sau afișat care poate induce în eroare contabilul.”
Acum stau inactive pe luna în curs, cu motivul lângă ele (`aria-describedby`), ca „Generează amortizarea” (deficiența 333) — o singură
definiție a lunii neîncheiate în ecran, `lunaNeincheiata` (firme.js), aceeași regulă ca serverul (`inchidere_luna.luna_in_curs`).

GARDA CLASEI (216 / 333 / C198): fiecare refuz „după ce luna se încheie” al serverului are, în ecran, butonul lui legat de luna
neîncheiată (inactiv cu motivul, sau neoferit). Un refuz nou fără butonul legat -> pică. Temei: N/A — regulă de ecran (CLAUDE.md §9).
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: refuzul serverului (`_cere_luna_incheiata(an, luna, "<ce>")`) -> (ruta scrisă în `data-actiune`, semnul legării de luna neîncheiată pe
#: care trebuie să-l poarte butonul — în tagul lui sau în ramura care îl desenează)
REFUZ_BUTON = {
    "Amortizarea lunii": ("/amortizare", ("lunaInCurs",)),
    "Descărcarea gestiunii lunii": ("/stocuri/descarcare", ("lunaNeincheiata(", "zInCurs")),
    "Salariile lunii": ("/salarii-contare", ("p.neincheiata",)),   # nota salariilor: butoanele care scriu stau în ramura „lună încheiată”
    "Reevaluarea în valută a lunii": ("/reevaluare-valuta/nota", ("p.luna_in_curs",)),
}


def _citeste(cale):
    with open(os.path.join(RAD, cale), encoding="utf-8") as f:
        return f.read()


def _refuzuri_server():
    gasite = set()
    for f in os.listdir(os.path.join(RAD, "core")):
        if f.endswith(".py") and not f.startswith("test_"):
            gasite |= set(re.findall(r'_cere_luna_incheiata\(an, luna, "([^"]+)"\)', _citeste(os.path.join("core", f))))
    return gasite


def _butoane(ruta):
    """(fișier, poziție, tagul) pentru fiecare `<button … data-actiune="POST /tenants/{tenant_id}<ruta>…">` din static/js."""
    out = []
    baza = os.path.join(RAD, "static", "js")
    for d, _s, fis in os.walk(baza):
        for f in fis:
            if not f.endswith(".js"):
                continue
            t = _citeste(os.path.join(d, f))
            for m in re.finditer(r"<button\b[^>]*data-actiune=\"([^\"]*)\"[^>]*>", t):
                if any(re.fullmatch(r"POST /tenants/\{tenant_id\}" + re.escape(ruta) + r"(\?.*)?", a) for a in m.group(1).split("|")):
                    out.append((os.path.relpath(os.path.join(d, f), RAD), m.start(), m.group(0), t))
    return out


def test_c198_fiecare_refuz_dupa_incheierea_lunii_are_butonul_legat_in_ecran():
    """MUTAȚIE: `${lunaNeincheiata(an, luna) ? ' disabled …' : ""}` scos din tagul lui `#s-desc` -> pică (butonul se oferă ca să fie
    refuzat); `zInCurs` scos din tagul lui `#z-desc-gv` -> pică."""
    assert _refuzuri_server() == set(REFUZ_BUTON), ("refuzurile „după ce luna se încheie” ale serverului s-au schimbat: fiecare are nevoie "
                                                    "de butonul lui legat de luna neîncheiată în ecran (REFUZ_BUTON)", _refuzuri_server())
    rele = []
    for ce, (ruta, semne) in REFUZ_BUTON.items():
        b = _butoane(ruta)
        assert b, "niciun buton pentru %s (%s): ruta s-a mutat?" % (ce, ruta)
        for fis, poz, tag, text in b:
            # semnul stă în tag (inactiv) sau în ramura care îl desenează (cel mult 4000 de caractere înaintea tagului, în același șablon: ramura `${p.neincheiata ? … : …}` a salariilor e cea mai lungă, 3090)
            if not any(s in tag for s in semne) and not any(s in text[max(0, poz - 4000):poz] for s in semne):
                rele.append("%s: %s" % (fis, tag[:140]))
    assert not rele, "butoane oferite pe luna în curs, refuzate apoi de server:\n" + "\n".join(rele)


def test_c198_butoanele_descarcarii_inactive_pe_luna_in_curs_cu_motivul_langa_ele():
    """Ambele butoane ale descărcării: `disabled` + `aria-describedby` spre motivul de lângă ele, desenat numai pe luna în curs.
    MUTAȚIE: `<p class="tip-micut" id="z-desc-gv-motiv">` scos -> pică."""
    t = _citeste("static/js/ecrane/firme.js")
    assert re.search(r"function lunaNeincheiata\(an, luna\) \{\n  const azi = new Date\(\);\n  return an \* 12 \+ luna >= azi\.getFullYear\(\) \* 12 "
                     r"\+ azi\.getMonth\(\) \+ 1;\n\}", t), "regula lunii neîncheiate din ecran s-a schimbat (inchidere_luna.luna_in_curs)"
    for buton, motiv, cond in (("s-desc", "s-desc-motiv", "lunaNeincheiata(an, luna)"), ("z-desc-gv", "z-desc-gv-motiv", "zInCurs")):
        tag = re.search(r'<button[^>]*id="%s"[^>]*>' % buton, t).group(0)
        assert "%s ? ' disabled aria-describedby=\"%s\"'" % (cond, motiv) in tag, tag
        assert '%s ? `<p class="tip-micut" id="%s">${esc(MOTIV_DESCARCARE_LUNA_IN_CURS)}</p>`' % (cond, motiv) in t, buton
    assert re.search(r'const MOTIV_DESCARCARE_LUNA_IN_CURS = "([^"]*)";', t).group(1) == "Descărcarea gestiunii lunii se face după ce luna se încheie."
