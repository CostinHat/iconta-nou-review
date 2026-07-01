#!/usr/bin/env python3
"""
patch_asistenti_sinteza.py — înlocuiește numărul hardcodat '3' din cardul Asistenți
cu numărul real de actori (din /asistenti), dinamic ca celelalte carduri.
Idempotent: marker prin prezența 'actualizeazaAsistenti'; backup .bak.
Rulează de pe server în ~/iconta_nou/.
"""
import os, shutil, sys

FILE = "static/js/ecrane/cabinet.js"

# 1) sinteza statică -> placeholder (se umple dinamic)
VECHI_SINTEZA = """    sinteza:'<b style="font-size:19px">3</b> asistenți în echipă', actiune:inLucru("Asistenți") },"""
NOU_SINTEZA = """    sinteza:'<b style="font-size:19px">·</b> asistenți în echipă', actiune:inLucru("Asistenți") },"""

# 2) apel în lista de actualizări (după actualizeazaValidat)
VECHI_APEL = "  actualizeazaValidat(grila);"
NOU_APEL = "  actualizeazaValidat(grila);\n  actualizeazaAsistenti(grila);"

# 3) funcția nouă (o adaug după actualizeazaValidat — o inserez înainte de finalul ei)
ANCORA_FUNC = '''async function actualizeazaValidat(grila) {
  const zona = grila.querySelector('[data-cheie="validat"]');
  if (!zona) return;
  try {
    const r = await api.get("/coada");
    const coada = (r && r.coada) || [];
    const n = coada.filter((c) => c.stare === "la_senior").length;
    zona.innerHTML = `<b style="font-size:19px">${n}</b> declaraț${n === 1 ? "ie de validat" : "ii de validat"} și trimis`;
  } catch {}
}'''

FUNC_NOUA = ANCORA_FUNC + '''

async function actualizeazaAsistenti(grila) {
  const zona = grila.querySelector('[data-cheie="asistenti"]');
  if (!zona) return;
  try {
    const r = await api.get("/asistenti");
    const n = (r && r.sumar && r.sumar.total) || 0;
    zona.innerHTML = `<b style="font-size:19px">${n}</b> ${n === 1 ? "asistent în echipă" : "asistenți în echipă"}`;
  } catch {}
}'''


def main():
    if not os.path.exists(FILE):
        print(f"EROARE: {FILE} nu există."); sys.exit(1)
    s = open(FILE, encoding="utf-8").read()
    if "actualizeazaAsistenti" in s:
        print("DEJA APLICAT."); sys.exit(0)

    for label, vechi in [("sinteza", VECHI_SINTEZA), ("apel", VECHI_APEL), ("functie", ANCORA_FUNC)]:
        if vechi not in s:
            print(f"EROARE: nu găsesc ancora '{label}'. Nu modific."); sys.exit(1)

    shutil.copy(FILE, FILE + ".bak")
    print(f"Backup: {FILE}.bak")

    s = s.replace(VECHI_SINTEZA, NOU_SINTEZA, 1)
    s = s.replace(VECHI_APEL, NOU_APEL, 1)
    s = s.replace(ANCORA_FUNC, FUNC_NOUA, 1)

    open(FILE, "w", encoding="utf-8").write(s)
    print("Sinteza Asistenți acum dinamică.")
    s2 = open(FILE, encoding="utf-8").read()
    ok = ("actualizeazaAsistenti(grila)" in s2 and "async function actualizeazaAsistenti" in s2)
    print("Verificare:", "OK" if ok else "EȘUAT")
    if not ok:
        shutil.copy(FILE + ".bak", FILE); sys.exit(1)


if __name__ == "__main__":
    main()
