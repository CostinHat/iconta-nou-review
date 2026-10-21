# -*- coding: utf-8 -*-
"""[A6, 18.09.2026] Atribuirea plăților de dividende (debit 457) pe DISTRIBUIRI (credit 457), FIFO pe
dată, ca impozitul să se aplice cu cota de la DATA DISTRIBUIRII — nu de la 31.12 al anului declarației.

[lotul 10, decizia Costin A, verbatim în DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”] „Varianta 2: D205 include și
dividendele distribuite neplătite la 31.12, pe anul distribuirii, cu impozitul datorat (Cap. V are rânduri separate distribuite /
plătite).” Încadrarea pe coloane, din instrucțiunile oficiale (OPANAF 179/2022, anexa 1, cap.II pct.9, `anaf_surse/
opanaf_179_2022_d205_d207_baza.txt`): „Col. 3 - se înscrie, pe fiecare beneficiar de venit, suma reprezentând totalul venitului distribuit
din dividende, într-un an fiscal. Col. 4 - [...] totalul venitului plătit acţionarilor sau asociaţilor din dividendele distribuite, într-un
an fiscal. Col. 5 - [...] baza de calcul al impozitului, într-un an fiscal. Col. 6 - [...] totalul impozitului pe venit calculat şi reţinut
în cursul anului. Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acţionarilor sau asociaţilor până la sfârşitul
anului în care s-a aprobat distribuirea acestora se cuprinde în declaraţia aferentă perioadei în care s-a aprobat distribuirea
dividendelor.” Și CF art.97 alin.(7): „În cazul dividendelor [...] distribuite, dar care nu au fost plătite acționarilor/asociaților/
investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data
de 25 ianuarie inclusiv a anului următor distribuirii.”
Deci, pe anul `an`: divid_D (col.3) = distribuirile anului; divid_P (col.4) = plățile anului, oricând ar fi fost distribuit dividendul;
baza1 / imp1 (col.5 / col.6) = distribuirile ANULUI cu impozitul lor — plătite sau nu la 31.12. Un dividend distribuit într-un an și plătit
în anul următor are baza și impozitul în anul distribuirii; în anul plății apare numai la „plătite”, cu baza și impozitul 0 — nu se declară
de două ori. *INTERPRETARE CU TEMEI* (col.4 „într-un an fiscal” = plățile anului, ca la col.3 și col.5, care se citesc pe același an):
alternativa respinsă — plata din anul următor să nu mai apară deloc — ar lăsa „plătite” sub „distribuite” pe toți anii, deși dividendul
s-a plătit. Validatorul DUK D205 (v8, `Benef`: R39a / R39b / R44 / R45) cere numai valori >= 0 pe divid_D, divid_P, baza1, imp1, fără
legătură între ele.

Legea 141/2025 art. VII: 16% pe dividendele DISTRIBUITE începând cu 01.01.2026; alin.(2): dividendele
interimare distribuite în 2025 rămân la 10% chiar dacă se plătesc/regularizează în 2026 (fără
recalculare). Deci cota se decide după data creditului 457 (distribuirea), nu după anul plății.

MODUL NEUTRU (intrare partajată, ca `common.cota`): primește mișcările 457 și o funcție de cotă,
întoarce impozitul PONDERAT pe rata fiecărei distribuiri. Cele două căi (generatorul `d205` și
reconcilierea `d205_reconciliere`) își trag SINGURE mișcările din registru (SQL propriu, fiecare cu
repo-ul ei), apoi cheamă acest atribuitor determinist. Independența rămâne acolo unde a fost mereu — la
CITIREA din sursă — nu la aritmetica ratei (care și azi era aceeași formulă `parte × cotă` în ambele).
"""
from decimal import Decimal


def _d(x):
    return Decimal(str(x or 0))


