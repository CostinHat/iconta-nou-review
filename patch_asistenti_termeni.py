#!/usr/bin/env python3
"""
patch_asistenti_termeni.py — uniformizează terminologia: 'actor/actori' -> 'asistent/asistenți'
în TEXTELE AFIȘATE din asistenti.js (nu în cod/variabile/comentarii).
Idempotent: marker prin prezența 'asistenții cabinetului'; backup .bak.
Rulează de pe server în ~/iconta_nou/.
"""
import os, shutil, sys

FILE = "static/js/ecrane/asistenti.js"

# Înlocuiri țintite doar pe stringuri afișate userului
INLOCUIRI = [
    ('Se încarcă actorii…', 'Se încarcă asistenții…'),
    ('Nu am putut încărca actorii.', 'Nu am putut încărca asistenții.'),
    ('Actorii cabinetului: roluri', 'Asistenții cabinetului: roluri'),
    ('${sumar.total} actori · ${sumar.activi} activi', '${sumar.total} asistenț${sumar.total === 1 ? "ă" : "i"} · ${sumar.activi} activ${sumar.activi === 1 ? "" : "i"}'),
    ('Niciun actor în cabinet.', 'Niciun asistent în cabinet.'),
    ('Dezactivează actorul', 'Dezactivează asistentul'),
]


def main():
    if not os.path.exists(FILE):
        print(f"EROARE: {FILE} nu există."); sys.exit(1)
    s = open(FILE, encoding="utf-8").read()
    if 'Asistenții cabinetului' in s:
        print("DEJA APLICAT."); sys.exit(0)

    lipsa = [v for v, _ in INLOCUIRI if v not in s]
    if lipsa:
        print("ATENȚIE: nu am găsit unele ancore:")
        for x in lipsa: print("  -", x)
        print("Nu modific (verifică manual).")
        sys.exit(1)

    shutil.copy(FILE, FILE + ".bak")
    print(f"Backup: {FILE}.bak")

    for vechi, nou in INLOCUIRI:
        s = s.replace(vechi, nou, 1)

    open(FILE, "w", encoding="utf-8").write(s)
    print(f"Înlocuite {len(INLOCUIRI)} texte: actor/actori -> asistent/asistenți.")
    print("Verificare:", "OK" if "Asistenții cabinetului" in open(FILE, encoding="utf-8").read() else "EȘUAT")


if __name__ == "__main__":
    main()
