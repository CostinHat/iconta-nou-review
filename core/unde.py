# -*- coding: utf-8 -*-
"""core/unde.py — DOMENIUL unei afirmatii, cand nu e o perioada. (P8, 22.08.2026)

DE CE. `unde` era text liber, in SAPTE forme masurate: „randul 7", „salariatul %s",
„partenerul %s (%s%s)", „vectorul fiscal al firmei", „codul CAEN al firmei (%s)", „facturile emise
%s", un id compus. Nimic nu-l citea mecanic - deci niciun gard nu era pacalit - dar era PRECONDITIA
unuia: cine ar fi vrut sa verifice „arata afirmatia spre ceva real?" ar fi trebuit sa parseze
„salariatul 53". Atunci ar fi devenit a cincea instanta de gard-care-citeste-proza intr-o zi.

FORMA, dupa `common.Temei` - modelul care exista deja in aplicatie: subclasa de `str`. Se randeaza ca
text, deci NICIUN randor nu se atinge si payload-ul ramane JSON; dar poarta `fel` (nomenclator INCHIS)
si `id`. Grepul „ce afirmatii arata spre un salariat" devine posibil.

CE NU FACE, declarat: NU verifica ca referentul EXISTA in baza. Aia cere o conexiune si e o garda
separata (si o decizie: ce faci cu o afirmatie despre un salariat sters). Aici se inchide FELUL si se
face id-ul accesibil - atat, si atat se promite.
"""

# Nomenclator INCHIS al felurilor de referent. Enumerat din cele sapte forme MASURATE pe 21.08, nu
# propus din imaginatie. `id_optional` = felul nu are identitate prin natura lui (vectorul fiscal al
# unei firme e unul singur; pachetul de preluare la fel).
FELURI_REFERENT = {
    "rand": {"eticheta": "rândul %s", "inseamna": "un rând dintr-un fișier importat"},
    "salariat": {"eticheta": "salariatul %s", "inseamna": "un salariat al firmei"},
    "partener": {"eticheta": "partenerul %s", "inseamna": "un client sau furnizor"},
    "factura": {"eticheta": "factura %s", "inseamna": "o factură emisă sau primită"},
    "cont": {"eticheta": "contul %s", "inseamna": "un cont contabil"},
    "camp_profil": {"eticheta": "%s (din datele firmei)",
                    "inseamna": "un câmp din profilul sau vectorul fiscal al firmei"},
    "vector_fiscal": {"eticheta": "vectorul fiscal al firmei", "id_optional": True,
                      "inseamna": "vectorul fiscal, ca întreg"},
    "pachet_preluare": {"eticheta": "pachetul de preluare", "id_optional": True,
                        "inseamna": "documentele primite de la contabilul anterior"},
    "linie_extras": {"eticheta": "linia de extras %s", "inseamna": "o linie dintr-un extras de cont"},
    "articol": {"eticheta": "articolul „%s”", "inseamna": "un articol de stoc"},
    "reteta": {"eticheta": "rețeta „%s”", "inseamna": "o rețetă de producție"},
    "firma": {"eticheta": "firma %s", "inseamna": "o firmă din portofoliu"},
    "mijloc_fix": {"eticheta": "mijlocul fix %s", "inseamna": "un mijloc fix din registru"},
    "declaratie_depusa": {"eticheta": "declarația depusă %s",
                          "inseamna": "o depunere din istoricul importat"},
}


class Unde(str):
    """Referinta STRUCTURATA la lucrul despre care se afirma ceva. Subclasa de str, ca `Temei`.

    `detaliu` e textul de recunoastere pentru contabil (numele omului, denumirea articolului) - el nu
    inlocuieste `id`, il insoteste: un id fara nume nu ajuta pe nimeni sa gaseasca randul, iar un nume
    fara id nu se poate urmari mecanic."""

    def __new__(cls, fel, id=None, detaliu=None):
        spec = FELURI_REFERENT.get(fel)
        if spec is None:
            raise ValueError(
                "fel de referent necunoscut %r; nomenclatorul e INCHIS: %s. Un fel nou se ADAUGA "
                "aici, cu ce inseamna - altfel `unde` redevine text liber, doar cu mai multi pasi."
                % (fel, ", ".join(sorted(FELURI_REFERENT))))
        if id is None and not spec.get("id_optional"):
            raise ValueError(
                "referinta `%s` fara identitate: „%s" % (fel, spec["inseamna"])
                + "\" e o CATEGORIE, nu o referinta. Contabilul nu poate deschide o categorie.")
        eticheta = spec["eticheta"]
        s = eticheta if spec.get("id_optional") and id is None else (eticheta % id)
        if detaliu:
            s = "%s — %s" % (s, detaliu)
        o = super().__new__(cls, s)
        o.fel, o.id, o.detaliu = fel, id, detaliu
        return o

    def __repr__(self):
        return "Unde(%r, %r)" % (self.fel, self.id)
