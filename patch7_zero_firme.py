#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch7_zero_firme.py — regula 'zero firme'.

Backend (core/asistenti_api.py):
  + _numara_firme()
  + aplica_regula_zero_firme(): la 0 firme -> competente golite;
    angajat -> activ=false; admin_firma -> cont intact.
Backend (main.py):
  + POST /asistenti/{uid}/finalizeaza-firme
Frontend (static/js/ecrane/asistenti.js):
  + avertisment confirm la ultima firma scoasa
  + apel /finalizeaza-firme dupa sincronizarea firmelor
Reactivarea ramane MANUALA (nu se reactiveaza automat la reatribuire).
Idempotent: marker + .bak + py_compile + node --check.
"""
import os, shutil, py_compile, subprocess

BASE = "/home/costin/iconta_nou"
ASIST = os.path.join(BASE, "core", "asistenti_api.py")
MAIN  = os.path.join(BASE, "main.py")
JS    = os.path.join(BASE, "static", "js", "ecrane", "asistenti.js")

M_ASIST = "# [patch7_zero_firme]"
M_MAIN  = "# [patch7_finalizeaza_firme]"
M_JS    = "/* [patch7_zero_firme] */"


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def once(text, old, new, label):
    if old not in text: raise SystemExit("ANCORA LIPSA: " + label)
    if text.count(old) != 1: raise SystemExit("ANCORA NEUNICA: " + label)
    return text.replace(old, new)


# ---------- 1. backend asistenti_api.py: helperi ----------
HELPERS = '''

''' + M_ASIST + '''
def _numara_firme(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT COUNT(*) FROM {TABEL_LEGATURA_FIRME} WHERE {COL_USER} = %s",
            (user_id,),
        )
        return int(cur.fetchone()[0])


def aplica_regula_zero_firme(conn, cabinet_id, user_id):
    """La ZERO firme: competentele se golesc.
    angajat -> cont dezactivat (ramane in istoric).
    admin_firma -> contul ramane intact (iese doar din procesatori)."""
    actor = _actor_din_cabinet(conn, cabinet_id, user_id)
    if not actor:
        return {"ok": False, "cod": "actor_inexistent"}
    if _numara_firme(conn, user_id) > 0:
        return {"ok": True, "aplicat": False}
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.users SET poate_pregati=false, poate_valida=false, "
            "poate_depune=false WHERE id=%s AND accounting_firm_id=%s",
            (user_id, cabinet_id),
        )
        dezactivat = False
        if actor["rol"] == "angajat":
            cur.execute(
                "UPDATE public.users SET activ=false "
                "WHERE id=%s AND accounting_firm_id=%s",
                (user_id, cabinet_id),
            )
            dezactivat = True
    return {"ok": True, "aplicat": True, "dezactivat": dezactivat,
            "rol": actor["rol"]}
'''

# ancora: inserez helperii inainte de blocul DEZACTIVARE
A_ASIST = ("# ============================================================\n"
           "#  DEZACTIVARE \u2014 DB")


# ---------- 2. main.py: ruta finalizeaza-firme ----------
RUTA = '''
''' + M_MAIN + '''
@app.post("/asistenti/{uid}/finalizeaza-firme")
def asistenti_finalizeaza_firme(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.aplica_regula_zero_firme(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r
'''
# ancora: dupa ruta reactiveaza, inainte de markerul calitate
A_MAIN = "# [patch_asistenti_calitate]"


# ---------- 3. frontend: blocul de salvare ----------
JS_OLD = '''    box.querySelector("#asi-salveaza").onclick = async () => {
      err.textContent = "";
      const valNou = box.querySelector('[data-perm="poate_valida"]')?.checked && !a.poate_valida;
      if (valNou && !confirm(`Acorzi dreptul de validare lui ${nume} (Nivel 2)? Asigura-te ca acopera tipurile pe care le va valida.`)) return;
      try {
        const permVals = {};
        box.querySelectorAll("[data-perm]").forEach((cb) => { permVals[cb.dataset.perm] = cb.checked; });
        await api.post(`/asistenti/${uid}/permisiuni`, permVals);
        if (a.atribuire_relevanta) {
          const initiale = {};
          firme.forEach((f) => (initiale[f.id] = f.atribuit));
          const tasks = [];
          box.querySelectorAll("[data-tid]").forEach((cb) => {
            const tid = Number(cb.dataset.tid);
            if (cb.checked && !initiale[tid]) tasks.push(api.post(`/asistenti/${uid}/firme/${tid}`));
            if (!cb.checked && initiale[tid]) tasks.push(api.del(`/asistenti/${uid}/firme/${tid}`));
          });
          await Promise.all(tasks);
        }
        nav.inapoi();
        randeazaAsistenti(corp, nav);
      } catch { err.textContent = "Nu am putut salva. Incearca din nou."; }
    };'''

JS_NEW = '''    box.querySelector("#asi-salveaza").onclick = async () => {
      err.textContent = "";
      const valNou = box.querySelector('[data-perm="poate_valida"]')?.checked && !a.poate_valida;
      if (valNou && !confirm(`Acorzi dreptul de validare lui ${nume} (Nivel 2)? Asigura-te ca acopera tipurile pe care le va valida.`)) return;
      ''' + M_JS + '''
      if (a.atribuire_relevanta) {
        const bifate = [...box.querySelectorAll("[data-tid]")].filter((cb) => cb.checked).length;
        if (bifate === 0) {
          const mesaj = a.rol === "angajat"
            ? `${nume} ramane fara nicio firma. Competentele se sterg si contul se DEZACTIVEAZA (ramane in istoric). Continui?`
            : `${nume} ramane fara nicio firma. Competentele se sterg si iese din lista de procesatori (contul de administrator ramane). Continui?`;
          if (!confirm(mesaj)) return;
        }
      }
      try {
        const permVals = {};
        box.querySelectorAll("[data-perm]").forEach((cb) => { permVals[cb.dataset.perm] = cb.checked; });
        await api.post(`/asistenti/${uid}/permisiuni`, permVals);
        if (a.atribuire_relevanta) {
          const initiale = {};
          firme.forEach((f) => (initiale[f.id] = f.atribuit));
          const tasks = [];
          box.querySelectorAll("[data-tid]").forEach((cb) => {
            const tid = Number(cb.dataset.tid);
            if (cb.checked && !initiale[tid]) tasks.push(api.post(`/asistenti/${uid}/firme/${tid}`));
            if (!cb.checked && initiale[tid]) tasks.push(api.del(`/asistenti/${uid}/firme/${tid}`));
          });
          await Promise.all(tasks);
          await api.post(`/asistenti/${uid}/finalizeaza-firme`);
        }
        nav.inapoi();
        randeazaAsistenti(corp, nav);
      } catch { err.textContent = "Nu am putut salva. Incearca din nou."; }
    };'''


def main():
    for p in (ASIST, MAIN, JS):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)

    # 1. backend helperi
    s = open(ASIST, encoding="utf-8").read()
    if M_ASIST in s:
        print("asistenti_api.py deja patch-at — sar.")
    else:
        backup(ASIST, ".bak_p7")
        s = once(s, A_ASIST, HELPERS.rstrip() + "\\n\\n\\n" + A_ASIST, "helperi zero firme")
        open(ASIST, "w", encoding="utf-8").write(s)
        py_compile.compile(ASIST, doraise=True)
        print("  asistenti_api.py: helperi + regula zero firme")

    # 2. main.py ruta
    s = open(MAIN, encoding="utf-8").read()
    if M_MAIN in s:
        print("main.py deja patch-at — sar.")
    else:
        backup(MAIN, ".bak_p7")
        s = once(s, A_MAIN, RUTA.rstrip() + "\\n\\n\\n" + A_MAIN, "ruta finalizeaza-firme")
        open(MAIN, "w", encoding="utf-8").write(s)
        py_compile.compile(MAIN, doraise=True)
        print("  main.py: POST /asistenti/{uid}/finalizeaza-firme")

    # 3. frontend
    s = open(JS, encoding="utf-8").read()
    if M_JS in s:
        print("asistenti.js deja patch-at — sar.")
    else:
        backup(JS, ".bak_p7")
        s = once(s, JS_OLD, JS_NEW, "bloc salvare")
        open(JS, "w", encoding="utf-8").write(s)
        r = subprocess.run(["node", "--check", JS], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("node --check a esuat:\\n" + r.stderr)
        print("  asistenti.js: avertisment zero firme + finalizare")

    print("\\nGATA. Restart 8010 (backend) + Ctrl+Shift+R.")
    print("Rollback: .bak_p7")


if __name__ == "__main__":
    main()
