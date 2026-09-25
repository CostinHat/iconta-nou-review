---
title: "Ce fac dacă am declarat de două ori același venit în D212?"
description: "Venitul dublu declarat în D212 se corectează prin ștergerea/corectarea operațiunii duplicate din registrul de încasări și plăți, apoi o declarație rectificativă; motorul D212 al iConta.eu însumează tot ce e validat în registru, fără să detecteze duplicate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă am declarat de două ori același venit în D212?

Dacă aceeași încasare a ajuns de două ori în calculul venitului brut, cauza cea mai frecventă e o operațiune introdusă de două ori în registrul de încasări și plăți; corecția are doi pași: repari registrul, apoi depui o declarație rectificativă dacă D212 a fost deja transmisă cu venitul dublat.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri [...]"
— Cod fiscal (Legea 227/2015), art. 68 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, venitul brut pentru D212 se stabilește prin însumarea încasărilor din activitate, pe an fiscal. Dacă aceeași sumă a fost înregistrată de două ori (fie ca două operațiuni identice, fie ca o operațiune corectată greșit, prin adăugare în loc de editare), venitul brut rezultă mai mare decât cel real, cu efect direct asupra venitului net, CAS, CASS și impozitului calculat. Corecția reală se face la sursă — în evidența din care se calculează venitul, nu direct în declarație — iar dacă declarația a fost deja depusă cu cifra greșită, se aplică mecanismul general de rectificare de mai sus.

## Ce se greșește în practică

- Se corectează direct cifra din declarație, fără să se corecteze și înregistrarea duplicată din evidență — la următoarea recalculare (sau la un control), suma dublă poate reapărea.
- Se șterge operațiunea duplicată fără să se verifice dacă a fost deja inclusă într-o declarație depusă — dacă da, corectarea evidenței, singură, nu actualizează automat declarația la ANAF; e nevoie și de rectificativă.
- Se presupune că aplicația de contabilitate detectează automat o încasare introdusă de două ori — un motor de calcul pur, care doar însumează operațiunile validate, nu are de unde să știe că două înregistrări reprezintă aceeași încasare reală.

## Ce face iConta.eu

Motorul D212 din iConta.eu (`core/d212_engine.py`, accesat prin funcția `fisa_d212` din `core/rip_api.py`) calculează venitul brut ca sumă a încasărilor cu categoria „activitate", **doar din operațiunile cu status „validată"** din registrul de încasări și plăți — ciornele nevalidate sunt excluse automat și semnalate separat, nu intră în calcul. Dacă însă aceeași încasare a fost introdusă și validată de două ori ca operațiuni distincte, motorul le însumează pe amândouă: **nu există în cod o detecție de duplicate** — validarea unei operațiuni certifică doar corectitudinea ei individuală, nu unicitatea față de restul registrului.

Corectarea reală înseamnă ștergerea sau anularea operațiunii duplicate din registrul de încasări și plăți, urmată de regenerarea fișei D212 — cifra nouă va reflecta corect venitul. Dacă declarația a fost deja depusă la ANAF cu venitul dublat, corectarea registrului în iConta.eu nu retrimite automat nimic la ANAF: e nevoie, separat, de o declarație rectificativă, prin mecanismul general descris mai sus.

[iConta.eu](/)
