# -*- coding: utf-8 -*-
"""RAZA VERIFICATORULUI: fiecare regulă din DESIGN_SYSTEM.md, față în față cu ce verifică el — 30.08.2026.

DE CE EXISTĂ. `verificator_conformitate.py` întoarce **TOTAL 0** pe 182 de locuri, iar poarta e verde
pe el la fiecare tură. Dacă are goluri de acoperire, „TOTAL 0" nu înseamnă ce pare: înseamnă *zero
din ce știe el să întrebe*. Regula de proces spune că orice regulă din DS intră **simultan** în
verificator — dar **nimic nu păzește regula asta**, deci ea se poate încălca tăcut. Instrumentul o
măsoară. *(Cerut de Costin, 30.08.2026, după trei încălcări ale regulii steluțelor — două în iulie,
una azi — care ar fi trebuit să fie imposibile.)*

CE E O „REGULĂ", mecanic — și e o alegere, deci se scrie. Un **punct de listă** din DS care poartă
un **marcaj normativ** (`trebuie`, `NICIODATĂ`, `MEREU`, `INTERZIS`, `obligatoriu`, `unic`, `singura
cale`, `nu se`, …) sau un **nume de regulă îngroșat cu versiune** (`**Câmp obligatoriu (v2.0)**`).
Sub-punctele numerotate ale unei reguli se numără separat: la cap.6, „plasarea erorii per-câmp" are
șase, iar una singură acoperită n-ar acoperi celelalte cinci.

CUM SE LEAGĂ DE VERIFICATOR. Fiecare regulă își are **ancorele**: identificatorii pe care îi numește
în backtick-uri — o clasă CSS (`.oblig`, `.stare-goala`), o funcție (`arataMesaj`, `eroareCamp`), un
câmp. O regulă cu ancore se poate căuta mecanic în verificator; una fără ancore **nu** — și aia e a
patra stare, declarată, nu ascunsă sub „neacoperită".

CELE TREI STĂRI CERUTE, plus a patra:
  - **NEACOPERITĂ** — nicio ancoră a regulii nu apare în verificator;
  - **ATINSĂ** — cel puțin o ancoră apare; instrumentul **nu decide singur** dacă e acoperire reală
    sau doar de suprafață, fiindcă asta cere citirea gărzii. Le enumeră, ca să fie citite;
  - **FĂRĂ ANCORĂ** — regula n-are nicio ancoră (e proză despre culoare, ton, așezare).

CE NU VEDE, declarat:
  - o regulă acoperită de o gardă din `core/test_*.py` **în afara** verificatorului trece aici drept
    neacoperită **de verificator** — și e corect, fiindcă întrebarea e despre raza LUI. Se numără
    separat, ca să nu fie citită ca „nepăzită deloc";
  - o ancoră care apare în verificator **într-un comentariu** contează ca apariție: instrumentul nu
    deosebește codul de proză. Direcția: **supra-numără acoperirea**, deci golul e **plafon
    inferior** — cel puțin atâtea reguli sunt neacoperite. *(Regula lui R100: cazul care ar cădea
    dacă direcția e inversă e `test_ancora_in_comentariu_nu_e_acoperire`, în gardă.)*

    ./venv/bin/python scripts/scan_ds_verificator.py [--md]
"""
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS = os.path.join(RAD, "DESIGN_SYSTEM.md")
VERIF = os.path.join(RAD, "verificator_conformitate.py")

# Marcajele care fac dintr-un punct de listă o REGULĂ, nu o descriere.
NORMATIVE = ("trebuie", "niciodat", "mereu", "interzis", "obligatoriu", "obligatorii", "unic",
             "singura cale", "singură sursă", "nu se ", "se face", "nu are voie", "canonic",
             "eliminat", "nu mai", "se cere", "se marchează", "se afișează")
