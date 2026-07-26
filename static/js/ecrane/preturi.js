// preturi.js — SURSA UNICA a continutului de preturi. Refolosit in modalul Functionalitati
// (cardul Preturi) si, ulterior, in fluxul de inregistrare. NU duplica textul altundeva.
// Text verbatim aprobat 26.07.2026. Treptele sunt PROGRESIVE: 30 firme = 20*10 + 10*8 = 280.

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
    <p class="preturi-nota">Prețurile sunt finale. Nu se adaugă TVA.</p>
    <h3>Ce primești</h3>
    <p>Tot. Contabilitate, salarizare, toate declarațiile fiscale, e-Factura, e-Transport, gestiunea stocurilor, controlul fiscal automat. Nu plătești separat pentru nimic și nu există funcție blocată la un preț mai mare.</p>
    <h3>Documente fotografiate</h3>
    <p>Clienții tăi pot fotografia bonuri fiscale și chitanțe direct din portalul lor, iar iConta.eu le citește singură și pregătește înregistrarea contabilă, pe care o confirmi tu.</p>
    <p>Sunt incluse 30 de astfel de documente pe lună, pentru fiecare firmă. Peste această limită, fiecare document în plus costă 0,20 lei.</p>
    <h3>Plata</h3>
    <p>Lunar, prin transfer bancar. Dacă plătești anul întreg în avans, primești 15% reducere.</p>
    <h3>Prețul tău nu se schimbă</h3>
    <p>Tariful de la data înscrierii rămâne același timp de 12 luni, chiar dacă prețurile publice cresc între timp. Primele 20 de cabinete care se înscriu îl păstrează 24 de luni.</p>
  `;
}
