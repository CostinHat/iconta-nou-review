# -*- coding: utf-8 -*-
"""P7 · valul use-case — mutatorul de CORPURI DE RUTA (loturile 2-4).

Muta corpul unei rute din `main.py` in `core/uc_<segment>.py`, unde `<segment>` e primul segment al
caii — aceeasi impartire ca la lotul 1, derivata din rutele deja mutate, nu inventata.

CE FACE, exact:
  · ia corpul ca FELIE CONTIGUA de sursa (nu statement cu statement: asa se pierd comentariile si
    liniile goale), dedentat cu indentarea comuna;
  · `raise HTTPException(cod, mesaj)` -> `raise _erori.<Clasa>(mesaj)`, harta fixa; un cod SCRIS CA
    EXPRESIE (`409 if ... else 404`) devine aceeasi expresie peste clase, deci decizia ramane
    exact unde era, cu aceleasi ramuri;
  · un nume care in `main.py` e doar un INVELIS peste use-case (sau o constanta mutata acolo)
    devine `_uc_comun.<nume>`;
  · **raspunsul HTTP nu pleaca.** Daca ultima instructiune e `return Response(...)`, use-case-ul
    intoarce VALORILE din care se construieste, iar invelisul construieste raspunsul — neatins;
  · **`UploadFile`/`Request` nu pleaca.** Invelisul citeste octetii (`_octetii`) si numele, si le
    paseaza; use-case-ul primeste `bytes` si `str`. O lista de incarcari devine o lista de perechi
    `(octeti, nume)`. Nu se cere ca citirea sa fie inaintea tranzactiei: `_octetii` e
    `fisier.file.read()` pe un fisier pe care parserul de multipart l-a primit INTREG inainte de
    handler — nu e I/O din afara si nu poate esua altfel, deci ridicarea lui in invelis nu schimba
    nicio ordine care sa se poata observa;
  · **gardile de protocol raman deasupra.** Un `_rate_limit_email(...)` care se uita la IP-ul
    cererii ramane pe primul rand al invelisului, inaintea lui `try`, exact unde era;
  · editarile se fac pe POZITII de AST, de la coada spre cap, deci nu se bat intre ele si nu ating
    textul din siruri;
  · in `main.py` ruta pastreaza decoratorii, semnatura si docstringul.

REFUZA si raporteaza in loc sa ghiceasca.
"""
import ast
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import p7_uc_extrage as X  # noqa: E402

ANTET_UC = '''# -*- coding: utf-8 -*-
"""USE_CASE — corpurile rutelor `/%(seg)s`.

[P7 · valul use-case, 13.09.2026] Corpurile au plecat din `main.py` VERBATIM, cu tranzactiile lor
cu tot: `with db.get_conn()` se deschide aici, in stratul care detine unitatea de lucru, nu in
stratul HTTP. `HTTPException(cod, mesaj)` a devenit `_erori.<Clasa>(mesaj)`; codul se pune la loc
in invelisul din `main.py`, dintr-o harta fixa. Mesajul si ordinea efectelor sunt neatinse.
"""
'''

#: cum se cheama, in use-case, ce citea invelisul din obiectul HTTP
DIN_FISIER = {"filename": "nume_fisier", "content_type": "tip_continut", "size": "marime_fisier"}


def _invelis(nod):
    """Numele din use-case pe care il imbraca, sau None.

    Forma nu e una singura: cele mai multe invelisuri sunt `try: return _uc_X.f(...)`, dar cele
    care construiesc un raspuns au inauntru `a, b = _uc_X.f(...)` urmat de `return Response(...)`.
    Ce le face invelis e delegarea din `try`, nu forma lui `return`."""
    if not isinstance(nod, ast.FunctionDef) or not nod.body:
        return None
    t = nod.body[-1]
    if not isinstance(t, ast.Try) or not t.body:
        return None
    for x in ast.walk(ast.Module(body=t.body, type_ignores=[])):
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) \
                and isinstance(x.func.value, ast.Name) and x.func.value.id.startswith("_uc"):
            return x.func.attr
    return None