def _transe(miscari, an):
    """[lotul 10, deficiența 431] Tranșele anului `an`: (fel, data_distribuirii, suma), fel ∈ {"distribuit", "platit"}; „platit”
    e dividendul BRUT plătit (netul plus impozitul reținut pe el). „distribuit” = distribuirile anului (minus compensările), pe care se
    calculează baza și impozitul (decizia A, antetul modulului).

    SOLDUL DE DESCHIDERE (`preluat`, [lotul 10, decizia Costin A — generalizarea pe clasă]): soldul creditor al lui 457 din balanța de
    deschidere e un dividend distribuit ÎNAINTE de evidența din iConta.eu — o distribuire deschisă la coada FIFO, fără tranșă
    „distribuit” (baza și impozitul ei sunt în declarația anului distribuirii, depusă înainte de preluare). Plata lui după preluare
    intră numai la „plătite”. Fără el, plata ar fi fost luată drept distribuire nouă și impozitată a doua oară.

    DOUĂ COZI FIFO, fiecare cu distribuirile ei deschise [data, brut rămas, impozit înregistrat rămas]:
      · dividendele ANUALE, pe 457: credit 457 = distribuire; 457 = 446 = impozitul înregistrat (`impozit`); debit 457 spre
        bancă / casă / altul = plata netului (`platit`); 457 = 463 = compensarea cu interimarele deja plătite (`compensat`, OMFP
        1802/2014 pct.423^2), care stinge distribuirea FĂRĂ plată și o scoate din distribuitul anului — dividendul acela a fost
        distribuit și plătit ca interimar, iar impozitul lui nu se recalculează (Legea 141/2025 art.VII alin.(2): „În cazul
        dividendelor distribuite în baza situaţiilor financiare interimare [...] cota de impozit pe dividende este de 10%, fără
        recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situaţiilor financiare anuale”);
      · dividendele INTERIMARE, pe 456: distribuirea 463 = 456, impozitul 456 = 446, plata 456 = 512x / 531x. Sunt dividende (CF
        art.7 pct.11: „dividend - o distribuire în bani sau în natură, efectuată de o persoană juridică unui participant, drept
        consecință a deținerii unor titluri de participare”), deci intră în D205 la plată. Pe 456 se decontează și capitalul (aport,
        reducere): o plată 456 fără distribuire interimară deschisă NU e dividend și nu se ia.

    IMPOZITUL ÎNREGISTRAT NU E PLATĂ. Nota de dividende poate înregistra impozitul (457 = 446) la distribuire, înainte de plată (forma
    notei din Operațiuni speciale, „Dividendul se plătește acum: Nu”); asociatul n-a primit nimic. Impozitul se reține la plată (CF
    art.97 alin.(7): „Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice,
    odată cu plata dividendelor”), deci tranșa plătită se socotește la plata netului: brutul plătit = netul × brut rămas / net rămas
    al distribuirii (netul rămas = brutul rămas minus impozitul înregistrat pe ea). Fără impozit înregistrat, brutul plătit = suma
    plătită (regula de dinainte). Impozitul din aceeași notă cu o distribuire se leagă întâi de ea, apoi FIFO.
    O plată 457 (sau un impozit 457 = 446) fără distribuire deschisă (inconsecvență de registru) se atribuie propriei date — ca
    distribuire ȘI plată a acelei zile (conservator, nu se pierde: baza și impozitul ei intră în anul ei)."""
    cozi = {"": [], "_interimar": []}
    for m in miscari:
        d = m["data"]
        preluat = _d(m.get("preluat"))
        if preluat > 0:   # soldul de deschidere 457: distribuire deschisă, fără tranșă „distribuit” (vezi mai sus)
            cozi[""].append([d, preluat, Decimal(0)])
        for suf, coada in cozi.items():
            dist = _d(m.get("distribuit" + suf))
            noua = None
            if dist > 0:
                noua = [d, dist, Decimal(0)]
                coada.append(noua)
                if d.year == an:
                    yield "distribuit", d, dist
            rest = _d(m.get("impozit" + suf))
            for e in ([noua] if noua else []) + [x for x in coada if x is not noua]:
                if rest <= 0:
                    break
                ia = min(rest, e[1] - e[2])
                if ia > 0:
                    e[2] += ia
                    rest -= ia
            if rest > 0 and d.year == an and not suf:
                yield "distribuit", d, rest
                yield "platit", d, rest
            for fel in ("compensat", "platit"):
                rest = _d(m.get(fel + suf)) if (fel == "platit" or not suf) else Decimal(0)
                while rest > 0 and coada:
                    e = coada[0]
                    net = e[1] - e[2]
                    if fel == "compensat" or net <= 0:   # brutul se stinge ca atare (compensare; sau nimic de dat în net)
                        brut = ia = min(rest, e[1])
                        e[2] -= e[2] * brut / e[1]
                    else:   # plata netului: brutul plătit = netul × brut / net, impozitul înregistrat pe el se consumă
                        ia = min(rest, net)
                        brut = e[1] if ia == net else ia * e[1] / net
                        e[2] -= brut - ia
                    rest -= ia
                    if d.year == an:
                        yield ("platit", e[0], brut) if fel == "platit" else ("distribuit", e[0], -brut)
                    e[1] -= brut
                    if e[1] <= 0:
                        coada.pop(0)
                if rest > 0 and d.year == an and fel == "platit" and not suf:
                    yield "distribuit", d, rest
                    yield "platit", d, rest


