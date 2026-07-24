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

**NUMEROTARE CANONICĂ (fixată 23.07.2026):** pozițiile 1–12 = ordinea ACESTEI liste, nu ordinea în care sunt
atacate. Se scrie „poziția N" (fixă), nu „N/12" derivat din ordinea de lucru. Ordinea DE ATAC o dă Costin,
independent de poziție. (Corecție la commitul de închidere care numea Control fiscal „1/12" — e poziția **2**.)
**ÎNCHISE: poziția 1 (Declarații) + poziția 2 (Control fiscal) + poziția 3 (Termene), 23.07.2026. Rămân 9** (4–12).

Ecrane de parcurs (din DE_FACUT.md §3, verificatorul e curat pe ele dar nu prinde randarea):

1. [x] **Declarații** — **ÎNCHIS 23.07.2026** (comituri 497c83c→a552a78 + d6485f4 + ac288ea). `declaratii_api.py` + `declaratii.js`.
   Verificat vizual pe 3 firme (2 PFA + 1 SRL): dropdown D100/D101/D406 dezactivate + temei pe PFA, cardul Declarații
   vizibil la PFA, filtrarea cardurilor pe `regim_contabil`. Reparat (vezi ISTORIC 23.07 poz.1): G1 `neaplicabile_forma`
   (o mapare, 3 consumatori, poartă 422), `DOAR_SRL` pe Declarații = fals negativ, listele `DOAR_SRL`/`DOAR_PFA`
   eliminate (cardul declară `regim`, vizibilitatea derivă prin `regim_contabil` — gardă CARD_REGIM), G2/G3/G4.
   BUG cache/instanță surfacat aici: antet lipsă pe calea Termene (firme.js importat cu versiuni divergente) → gardă
   IMPORT_VERSIUNE (DS cap.19) + antet explicit în meniuFirma (DS cap.9).
   RĂMAS consemnat (nereparat): Casă card „ambele" (5311 partidă dublă, filtrare fină în interior); D710 LIVE inaccesibil UI; D301 fără writer.
2. [x] **Control fiscal** — **ÎNCHIS 23.07.2026** (SRL+PFA, comituri ac5ab4f→9693c1f). Semafor cross-portofoliu + Declarație vs contabilitate. `control_fiscal_api.py` + `control.js`.
   **Consolidare 24.07** (comituri 4e43254 + ac7e135, vezi ISTORIC 24.07 poz.2): 3 renderere per-firmă alegeau chei `vc` pe nume, fiecare cu altă omisiune tăcută (DANTE: salarii + 5121 nu apăreau pe card) → renderer UNIC de corp (`control_verdict.js`, detaliu + card fișă) + gardă **VERDICT_PARITATE** cu 2 parități (randare + severitate); `ecranVerificari` scoped + declarat (`VC_VERIFICARI`). DS cap.20. Nimic vizual nou — nu cere re-verificare pe ecran.
3. [x] **Termene** — **ÎNCHIS 23.07.2026** (comituri 80c260b→b3fb563). `termene_api.py` + `termene.js`.
   8 reparații (vezi ISTORIC 23.07 poz.3): sub-raportare D394/D406/D101 (consolidare pe primitivă unică), D390 pe
   fapt lunar (nu flag fix), d205_vs_457 roșu fals (cod mort scos), neevaluate gri cu temei, regresie d301 negardat,
   §4 mărginire TVA, edge decembrie an+1, dataLunga → dataRo + gard DATA_DIALECT extins. Prezentare P1–P4.
   RĂMAS vizual (Costin): eticheta de perioadă cu an se vede abia în decembrie (fereastra traversează anul).
4. [ ] **Setări cont** (profil, parolă, cabinet, competențe, chei API)
5. [ ] **Recomandă**
6. [ ] **Admin*** (Raportări, Activitate cabinete, Sănătate server — grafice SVG)
7. [ ] **e-Transport** (XML upload manual)
8. [ ] **Produse**
9. [ ] **Tipare** (asistenți)
10. [ ] **Semafor** (validat / de validat)
11. [ ] **Pachete lunare**
12. [ ] **Capacitate**

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

---

## E. F131 Scadențar (construit 17.07) — verificare vizuală

Cardul **Facturi → Scadențar** (și badge-ul roșu pe cardul Facturi):
- [ ] Badge roșu cu nr. de restante apare pe cardul Facturi (dacă există restante).
- [ ] Scadențar: rezumat cu 3 pastile-semafor (restante roșu / scad curând galben / în termen verde), listă sortată pe urgență.
- [ ] Bulinele de stare per factură au culorile corecte (cap.8).
- [ ] Buton „Fișă client" comută la vederea agregată (sold + restant per client).
- [ ] Comutator opt-in (checkbox) — la activare fără email de firmă → mesaj de eroare (nu se activează); cu email → se activează.
- [ ] Supape per factură (când opt-in activ): „nu notifica" / „amână 30 zile" / „reia" funcționează și starea se reflectă.
- [ ] Sume prin `bani()`, date prin `dataRo()` (fără format brut).

Backend/logică deja testate prin SSH (18 teste + funcțional); aici doar randarea.

## F. F136 Adeverință salariat (construit 17.07) — verificare vizuală

Salariați → rând salariat → buton **Adeverință**:
- [ ] Formularul se deschide ca fereastră; câmpuri DS (`.camp`/`.camp-input`), scop marcat obligatoriu (`.oblig`).
- [ ] Caseta de atenție (bancă) apare clar.
- [ ] „Generează PDF" → se deschide PDF-ul; conține firma+CUI, nume+CNP, funcție COR, data angajării, brut+net, vechime, scop, temeiul art. 34(5).
- [ ] Fără scop completat → mesaj de eroare (nu generează).

## G. F135 Pontaj (construit 17.07) — verificare vizuală

Salariați → rând salariat → buton **Pontaj**:
- [ ] Grila arată doar zilele lucrătoare (weekendul + sărbătorile legale, inclusiv Vinerea Mare, lipsesc).
- [ ] Rezumatul (prezent/absent/concediu) se actualizează la schimbarea unei stări.
- [ ] Salariat angajat la mijloc de lună: zilele dinainte de angajare nu apar.
- [ ] Navigarea ← lună / lună → funcționează.