# Ancore: ce numește regula in backtick-uri si poate fi cautat mecanic.
RE_ANCORA = re.compile(r"`([^`]+)`")
# Numele de regula ingrosate, cu versiune: **Câmp obligatoriu (v2.0)**
RE_NUME = re.compile(r"\*\*([^*]{3,80}?\(v[\d.]+[^)]*\))\*\*")


# Cuvinte care apar in ORICE fisier Python: ca ancore n-ar discrimina nimic. Lista se scrie, ca sa
# poata fi contrazisa. *(Prima forma a instrumentului le accepta, si raporta „ATINSĂ prin: in, camp,
# return" — adica acoperire fabricata. Masurat si corectat inainte de a raporta cifra.)*
STOP = {"in", "camp", "return", "activ", "continut", "conținut", "lei", "ron", "fmt", "pct", "data",
        "date", "text", "tip", "id", "nume", "cod", "an", "luna", "zi", "ok", "nu", "da", "and",
        "or", "not", "if", "for", "def", "class", "self", "true", "false", "none", "str", "int"}


def _ancore_din(brut):
    """Ancorele CAUTABILE dintr-un fragment din backtick-uri.

    O ancora trebuie sa DISCRIMINEZE: un identificator, un selector CSS, un nume de fisier. Un
    cuvant obisnuit nu — el s-ar potrivi in orice fisier, deci ar raporta acoperire acolo unde nu e.
    Din `<span class="oblig">*</span>` se scoate si numele clasei, `oblig`, fiindca ala e ce ar
    cauta o garda.
    """
    import re as _re
    out = set()
    b = brut.strip()
    for cls in _re.findall(r'class="([^"]+)"', b):
        for c in cls.split():
            if len(c) >= 4:
                out.add(c)
    for cand in _re.findall(r"[A-Za-z_][\w./#-]{3,}", b):
        c = cand.strip("./#-")
        if len(c) < 4 or c.lower() in STOP:
            continue
        # discriminant: are punct, minus, underscore, slash, sau e mai lung de 6 caractere
        if any(ch in c for ch in "._-/") or len(c) > 6:
            out.add(c)
    return {a for a in out if not a.startswith("http")}


# Verbe care arata ca regula are o JUMATATE DE COMPORTAMENT: nu spune doar „foloseste marcajul X",
# ci si „si atunci se intampla Y". Lista se scrie, ca sa poata fi contrazisa.
CONSECINTA = ("blocheaz", "refuz", "respinge", "valideaz", "validari", "validări", "salvare",
              "salvarea", "se opreste", "se oprește", "nu se poate", "cade", "obligatoriu",
              "obligatorii", "cere", "interzis", "impiedic", "împiedic", "trebuie sa", "trebuie să")


def are_jumatate_de_comportament(text_regula):
    """Regula cere si un EFECT, nu doar un marcaj?

    DE CE CONTEAZA. `verificator_conformitate.py` e un scaner STATIC peste sursa: citeste fisiere,
    potriveste tipare, construieste AST. Nu cheama nicio ruta si nu observa nicio refuzare. Deci o
    regula care are jumatate de comportament NU poate fi acoperita de el decat la nivelul
    MARCAJULUI — oricat de bine ar fi scrisa garda. Asta nu e o scapare a vreunei garzi anume; e o
    proprietate a instrumentului, si de-aia se numara separat.

    Instanta care a cerut masuratoarea: „camp obligatoriu -> asterisc" se poate verifica static;
    „si salvarea refuza fara el" nu.
    """
    low = text_regula.lower()
    return any(v in low for v in CONSECINTA)


# Echivalente DECLARATE: forma din DS <-> forma sub care regula e pazita efectiv in verificator.
# Fiecare intrare a fost VERIFICATA in cod, nu dedusa. O lista goala ar fi fost o minciuna prin
# omisiune; una ghicita ar fi fost mai rea.
ECHIVALENTE = {
    # DS cap.21 cere marca „iConta.eu"; verificatorul o pazeste prin regexul negativ
    # `RE_BRAND = re.compile(r"iConta(?!\.eu)")`, deci forma intreaga NU apare in cod.
    "iConta.eu": ("RE_BRAND",),
}