def impozit_ponderat(miscari, an, rate_fn):
    """`miscari`: iterabil de dict-uri {'data': date, 'distribuit', 'platit' [, 'impozit', 'compensat', 'distribuit_interimar',
    'impozit_interimar', 'platit_interimar']}, SORTATE crescător după (data, id) (`_transe`). `an`: anul declarației D205. `rate_fn(data_distribuire)
    -> Decimal` (fracție, ex. 0.10 / 0.16).

    Întoarce (impozit_ponderat, platit_an, distribuit_an):
      - impozit_ponderat = Σ, peste tranșele DISTRIBUITE în anul `an` (plătite sau nu la 31.12 — decizia A, antetul), tranșă ×
        rate_fn(data distribuirii ei) -> imp1;
      - platit_an     = Σ plăților din anul `an`, oricând ar fi fost distribuit dividendul -> divid_P;
      - distribuit_an = Σ distribuirilor din anul `an`, fără partea compensată cu interimarele -> divid_D și baza1."""
    imp = Decimal(0)
    platit_an = Decimal(0)
    distribuit_an = Decimal(0)
    for fel, dd, s in _transe(miscari, an):
        if fel == "platit":
            platit_an += s
        else:   # [lotul 10, decizia A] impozitul e pe distribuirile anului, nu pe plăți
            distribuit_an += s
            imp += s * Decimal(str(rate_fn(dd)))
    return imp, platit_an, distribuit_an


def structura_la(curenta, istoric):
    """[02.10.2026, pct.4e] Funcția `data -> [(cnp, nume, cota)]`: structura asociaților valabilă la o dată.
    `curenta` = [(nume, cnp, cota)] din `asociati`; `istoric` = [(cnp, nume, cota, valabil_pana_la)] din
    `asociati_istoric`. La data d se ia cea mai VECHE structură arhivată cu valabil_pana_la >= d; dacă nu există, cea
    curentă. Fără istoric -> mereu cea curentă (comportamentul de dinainte, pe firmele fără cesiuni)."""
    pe_data = {}
    for cnp, nume, cota, pana in istoric or ():
        pe_data.setdefault(pana, []).append((str(cnp or ""), nume, Decimal(str(cota))))
    praguri = sorted(pe_data)
    cur = [(str(c or ""), n, Decimal(str(q))) for n, c, q in (curenta or ()) if Decimal(str(q)) > 0]

    def la(d):
        for p in praguri:
            if d <= p:
                return pe_data[p]
        return cur
    return la


def atribuie_pe_asociati(miscari, an, rate_fn, structura):
    """[lot 19 pct.4e] Ca `impozit_ponderat`, dar PE ASOCIAT: fiecare tranșă a anului `an` se împarte după
    structura de la DATA DISTRIBUIRII ei (Legea 31/1990 art.67 alin.(2): „proporțional cu cota de participare”;
    alin.(6): „Dividendele care se cuvin după data transmiterii acțiunilor aparțin cesionarului”), iar distribuirile
    anului după structura de la data lor. `structura(d) -> [(cnp, nume, cota)]` (vezi `structura_la`). Tranșele vin din
    `_transe` (anualele pe 457 și interimarele pe 456 — lotul 10, deficiența 431).
    Întoarce {cnp: {"nume", "platit", "impozit", "distribuit"}} (Decimal, nerotunjite — rotunjirea e a apelantului); „impozit” e pe
    tranșele distribuite (lotul 10, decizia A).
    O structură unică pe tot registrul dă exact `total × cotă` (aceeași cifră ca înainte)."""
    out = {}

    def adauga(cheie, d, suma):
        for cnp, nume, cota in structura(d):
            r = out.setdefault(cnp, {"nume": nume, "platit": Decimal(0), "impozit": Decimal(0), "distribuit": Decimal(0)})
            r[cheie] += suma * cota / Decimal(100)

    for fel, dd, s in _transe(miscari, an):
        adauga(fel, dd, s)
        if fel == "distribuit":   # [lotul 10, decizia A] impozitul pe distribuirile anului
            adauga("impozit", dd, s * Decimal(str(rate_fn(dd))))
    return out
