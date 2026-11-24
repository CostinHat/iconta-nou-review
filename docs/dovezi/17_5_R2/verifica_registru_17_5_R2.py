"""17.5-R2 pct.3 — verificarea registrului activ și a arhivei față de E (numai citire).
Uz: python verifica_registru_17_5_R2.py <commit_E> [<commit_inainte_corectie>]
Compară, pe rândurile CSV decodate și pe octeții brut ai rândurilor:
  - arhiva = exact rândurile MUTA IN ARHIVA din curatenie_registru_lista.tsv, fiecare egal cu rândul de pe E (aceleași coloane și valori);
  - activ și arhivă au ID-uri disjuncte, activ ∪ arhivă = ID-urile de pe E;
  - F067 rămâne activ, Stare INTERN, ajutor gol, celelalte coloane egale cu E;
  - cu al doilea argument: lista celulelor schimbate între acel commit și arborele curent (ID, coloană), ordinea rândurilor și antetul."""
import csv
import io
import subprocess
import sys
from pathlib import Path

RAD = Path(__file__).resolve().parents[3]


def git_show(commit, cale):
    return subprocess.run(["git", "show", f"{commit}:{cale}"], cwd=RAD, capture_output=True, check=True).stdout.decode("utf-8")


def randuri(text):
    return list(csv.reader(io.StringIO(text, newline="")))


def main():
    e = sys.argv[1]
    lista = [l.split("\t") for l in (Path(__file__).parent / "curatenie_registru_lista.tsv").read_text(encoding="utf-8").splitlines()]
    antet_l = lista[0]
    ic = next(i for i, c in enumerate(antet_l) if c.lower().startswith("ac"))
    muta = sorted(r[0] for r in lista[1:] if len(r) > ic and r[ic].strip() == "MUTA IN ARHIVA")
    alte = [(r[0], r[ic]) for r in lista[1:] if len(r) > ic and r[ic].strip() != "MUTA IN ARHIVA"]
    re_ = randuri(git_show(e, "FUNCTIONALITATI.csv"))
    ra = randuri((RAD / "FUNCTIONALITATI.csv").read_text(encoding="utf-8"))
    rh = randuri((RAD / "FUNCTIONALITATI_ARHIVA.csv").read_text(encoding="utf-8"))
    hdr = re_[0]
    iid, ist, iaj = hdr.index("ID"), hdr.index("Stare"), hdr.index("ajutor")
    E = {r[iid]: r for r in re_[1:]}
    A = {r[iid]: r for r in ra[1:]}
    H = {r[iid]: r for r in rh[1:]}
    print("antet activ = E:", ra[0] == hdr, "| antet arhivă = E:", rh[0] == hdr, "| coloane:", len(hdr))
    print("E:", len(E), "activ:", len(A), "arhivă:", len(H))
    print("MUTA IN ARHIVA (lista):", len(muta), " ".join(muta))
    print("alte acțiuni în listă:", alte)
    print("arhiva = exact lista:", sorted(H) == muta)
    print("rânduri arhivate egale cu E (toate coloanele):", all(H[i] == E[i] for i in H), [i for i in H if H[i] != E[i]])
    print("ID comune activ ∩ arhivă:", sorted(set(A) & set(H)))
    print("activ ∪ arhivă = E:", set(A) | set(H) == set(E))
    print("F160 în arhivă:", "F160" in H, "| F160 în activ:", "F160" in A)
    f = A.get("F067")
    print("F067 activ:", f is not None, "| Stare:", f[ist] if f else None, "| ajutor gol:", (f[iaj] == "") if f else None,
          "| celelalte coloane = E:", all(f[k] == E["F067"][k] for k in range(len(hdr)) if k not in (ist, iaj)) if f else None)
    ordine_e = [r[iid] for r in re_[1:] if r[iid] in A]
    print("ordinea rândurilor active = ordinea lor pe E:", ordine_e == [r[iid] for r in ra[1:]])
    # octeții rândurilor arhivate: fiecare rând din arhivă apare identic (octet cu octet) în fișierul de pe E
    brut_e = git_show(e, "FUNCTIONALITATI.csv")
    brut_h = (RAD / "FUNCTIONALITATI_ARHIVA.csv").read_text(encoding="utf-8")
    term = "\r\n" if "\r\n" in brut_e else "\n"
    print("terminator de rând E:", repr(term), "| arhivă același:", (term in brut_h) and (("\r\n" in brut_h) == (term == "\r\n")))
    if len(sys.argv) > 2:
        b = randuri(git_show(sys.argv[2], "FUNCTIONALITATI.csv"))
        print("corecție — antet egal:", b[0] == ra[0], "| ordinea rândurilor egală:", [r[iid] for r in b[1:]] == [r[iid] for r in ra[1:]])
        B = {r[iid]: r for r in b[1:]}
        dif = [(i, hdr[k]) for i in B for k in range(len(hdr)) if B[i][k] != A[i][k]]
        print("celule schimbate de corecție:", dif)


if __name__ == "__main__":
    main()