class Val(object):
    def __init__(self):
        self.m = X.Main()
        self.linii = self.m.text.splitlines(True)
        # `col_offset` din AST se numara in OCTETI de UTF-8, nu in caractere. Pe o linie cu
        # diacritice, „fără" are patru caractere si sase octeti — iar o taietura facuta cu octetii
        # pe un sir de caractere musca doua caractere in plus din linia urmatoare. Se pastreaza
        # deci si forma in octeti a fiecarei linii, si se converteste la fiecare pozitie.
        self.octeti = [ln.encode("utf-8") for ln in self.linii]
        self.offset, k = [], 0
        for ln in self.linii:
            self.offset.append(k)
            k += len(ln)
        self.invelis = {}
        for n in self.m.arb.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                u = _invelis(n)
                if u:
                    self.invelis[n.name] = u
        self.din_uc = set()
        for n in self.m.arb.body:
            if isinstance(n, ast.ImportFrom) and n.module == "core.uc_comun":
                for a in n.names:
                    self.din_uc.add(a.asname or a.name)

    def poz(self, lineno, col):
        """Pozitia in CARACTERE a unei coordonate de AST (care vine in octeti de UTF-8)."""
        return self.offset[lineno - 1] + len(self.octeti[lineno - 1][:col].decode("utf-8"))

    def _mesaj_nod(self, apel):
        """Nodul mesajului unui `HTTPException(...)` — pozitional sau `detail=`."""
        if len(apel.args) > 1:
            return apel.args[1]
        for kw in apel.keywords:
            if kw.arg == "detail":
                return kw.value
        return None

    def _taie(self, a, b, editari):
        """Felia [a,b) din sursa, cu editarile atomice dinauntru aplicate."""
        s = self.m.text[a:b]
        for i, j, nou in sorted([e for e in editari if a <= e[0] and e[1] <= b],
                                key=lambda e: -e[0]):
            s = s[:i - a] + nou + s[j - a:]
        return s

    def src(self, nod):
        return self.m.text[self.poz(nod.lineno, nod.col_offset):
                           self.poz(nod.end_lineno, nod.end_col_offset)]

    # -- ce se poate citi fix -------------------------------------------------------------------
    def _locale_unice(self, fn):
        cate, val = {}, {}
        for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
            if isinstance(x, ast.Assign) and len(x.targets) == 1 \
                    and isinstance(x.targets[0], ast.Name):
                n = x.targets[0].id
                cate[n] = cate.get(n, 0) + 1
                val[n] = x
        return {n: v for n, v in val.items() if cate[n] == 1}

    def _clase_din(self, expr):
        """Expresia de cod rescrisa peste clase, sau None daca vreo frunza n-are clasa."""
        if isinstance(expr, ast.Constant) and isinstance(expr.value, int):
            return "_erori.%s" % X.CLASA[expr.value] if expr.value in X.CLASA else None
        if isinstance(expr, ast.Name) and expr.id in self.m.intregi:
            c = self.m.intregi[expr.id]
            return "_erori.%s" % X.CLASA[c] if c in X.CLASA else None
        if isinstance(expr, ast.IfExp):
            a, b = self._clase_din(expr.body), self._clase_din(expr.orelse)
            if a is None or b is None:
                return None
            return "%s if %s else %s" % (a, self.src(expr.test), b)
        return None

    # -- refuzuri -------------------------------------------------------------------------------
    def piedici(self, fn):
        p = []
        corp = ast.Module(body=fn.body, type_ignores=[])
        if isinstance(fn, ast.AsyncFunctionDef):
            p.append("ruta e `async`")
        if any(isinstance(x, (ast.Yield, ast.YieldFrom)) for x in ast.walk(corp)):
            p.append("corpul are `yield`")
        # coduri
        loc = self._locale_unice(fn)
        for x in ast.walk(corp):
            if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call) \
                    and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException":
                a = x.exc.args[0] if x.exc.args else None
                if a is None:
                    for kw in x.exc.keywords:
                        if kw.arg == "status_code":
                            a = kw.value
                if self._clase_din(a) is None:
                    if isinstance(a, ast.Name) and a.id in loc \
                            and self._clase_din(loc[a.id].value) is not None:
                        continue
                    p.append("cod fara clasa de domeniu la l.%d" % x.lineno)
        # raspuns HTTP
        nume = {x.id for x in ast.walk(corp) if isinstance(x, ast.Name)}
        atinse = sorted(nume & set(X.RASPUNS))
        if atinse and not self._raspuns_separabil(fn):
            p.append("raspuns HTTP neseparabil: %s" % ",".join(atinse))
        # obiecte HTTP in corp
        for a in fn.args.args:
            adn = ast.get_source_segment(self.m.text, a.annotation) if a.annotation else ""
            if not adn or ("UploadFile" not in adn and "Request" not in adn):
                continue
            if a.arg not in nume:
                continue
            if "list[" in adn and self._lista_de_fisiere(fn, a.arg) is not None:
                continue                       # lista de incarcari, forma cunoscuta
            if "Request" in adn and self._garda_de_inceput(fn, a.arg) is not None:
                continue                       # garda de protocol, ramane in invelis
            rest = self._obiect_http_separabil(fn, a.arg, adn)
            if rest:
                p.append("obiect HTTP nesplitabil (`%s`): %s" % (a.arg, rest))
        # Numele se citesc pe corpul care CHIAR pleaca: o garda de protocol ramasa in invelis
        # isi duce si numele cu ea, deci n-are ce cauta pe lista celor nerezolvate.
        for n in X.externe(self._fara_garzi(fn)):
            if n in self.m.importuri or n in self.invelis or n in self.din_uc:
                continue
            if n in self.m.definite:
                p.append("nume din main.py: %s" % n)
            else:
                p.append("nume necunoscut: %s" % n)
        return p

    def _raspuns_separabil(self, fn):
        """Raspunsul se poate lasa in invelis DACA e construit intr-un singur `return`, ultimul."""
        corp = ast.Module(body=fn.body, type_ignores=[])
        ret = [x for x in ast.walk(corp) if isinstance(x, ast.Return)]
        if len(ret) != 1 or fn.body[-1] is not ret[0] or ret[0].value is None:
            return False
        return bool({x.id for x in ast.walk(ret[0].value) if isinstance(x, ast.Name)}
                    & set(X.RASPUNS))

    def _obiect_http_separabil(self, fn, param, adn):
        """Ce se citeste din obiectul HTTP. Intoarce "" daca tot ce se citeste se poate PASA."""
        corp = ast.Module(body=fn.body, type_ignores=[])
        rele = []
        for x in ast.walk(corp):
            if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) \
                    and x.value.id == param and x.attr not in DIN_FISIER:
                rele.append("." + x.attr)
            if isinstance(x, ast.Name) and x.id == param:
                pass
        # fiecare aparitie a numelui trebuie sa fie ori `param.<camp cunoscut>`, ori `_octetii(param)`,
        # ori argumentul unei garzi care ramane in invelis
        ok = set()
        for x in ast.walk(corp):
            if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) and x.value.id == param:
                ok.add(id(x.value))
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                    and x.func.id in ("_octetii",) and len(x.args) == 1 \
                    and isinstance(x.args[0], ast.Name) and x.args[0].id == param:
                ok.add(id(x.args[0]))
        for x in ast.walk(corp):
            if isinstance(x, ast.Name) and x.id == param and id(x) not in ok:
                rele.append("folosit intreg la l.%d" % x.lineno)
        # De ce NU se cere ca citirea sa fie inaintea tranzactiei: `_octetii` e `fisier.file.read()`
        # pe un fisier pe care parserul de multipart l-a primit INTREG inainte sa intre in handler
        # (`starlette/formparsers.py`). Nu e I/O din afara, nu poate esua altfel si nu poate astepta
        # pe nimeni — deci a-l ridica in invelis nu schimba nicio ordine care sa se poata observa.
        return ", ".join(sorted(set(rele)))

    def _fara_garzi(self, fn):
        """Functia, cu gardile de protocol de la inceput scoase — cele care raman in invelis."""
        k = 1 if (fn.body and isinstance(fn.body[0], ast.Expr)
                  and isinstance(fn.body[0].value, ast.Constant)
                  and isinstance(fn.body[0].value.value, str)) else 0
        corp = fn.body[k:]
        for p in fn.args.args:
            adn = ast.get_source_segment(self.m.text, p.annotation) if p.annotation else ""
            if adn and "Request" in adn:
                sus = self._garda_de_inceput(fn, p.arg)
                if sus:
                    corp = corp[sus:]
        if corp is fn.body:
            return fn
        nou = ast.FunctionDef(name=fn.name, args=fn.args, body=list(corp) or [ast.Pass()],
                              decorator_list=[], returns=None, type_comment=None)
        nou.type_params = []
        return nou

    def _garda_de_inceput(self, fn, param):
        """Instructiunile de la INCEPUTUL corpului care folosesc obiectul HTTP, si numai ele.

        `_rate_limit_email(_magic_rate, request)` e o garda de PROTOCOL: se uita la IP-ul cererii,
        nu la datele firmei, si refuza inainte de orice tranzactie. Nu pleaca in use-case — ramane
        in invelis, pe primul rand, exact unde era. Intoarce cate instructiuni raman sus, sau None
        daca obiectul mai e folosit si dupa aceea."""
        k = 1 if (fn.body and isinstance(fn.body[0], ast.Expr)
                  and isinstance(fn.body[0].value, ast.Constant)
                  and isinstance(fn.body[0].value.value, str)) else 0
        corp = fn.body[k:]
        sus = 0
        while sus < len(corp):
            if any(isinstance(x, ast.Name) and x.id == param for x in ast.walk(corp[sus])):
                sus += 1
            else:
                break
        rest = ast.Module(body=corp[sus:], type_ignores=[])
        if any(isinstance(x, ast.Name) and x.id == param for x in ast.walk(rest)):
            return None
        return sus if sus else None

    def _lista_de_fisiere(self, fn, param):
        """`for X in fisiere:` cu `_octetii(X)` si `X.filename` inauntru — forma pe care o stim.

        Intoarce {var_bucla: [campuri]}, sau None daca parametrul se foloseste si altfel."""
        corp = ast.Module(body=fn.body, type_ignores=[])
        bucle = {}
        for x in ast.walk(corp):
            if isinstance(x, (ast.For, ast.AsyncFor)) and isinstance(x.target, ast.Name):
                it = x.iter
                if isinstance(it, ast.Subscript):
                    it = it.value
                if isinstance(it, ast.Name) and it.id == param:
                    bucle[x.target.id] = x
        if not bucle:
            return None
        ok = set()
        for x in ast.walk(corp):
            if isinstance(x, (ast.For, ast.AsyncFor)) and isinstance(x.target, ast.Name) \
                    and x.target.id in bucle:
                it = x.iter.value if isinstance(x.iter, ast.Subscript) else x.iter
                ok.add(id(it))
                ok.add(id(x.target))
            if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) \
                    and x.value.id in bucle and x.attr in DIN_FISIER:
                ok.add(id(x.value))
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "_octetii" \
                    and len(x.args) == 1 and isinstance(x.args[0], ast.Name) \
                    and x.args[0].id in bucle:
                ok.add(id(x.args[0]))
        for x in ast.walk(corp):
            if isinstance(x, ast.Name) and (x.id == param or x.id in bucle) and id(x) not in ok:
                return None
        return bucle

    # -- corpul ---------------------------------------------------------------------------------
    def plan(self, fn):
        """(felie_corp, parametri_use_case, argumente_invelis, coada_invelis, cap_invelis)."""
        k = 1 if (fn.body and isinstance(fn.body[0], ast.Expr)
                  and isinstance(fn.body[0].value, ast.Constant)
                  and isinstance(fn.body[0].value.value, str)) else 0
        corpuri = fn.body[k:]
        coada = ""
        # gardile de protocol de la inceput raman in invelis, pe rand, in ordinea lor
        cap, fara = "", []
        for p in fn.args.args:
            adn = ast.get_source_segment(self.m.text, p.annotation) if p.annotation else ""
            if adn and "Request" in adn:
                sus = self._garda_de_inceput(fn, p.arg)
                if sus:
                    for i in range(sus):
                        cap += "    " + self.src(corpuri[i]).strip() + "\n"
                    corpuri = corpuri[sus:]
                    fara.append(p.arg)
        if self._raspuns_separabil(fn):
            ret = corpuri[-1]
            corpuri = corpuri[:-1]
            legate = {a.arg for a in fn.args.args} | {a.arg for a in fn.args.kwonlyargs}
            iesiri = []
            for x in ast.walk(ret.value):
                if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load) \
                        and x.id not in legate and x.id not in self.m.importuri \
                        and x.id not in X.RASPUNS and x.id not in dir(__builtins__) \
                        and x.id not in self.m.definite and x.id not in iesiri:
                    iesiri.append(x.id)
            coada = (("    %s = _APEL_\n" % ", ".join(iesiri)) if iesiri else "    _APEL_\n") \
                + "    " + self.src(ret).strip() + "\n"
        else:
            iesiri = None

        prim, ultim = corpuri[0], corpuri[-1]
        a = self.poz(prim.lineno, 0)
        b = self.poz(ultim.end_lineno, 0) + len(self.linii[ultim.end_lineno - 1])
        felie = self.m.text[a:b]

        # --- editari pe pozitii -------------------------------------------------------------
        # Doua feluri, si ordinea conteaza. ATOMICE: un nume care se rescrie (`_cere_perioada` ->
        # `_uc_comun._cere_perioada`, `_octetii(fisier)` -> `continut`). CUPRINZATOARE: un
        # `HTTPException(...)` intreg, care poate CONTINE unul atomic in mesaj. Cele atomice dinauntru
        # nu se aplica peste text deja inlocuit — se aplica INAINTE, pe mesaj, iar apoi mesajul intra
        # in inlocuirea cuprinzatoare. Fara asta, cele doua editari se calca si ies `...(e))ntrare(e))`.
        nod_corp = ast.Module(body=corpuri, type_ignores=[])
        loc = self._locale_unice(fn)
        atomice = []
        # nume-invelis / constante mutate
        for x in ast.walk(nod_corp):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load) \
                    and (x.id in self.invelis or x.id in self.din_uc):
                atomice.append((self.poz(x.lineno, x.col_offset),
                                self.poz(x.end_lineno, x.end_col_offset), "_uc_comun." + x.id))
        # obiectele HTTP: `_octetii(f)` -> `continut`, `f.filename` -> `nume_fisier`
        parm = [p.arg for p in fn.args.args if p.arg not in fara]             + [p.arg for p in fn.args.kwonlyargs if p.arg not in fara]
        arg_inv, parm_uc = list(parm), list(parm)
        for p in fn.args.args:
            adn = ast.get_source_segment(self.m.text, p.annotation) if p.annotation else ""
            if not adn or "UploadFile" not in adn or "list[" in adn:
                continue          # `list[UploadFile]` are regula lui, mai jos
            noi, i = [], parm_uc.index(p.arg)
            for x in ast.walk(nod_corp):
                if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                        and x.func.id == "_octetii" and len(x.args) == 1 \
                        and isinstance(x.args[0], ast.Name) and x.args[0].id == p.arg:
                    atomice.append((self.poz(x.lineno, x.col_offset),
                                    self.poz(x.end_lineno, x.end_col_offset), "continut"))
                    if "continut" not in noi:
                        noi.append("continut")
                elif isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) \
                        and x.value.id == p.arg and x.attr in DIN_FISIER:
                    atomice.append((self.poz(x.lineno, x.col_offset),
                                    self.poz(x.end_lineno, x.end_col_offset), DIN_FISIER[x.attr]))
                    if DIN_FISIER[x.attr] not in noi:
                        noi.append(DIN_FISIER[x.attr])
            inapoi = dict([(v2, "%s.%s" % (p.arg, k2)) for k2, v2 in DIN_FISIER.items()]
                          + [("continut", "_octetii(%s)" % p.arg)])
            parm_uc[i:i + 1] = noi
            arg_inv[i:i + 1] = [inapoi[n] for n in noi]

        # LISTA de incarcari: invelisul o preface intr-o lista de perechi `(octeti, nume)`, iar
        # bucla din corp despacheteaza perechea. Acelasi lucru citit, sub alt nume — obiectul HTTP
        # nu trece granita.
        for p in fn.args.args:
            adn = ast.get_source_segment(self.m.text, p.annotation) if p.annotation else ""
            if not adn or "list[" not in adn or "UploadFile" not in adn:
                continue
            bucle = self._lista_de_fisiere(fn, p.arg)
            if not bucle:
                continue
            # Numele despachetate sunt ACELEASI ca la o singura incarcare (`continut`,
            # `nume_fisier`), nu derivate din variabila buclei: asa mesajul de refuz arata la fel
            # indiferent pe ce cale a venit fisierul, iar confruntarea de contract nu vede o
            # „schimbare" acolo unde e doar alt nume de bucla.
            assert len(bucle) == 1, "%s: doua bucle peste aceeasi lista" % fn.name
            for var in bucle:
                nou = "continut, nume_fisier"
                t = bucle[var].target
                atomice.append((self.poz(t.lineno, t.col_offset),
                                self.poz(t.end_lineno, t.end_col_offset), nou))
            for x in ast.walk(nod_corp):
                if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                        and x.func.id == "_octetii" and len(x.args) == 1 \
                        and isinstance(x.args[0], ast.Name) and x.args[0].id in bucle:
                    atomice.append((self.poz(x.lineno, x.col_offset),
                                    self.poz(x.end_lineno, x.end_col_offset), "continut"))
                elif isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) \
                        and x.value.id in bucle and x.attr == "filename":
                    atomice.append((self.poz(x.lineno, x.col_offset),
                                    self.poz(x.end_lineno, x.end_col_offset), "nume_fisier"))
            j = arg_inv.index(p.arg)
            arg_inv[j] = "[(_octetii(_f), _f.filename) for _f in %s]" % p.arg

        cuprinzatoare = []
        for x in ast.walk(nod_corp):
            if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call) \
                    and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException":
                arg = x.exc.args[0] if x.exc.args else None
                if arg is None:
                    for kw in x.exc.keywords:
                        if kw.arg == "status_code":
                            arg = kw.value
                cls = self._clase_din(arg)
                if cls is None and isinstance(arg, ast.Name) and arg.id in loc:
                    cls = arg.id                      # numele local, rescris mai jos
                assert cls is not None, "%s l.%d: cod fara clasa" % (fn.name, x.lineno)
                mesaj = self._mesaj_nod(x.exc)
                if mesaj is None:
                    txt = '""'
                else:
                    txt = self._taie(self.poz(mesaj.lineno, mesaj.col_offset),
                                     self.poz(mesaj.end_lineno, mesaj.end_col_offset), atomice)
                nou = "%s(%s)" % (("(%s)" % cls) if " if " in cls else cls, txt)
                cuprinzatoare.append((self.poz(x.exc.lineno, x.exc.col_offset),
                                      self.poz(x.exc.end_lineno, x.exc.end_col_offset), nou))
        # local `http = 409 if ... else 404` -> aceeasi expresie, peste clase
        for nume_l, nod in loc.items():
            cls = self._clase_din(nod.value)
            if cls is None:
                continue
            folosit = any(isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call)
                          and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException"
                          and isinstance(x.exc.args[0] if x.exc.args else None, ast.Name)
                          and x.exc.args[0].id == nume_l
                          for x in ast.walk(nod_corp))
            if folosit:
                cuprinzatoare.append((self.poz(nod.value.lineno, nod.value.col_offset),
                                      self.poz(nod.value.end_lineno, nod.value.end_col_offset),
                                      "(%s)" % cls if " if " in cls else cls))

        # `_octetii(fisier)` -> `continut` CUPRINDE `_octetii` -> `_uc_comun._octetii`. Cand doua
        # editari atomice se suprapun, ramane cea mai LARGA: ea e cea care stie ce inseamna intregul.
        atomice = [(i, j, n) for i, j, n in atomice
                   if not any((ci, cj) != (i, j) and ci <= i and j <= cj for ci, cj, _x in atomice)]
        editari = list(cuprinzatoare)
        for i, j, nou in atomice:
            if not any(ci <= i and j <= cj for ci, cj, _n in cuprinzatoare):
                editari.append((i, j, nou))
        vazute = set()
        for i, j, nou in sorted(editari, key=lambda e: -e[0]):
            if i in vazute or not (a <= i and j <= b):
                continue
            vazute.add(i)
            felie = felie[:i - a] + nou + felie[j - a:]
        if coada:
            felie += "    return %s\n" % ", ".join(iesiri) if iesiri else ""
        ind = min((len(l) - len(l.lstrip()) for l in felie.splitlines() if l.strip()), default=4)
        felie = "".join((l[ind:] if l.strip() else l.lstrip(" ")) for l in felie.splitlines(True))
        if coada:
            # Raspunsul a ramas in invelis; importul lui n-are ce cauta in use-case, unde numele nu
            # se mai foloseste. Un strat care importa `Response` fara sa-l atinga e o urma de HTTP
            # lasata acolo degeaba — si un detector viitor ar avea dreptate s-o numeasca.
            pastrate = []
            for l in felie.splitlines(True):
                s = l.strip()
                if s.startswith(("from fastapi.responses import ", "from fastapi import ")):
                    nume = [x.strip().split(" as ")[-1].strip() for x in s.split("import", 1)[1].split(",")]
                    rest = "".join(x for x in felie.splitlines(True) if x is not l)
                    if all(n in X.RASPUNS for n in nume) and \
                            not any(re.search(r"\b%s\b" % re.escape(n), rest) for n in nume):
                        continue
                pastrate.append(l)
            felie = "".join(pastrate)
        return felie, parm_uc, arg_inv, coada, cap

    def semnatura(self, fn):
        s = self.m.text.index("(", self.poz(fn.lineno, fn.col_offset))
        adanc, i = 0, s
        while True:
            if self.m.text[i] == "(":
                adanc += 1
            elif self.m.text[i] == ")":
                adanc -= 1
                if adanc == 0:
                    return self.m.text[s + 1:i]
            i += 1

    def importuri_cerute(self, fn):
        return [self.m.importuri[n] for n in X.externe(fn) if n in self.m.importuri]


