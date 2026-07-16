# Checklist sesiune browser — ce NU se poate testa prin SSH

Pregătit 16.07.2026 după re-testarea SSH completă (555 teste verzi, 4 bug-uri reparate).
Aici sunt DOAR verificările care cer ochi/telefon: randare reală, responsive, PWA.
Criteriile sunt obiective (Design System + breakpoint-uri reale din CSS), nu de gust.

Referință: `DESIGN_SYSTEM.md` (cap.1–16). Breakpoint-uri reale în CSS: **480, 520, 560, 760, 900px**.
Gardianul mecanic (`verificator_conformitate.py`) e deja curat pe toate — aici prindem ce el nu vede.

---

## A. PWA & mobil (P4.18–19) — pe telefon real

- [ ] **P4.18 iOS** (deja făcut 14.07, re-confirmare): Safari → Adaugă pe ecran principal → pornește **standalone** (fără bara Safari) → funcționează **offline** (avion pornit, deschide app).
- [ ] **P4.18 Android**: Chrome → banner/meniu "Instalează aplicația" → pornire standalone → offline OK. (rămas secundar din 14.07)
- [ ] **P4.19 Pozează bon**: pe telefon, portal → Pozează bon → **cameră directă** se deschide (nu doar galerie) → **multi-imagine** (2+ poze pe același bon) → flux până la nota generată.
- [ ] Manifest: iconă corectă pe ecranul principal (nu iconă generică), nume scurt lizibil.

## B. Responsive (P4.20–21) — DevTools (F12 → device toolbar) + telefon

- [ ] **P4.20 Portal <400px** (setează 360px): toate cardurile intră în lățime, **fără scroll orizontal**, fără text tăiat. Ecrane: Acasă, Facturi, Declarații, Solicitări, Cifrele firmei.
- [ ] Verifică la 480px și 520px (breakpoint-uri reale) că tranziția e curată, nu sare layout-ul.
- [ ] **P4.21 Landing <900px**: meniu/hero se rearanjează corect.
- [ ] **P4.21 Landing <560px**: o coloană, butoane full-width, fără overflow.

---

## C. Audit vizual ecrane (~20 neverificate cu ochii) — cabinet, desktop

Pentru FIECARE ecran, 4 verificări obiective din Design System:

1. **Anatomie fereastră** (cap.1 + cap.9): entitate-antet → titlu `h2` → corp. Cardul se deschide ca **fereastră/modal**, niciodată inline (cap.2a).
2. **Aliniere tabele** (cap.4): text la stânga, **sume la dreapta** cu separatorul de mii aliniat pe coloană.
3. **Panouri** (cap.16 + cap.2): fundal alb + bordură `#b9c2cf`; formularele **NU** într-un wrapper alb pe gri (caseta invizibilă gri-pe-gri).
4. **Semafoare** (cap.8): culori din tokeni (verde/galben/roșu), nu nuanțe ad-hoc.

Ecrane de parcurs (din DE_FACUT.md §3, verificatorul e curat pe ele dar nu prinde randarea):

- [ ] Declarații (listă + flux 3 pași per declarație)
- [ ] Control fiscal (semafor cross-portofoliu + secțiunea Declarație vs contabilitate)
- [ ] Termene
- [ ] Setări cont (profil, parolă, cabinet, competențe, chei API)
- [ ] Recomandă
- [ ] Admin* (Raportări, Activitate cabinete, Sănătate server — grafice SVG)
- [ ] e-Transport (XML upload manual)
- [ ] Produse
- [ ] Tipare (asistenți)
- [ ] Semafor (validat / de validat)
- [ ] Pachete lunare
- [ ] Capacitate

## D. Categorii neatacate sistematic (DE_FACUT §3.2) — de decis, nu neapărat de reparat

- [ ] **Spacing/padding inline**: închis explicit ca datorie acceptată (v2.11). Doar de confirmat că nu deranjează vizual.
- [ ] **Wrapper alb pe formulare** (cap.2): verificatorul n-are regulă; prins doar 1 manual. De scanat vizual formularele.
- [ ] **Aliniere tabele** (cap.4): sume la dreapta — neverificat sistematic pe toate tabelele.
- [ ] **Anatomia ferestrei** (cap.1): entitate-antet/titlu-h2-corp — neauditată vizual pe toate.

---

## Ce e DEJA verificat (NU relua)
- Backend/logică/declarații/securitate/provisioning/cron: 555 teste + validare DUK (sesiunea SSH 16.07).
- Gardian mecanic DS: `verificator_conformitate.py` = 0 pe toate ecranele (formatare bani/dată/procent, culori, iconițe, tipografie, borduri/rază, semafor).
- Audit vizual ~22 ecrane deja făcut 14.07 (INCHISE azi în DE_FACUT §Actualizare).

## Bug găsit în sesiune → deschide-l pe telefon/browser și confirmă vizual dacă vrei
- Niciunul din cele 4 bug-uri reparate azi nu e vizual (toate backend). Nimic de re-confirmat cu ochii.