def _capitole(text):
    """[(numar, titlu, start, stop)] pentru fiecare `## <n>. <titlu>`."""
    out = []
    m = list(re.finditer(r"^## (\d+[a-z]?)\.\s+(.+)$", text, re.M))
    for i, x in enumerate(m):
        stop = m[i + 1].start() if i + 1 < len(m) else len(text)
        out.append((x.group(1), x.group(2).strip(), x.start(), stop))
    return out


def _puncte(felie):
    """Punctele de listă ale unei felii — inclusiv sub-punctele numerotate."""
    out = []
    for ln in felie.splitlines():
        s = ln.strip()
        if re.match(r"^[-*]\s+\S", s) or re.match(r"^\d+\.\s+\*\*", s):
            out.append(s)
    return out


def reguli():
    text = io.open(DS, encoding="utf-8").read()
    out = []
    for nr, titlu, a, b in _capitole(text):
        for p in _puncte(text[a:b]):
            low = p.lower()
            nume = RE_NUME.search(p)
            e_regula = bool(nume) or any(k in low for k in NORMATIVE)
            if not e_regula:
                continue
            ancore = sorted({a for x in RE_ANCORA.findall(p) for a in _ancore_din(x)})
            out.append({"cap": nr, "titlu": titlu,
                        "nume": nume.group(1) if nume else p[:70].strip("-* "),
                        "ancore": sorted(set(ancore)), "text": p})
    return out