def modul(cale):
    seg = (cale or "/").strip("/").split("/")[0] or "radacina"
    return re.sub(r"[^a-z0-9]+", "_", seg.lower())


def ruleaza(doar=None, plan=False):
    v = Val()
    m = v.m
    tinte, refuzate = [], []
    for fn in m.rute():
        c = ast.Module(body=fn.body, type_ignores=[])
        if not any(isinstance(x, ast.Attribute) and x.attr == "get_conn" for x in ast.walk(c)):
            continue
        if doar and fn.name not in doar:
            continue
        p = v.piedici(fn)
        (refuzate if p else tinte).append((fn, p))
    print("DE MUTAT: %d · REFUZATE: %d" % (len(tinte), len(refuzate)))
    if plan:
        for fn, _ in tinte:
            print("  + %-42s -> core/uc_%s.py" % (fn.name, modul(m.cale(fn))))
        for fn, p in sorted(refuzate, key=lambda e: e[0].name):
            print("  - %-42s %s" % (fn.name, " | ".join(sorted(set(p)))))
        return

    pe_modul, invelisuri = {}, []
    for fn, _ in tinte:
        mm = modul(m.cale(fn))
        felie, parm_uc, arg_inv, coada, cap = v.plan(fn)
        antet = "def %s(%s):\n" % (fn.name, ", ".join(parm_uc))
        doc = ('    """[P7 · use-case] Corpul rutei `%s`; docstringul ei a ramas in stratul HTTP."""\n'
               % (m.cale(fn) or "?"))
        text = antet + doc + "".join("    " + l if l.strip() else l for l in felie.splitlines(True))
        d = pe_modul.setdefault(mm, {"functii": [], "importuri": []})
        d["functii"].append(text)
        d["importuri"] += v.importuri_cerute(fn)
        invelisuri.append((fn, mm, arg_inv, coada, cap))

    for mm, d in sorted(pe_modul.items()):
        cale = "core/uc_%s.py" % mm
        nou = not os.path.exists(cale)
        vechi = "" if nou else io.open(cale, encoding="utf-8").read()
        cap = ANTET_UC % {"seg": mm} if nou else ""
        imp = []
        for linie in d["importuri"]:
            if linie and linie not in imp and linie not in vechi and linie not in cap:
                imp.append(linie)
        for oblig in ("from core import erori as _erori", "from core import uc_comun as _uc_comun"):
            if oblig not in vechi and oblig not in imp:
                imp.append(oblig)
        if nou:
            io.open(cale, "wb").write((cap + "\n".join(imp) + "\n\n\n"
                                       + "\n\n\n".join(d["functii"])).encode("utf-8"))
        else:
            arb = ast.parse(vechi)
            ultim = max([n.end_lineno for n in arb.body
                         if isinstance(n, (ast.Import, ast.ImportFrom))] or [1])
            linii = vechi.splitlines(True)
            io.open(cale, "wb").write(("".join(linii[:ultim])
                                       + ("\n".join(imp) + "\n" if imp else "")
                                       + "".join(linii[ultim:]).rstrip("\n") + "\n\n\n"
                                       + "\n\n\n".join(d["functii"]) + "\n").encode("utf-8"))
        print("  %s %s (+%d functii)" % ("creat " if nou else "extins", cale, len(d["functii"])))

    t = m.text
    for fn, mm, arg_inv, coada, cap in invelisuri:
        vechi = v.src(fn)
        vechi = m.text[v.poz(fn.decorator_list[0].lineno, 0) if fn.decorator_list else
                       v.poz(fn.lineno, 0):
                       v.poz(fn.end_lineno, 0) + len(v.linii[fn.end_lineno - 1])]
        assert t.count(vechi) == 1, "%s: sursa nu e unica" % fn.name
        docsrc = ""
        if fn.body and isinstance(fn.body[0], ast.Expr) \
                and isinstance(fn.body[0].value, ast.Constant) \
                and isinstance(fn.body[0].value.value, str):
            docsrc = "    " + v.src(fn.body[0]).lstrip() + "\n"
        apel = "_uc_%s.%s(%s)" % (mm, fn.name, ", ".join(arg_inv))
        if coada:
            interior = coada.replace("_APEL_", apel)
            interior = "".join("    " + l for l in interior.splitlines(True))
        else:
            interior = "        return %s\n" % apel
        dec = "".join("@" + ast.get_source_segment(m.text, d0) + "\n" for d0 in fn.decorator_list)
        nou = (dec + "def %s(%s):\n" % (fn.name, v.semnatura(fn)) + docsrc + cap
               + "    try:\n" + interior
               + "    except _erori.EroareDeDomeniu as e:\n"
               + "        raise _http_din(e)\n")
        t = t.replace(vechi, nou, 1)
    for mm in pe_modul:
        linie = "from core import uc_%s as _uc_%s" % (mm, mm)
        if linie not in t:
            ancora = "from core import uc_comun as _uc_comun"
            assert ancora in t, "nu gasesc ancora de import in main.py"
            t = t.replace(ancora, ancora + "\n" + linie, 1)
    io.open("main.py", "wb").write(t.encode("utf-8"))
    print("[val] %d rute mutate" % len(invelisuri))


if __name__ == "__main__":
    ruleaza(plan="--plan" in sys.argv,
            doar=[a for a in sys.argv[1:] if not a.startswith("--")] or None)
