// preturi.js — SURSA UNICA a continutului de preturi. Refolosit in modalul Functionalitati
// (cardul Preturi) si, ulterior, in fluxul de inregistrare. NU duplica textul altundeva.
// Text verbatim aprobat 26.07.2026; sectiunile de facturare adaugate 29.07.2026, PRELUATE
// LITERAL din TERMENI_SI_CONDITII.md sectiunile 11.4-11.10 si 17. NU reformula aici: doua
// texte publice care spun acelasi lucru altfel devin, in timp, doua promisiuni diferite. Treptele sunt PROGRESIVE: 30 firme = 20*10 + 10*8 = 280.

export const PRETURI_TITLU = "Prețuri";
export const PRETURI_SUBTITLU = "10 lei pe firmă pe lună";

export function preturiHTML() {
  return `
    <p>Plătești pentru fiecare firmă pe care o ai în evidență. Cu cât ai mai multe firme, cu atât fiecare firmă nouă costă mai puțin.</p>
    <ul>
      <li>Primele 20 de firme: 10 lei pe lună fiecare</li>
      <li>Următoarele 30 (de la 21 la 50): 8 lei pe lună fiecare</li>
      <li>Peste 50 de firme: 6 lei pe lună fiecare</li>
    </ul>
    <p class="preturi-eticheta">Exemple:</p>
    <ul>
      <li>10 firme — 100 lei pe lună</li>
      <li>30 firme — 280 lei pe lună</li>
      <li>50 firme — 440 lei pe lună</li>
      <li>100 firme — 740 lei pe lună</li>
    </ul>
    <p class="preturi-nota"><strong>Prețurile sunt finale. Nu se adaugă TVA peste ele.</strong> Dacă la un moment dat devenim plătitori de TVA, taxa va fi inclusă în prețul publicat, nu adăugată. Prețul pe care îl vezi este prețul pe care îl plătești.</p>
    <h3>Ce primești</h3>
    <p>Tot. Contabilitate, salarizare, toate declarațiile fiscale, e-Factura, e-Transport, gestiunea stocurilor, controlul fiscal automat. Nu plătești separat pentru nimic și nu există funcție blocată la un preț mai mare.</p>
    <h3>Documente fotografiate</h3>
    <p>Clienții tăi pot fotografia bonuri fiscale și chitanțe direct din portalul lor, iar iConta.eu le citește singură și pregătește înregistrarea contabilă, pe care o confirmi tu.</p>
    <p>Sunt incluse 30 de astfel de documente pe lună, pentru fiecare firmă. Peste această limită, fiecare document în plus costă 0,20 lei.</p>
    <h3>Când începe plata</h3>
    <p><strong>Abonamentul nu se facturează pentru perioada dintre înscriere și prima zi de 1 care urmează.</strong></p>
    <p>Exemplu: te înscrii pe <strong>5 iulie</strong> cu 10 firme. Pentru intervalul 5&ndash;31 iulie nu plătești abonament. Prima factură se emite pe <strong>1 august</strong> și cuprinde abonamentul pentru <strong>august</strong> (100 lei).</p>
    <p>În perioada dintre înscriere și primul 1 se aplică aceleași limite de utilizare ca într-o lună obișnuită. Dacă depășești limita de documente fotografiate, depășirea se tarifează normal și apare pe prima factură. Nu plătești abonament, dar plătești consumul care ne costă efectiv.</p>
    <p><strong>Simetric, pentru firmele adăugate pe parcurs:</strong> o firmă administrată adăugată în cursul unei luni intră la facturarea abonamentului de la următoarea zi de 1, nu de la data adăugării.</p>
    <p>Exemplu: ai 10 firme pe 1 august (facturate 100 lei) și adaugi încă 5 pe 20 august. Pentru cele 5 nu plătești nimic în august. Pe 1 septembrie factura va fi pentru 15 firme (150 lei).</p>
    <h3>Plata</h3>
    <p><strong>Emitem o singură factură pe lună, în prima zi a lunii.</strong> Ea cuprinde două elemente:</p>
    <ul>
      <li><strong>abonamentul pentru luna care urmează</strong> &mdash; facturare în avans, calculată după numărul de firme administrate activ la data emiterii facturii;</li>
      <li><strong>utilizarea peste limită din luna încheiată</strong> &mdash; facturare în urmă, dacă a existat. Aceasta nu poate fi cunoscută dinainte, de aceea apare cu o lună decalaj.</li>
    </ul>
    <p>Plata se face prin transfer bancar, în contul indicat pe factură.</p>
    <p><strong>Plata anuală în avans.</strong> Poți plăti abonamentul pentru 12 luni în avans, cu o reducere de 15%. Dacă adaugi firme în cursul anului plătit, diferența se facturează lunar, la tariful standard, fără reducere. Dacă încetezi contractul înainte de expirarea celor 12 luni, îți returnăm contravaloarea lunilor neîncepute, recalculată la tariful lunar standard, în termen de 30 de zile.</p>
    <h3>Fără angajament</h3>
    <p>Contractul se încheie pe <strong>durată nedeterminată</strong>, cu ciclu lunar. Se reînnoiește tacit la fiecare început de lună, până când una dintre părți îl încetează. <strong>Nu există angajament minim și nu se percepe penalitate de încetare.</strong></p>
    <p>Poți înceta utilizarea oricând, cu efect de la sfârșitul lunii pentru care s-a facturat. Exportul datelor rămâne disponibil în aplicație, fără intervenția noastră.</p>
    <h3>Prețul tău nu se schimbă</h3>
    <p>Tariful de la data înscrierii rămâne același timp de 12 luni, chiar dacă prețurile publice cresc între timp. Primele 20 de cabinete care se înscriu îl păstrează 24 de luni.</p>
    <p><strong>Indexarea anuală.</strong> Tarifele publicate se ajustează automat la data de 1 ianuarie a fiecărui an cu rata inflației aferentă anului precedent, potrivit indicelui prețurilor de consum comunicat oficial de Institutul Național de Statistică. Exemplu: dacă inflația anului 2026 este de 5%, tariful de 10 lei devine 10,50 lei de la 1 ianuarie 2027.</p>
    <p><strong>Modificarea tarifelor.</strong> În afara indexării anuale, putem modifica tarifele publicate. Modificarea se comunică cu cel puțin 30 de zile înainte de intrarea în vigoare, nu afectează cabinetele aflate în perioada de stabilitate, iar cabinetul poate înceta contractul fără penalitate până la acea dată.</p>
  `;
}