def _randuri_cod(sursa):
    """Randurile de COD ale verificatorului, fara comentarii si fara docstringuri.

    DE CE. O ancora care apare doar intr-un COMENTARIU nu verifica nimic — descrie. Prima forma a
    instrumentului le numara la fel, deci raporta acoperire acolo unde era doar proza. Directia
    conteaza: fara despartirea asta, golul iese mai MIC decat e.
    """
    import io as _io  # noqa: F401
    import tokenize
    from io import StringIO
    pastrate, ultim = [], None
    try:
        for tok in tokenize.generate_tokens(StringIO(sursa).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING and ultim in (tokenize.INDENT, tokenize.NEWLINE,
                                                         tokenize.NL, None):
                continue          # docstring / sir la nivel de instructiune
            pastrate.append(tok.string)
            ultim = tok.type
    except (tokenize.TokenError, IndentationError):
        return sursa              # daca nu se poate tokeniza, se declara si se cade pe tot textul
    return "\n".join(pastrate)


def acoperire(reg, sursa_verif, doar_cod):
    """(stare, ancore_in_cod, ancore_doar_in_proza) pentru o regulă."""
    if not reg["ancore"]:
        return "FĂRĂ ANCORĂ", [], []
    import re as _re

    def _variante(a):
        """Ancora, in forma INTREAGA, plus echivalentele DECLARATE pentru ea.

        DE CE NU SE SEGMENTEAZA. Prima forma taia ancora pe `.` si pe `-` si cauta bucatile. A
        reparat un fals negativ (marca) si a fabricat mai multe false POZITIVE: `msg-eroare` aparea
        drept acoperit fiindca in verificator exista cuvantul `eroare`, iar `camp-ajutor` fiindca
        exista `ajutor`. Adica instrumentul a inceput sa greseasca in AMANDOUA directiile deodata —
        starea in care o cifra nu mai poate fi folosita la nimic (METODA §22).

        Deci: potrivire pe forma intreaga, iar exceptiile se DECLARA una cate una, dupa ce au fost
        verificate in cod. O lista scurta care se poate contrazice bate o euristica ce nu se poate.
        """
        return {a.strip(".#")} | set(ECHIVALENTE.get(a.strip(".#"), ()))

    def _apare(a, unde):
        return any(_re.search(r"(?<![\w.])%s(?![\w])" % _re.escape(v), unde)
                   for v in _variante(a))

    in_cod = [a for a in reg["ancore"] if _apare(a, doar_cod)]
    doar_proza = [a for a in reg["ancore"] if a not in in_cod and _apare(a, sursa_verif)]
    if not in_cod:
        return "NEACOPERITĂ", in_cod, doar_proza
    if are_jumatate_de_comportament(reg["text"]):
        return "DOAR LA SUPRAFAȚĂ", in_cod, doar_proza
    return "ACOPERITĂ", in_cod, doar_proza


def masoara():
    sursa = io.open(VERIF, encoding="utf-8").read()
    cod = _randuri_cod(sursa)
    regs = reguli()
    for r in regs:
        r["stare"], r["ancore_gasite"], r["ancore_doar_proza"] = acoperire(r, sursa, cod)
    return regs


def ruleaza():
    regs = masoara()
    assert len(regs) > 40, "ANTI-VACUU: doar %d reguli extrase din DS" % len(regs)
    pe_stare = {}
    for r in regs:
        pe_stare.setdefault(r["stare"], []).append(r)

    print("=" * 100)
    print("RAZA VERIFICATORULUI — fiecare regulă din DESIGN_SYSTEM.md, față în față cu el")
    print("=" * 100)
    print("reguli extrase: %d, din %d capitole\n" % (len(regs), len({r["cap"] for r in regs})))
    for stare in ("NEACOPERITĂ", "DOAR LA SUPRAFAȚĂ", "ACOPERITĂ", "FĂRĂ ANCORĂ"):
        lot = pe_stare.get(stare, [])
        print("  %-24s %3d  (%4.1f%%)" % (stare, len(lot), 100.0 * len(lot) / len(regs)))

    print("\n═══ NEACOPERITE — regula numește ceva concret, verificatorul nu-l cunoaște")
    for r in sorted(pe_stare.get("NEACOPERITĂ", []), key=lambda x: (int(x["cap"].rstrip("ab")), x["nume"])):
        proza = r.get("ancore_doar_proza") or []
        print("  cap.%-3s %-58s ancore: %s%s"
              % (r["cap"], r["nume"][:58], ", ".join(r["ancore"][:5]),
                 ("   [DOAR ÎN PROZA VERIFICATORULUI: %s]" % ", ".join(proza[:3])) if proza else ""))

    print("\n═══ DOAR LA SUPRAFAȚĂ — marcajul e verificat, efectul din spatele lui NU poate fi")
    for r in sorted(pe_stare.get("DOAR LA SUPRAFAȚĂ", []),
                    key=lambda x: (int(x["cap"].rstrip("ab")), x["nume"])):
        print("  cap.%-3s %-58s prin: %s" % (r["cap"], r["nume"][:58], ", ".join(r["ancore_gasite"][:5])))

    print("\n═══ PE CAPITOLE")
    print("  %-4s %-42s %6s %6s %6s %6s" % ("cap", "titlu", "neac.", "supraf", "acop", "nemas"))
    for cap in sorted({r["cap"] for r in regs}, key=lambda c: int(c.rstrip("ab"))):
        lot = [r for r in regs if r["cap"] == cap]
        n = sum(1 for r in lot if r["stare"] == "NEACOPERITĂ")
        a = sum(1 for r in lot if r["stare"] == "DOAR LA SUPRAFAȚĂ")
        m = sum(1 for r in lot if r["stare"] == "FĂRĂ ANCORĂ")
        c = sum(1 for r in lot if r["stare"] == "ACOPERITĂ")
        print("  %-4s %-42s %6d %6d %6d %6d" % (cap, lot[0]["titlu"][:42], n, a, c, m))
    return regs


if __name__ == "__main__":
    _r = ruleaza()
    if "--md" in sys.argv:
        import json
        open("/tmp/ds_verificator.json", "w", encoding="utf-8").write(
            json.dumps(_r, ensure_ascii=False, indent=1))
        print("\nJSON: /tmp/ds_verificator.json")
