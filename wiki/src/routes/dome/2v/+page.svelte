<script>
import { browser } from '$app/environment';
import { base } from '$app/paths';
import DomePreview from '$lib/DomePreview.svelte';
import SpecTable from '$lib/SpecTable.svelte';
import StrutBreakdown from '$lib/StrutBreakdown.svelte';
import DownloadSection from '$lib/DownloadSection.svelte';

const strutGroups = [
  { type: 'A', chord_factor: 0.5465, length_ft: 8.20, count: 30, color: [0.906, 0.298, 0.235] },
  { type: 'B', chord_factor: 0.6180, length_ft: 9.27, count: 35, color: [0.204, 0.596, 0.859] },
];

const dimRows = [
  ['Property', 'Value'],
  ['Frequency', '2V'],
  ['Diameter', '30.00 ft'],
  ['Radius', '15.00 ft'],
  ['Height', '15.00 ft (hemisphere)'],
  ['Floor Area', '706.86 sq ft'],
  ['Surface Area', '1,413.72 sq ft'],
  ['Volume', '7,068.59 cu ft'],
];

const structRows = [
  ['Property', 'Value'],
  ['Total Struts', '65'],
  ['Strut Types', '2 (A, B)'],
  ['Total Vertices', '26'],
  ['Nodes / Hubs', '26'],
  ['Hubs by valence', '10 × 4-way, 10 × 6-way, 6 × 5-way'],
  ['Assembly Complexity', 'Low'],
  ['Wind Resistance', '20–40 mph'],
];

const hubTypes = [
  { valence: 4, count: 10 },
  { valence: 5, count: 6 },
  { valence: 6, count: 10 },
];

const costRows = [
  ['Item', 'PVC', '1" EMT', '2" EMT'],
  ['Pipe (216 × 10 ft)', '216 × $8.49 = $1,834', '216 × $19.98 = $4,316', '216 × $42.98 = $9,284'],
  ['Plywood Hubs (12 sheets)', '12 × $65 = $780', '12 × $65 = $780', '12 × $65 = $780'],
  ['Bolts & Fasteners', '$600–900', '$900–1,350', '$900–1,350'],
  ['Tarps, Anchors, Rope, Misc', '$1,960–3,418', '$1,960–3,418', '$1,960–3,418'],
  ['PVC Primer/Cement', '$22', '—', '—'],
  ['Subtotal', '$5,169–6,932', '$7,929–9,842', '$12,897–14,810'],
  ['Tax (9%) + Contingency (10%)', '+$982–1,317', '+$1,507–1,870', '+$2,450–2,814'],
  ['Tools', '$180–260', '$180–260', '$180–260'],
  ['Total Build Cost', '$6,279–8,578', '$9,616–11,972', '$15,527–17,884'],
];

const emtCompare = [
  ['Property', 'PVC 1.5"', '1" EMT', '2" EMT'],
  ['Pipe Cost', '$1,834', '$4,316', '$9,284'],
  ['Total Weight', '1,080 lbs', '2,138 lbs', '4,644 lbs'],
  ['Weight per Stick', '5.0 lbs', '9.9 lbs', '21.5 lbs'],
  ['Wind Rating', '20–40 mph', '50–100 mph', '80–130 mph'],
  ['Lifespan', '2–3 years', '15–20 years', '20–25 years'],
  ['Joining', 'PVC cement', 'Bolts at hubs', 'Bolts at hubs'],
  ['Cutting Tool', 'PVC cutter', 'Angle grinder', 'Angle grinder'],
];

let title = $state('2V Dome — Geodesic Dome Wiki');
</script>

<svelte:head>
  <title>{title}</title>
</svelte:head>

<h1>2V Geodesic Dome</h1>
<p class="tag">The simplest geodesic dome. Two strut types. 65 struts total. Best for budget camping in low-wind conditions.</p>

{#if browser}
<DomePreview modelUrl="{base}/models/2v/dome_2v.json" />
{:else}
<div class="preview-container" style="display:flex;align-items:center;justify-content:center;background:#0f172a;border-radius:var(--radius);height:500px;margin-bottom:1.5rem;">
  <span style="color:#94a3b8;font-family:var(--font);">3D preview loading...</span>
</div>
{/if}

<h2>Dimensions</h2>
<SpecTable rows={dimRows} />

<h2>Structure</h2>
<SpecTable rows={structRows} />

<StrutBreakdown {strutGroups} radius={15} />

<h2>Materials & Cost (Home Depot 2026)</h2>
<SpecTable rows={costRows} />

<h2>PVC vs EMT Conduit</h2>
<SpecTable rows={emtCompare} />

<h2>Construction</h2>
<div class="card">
  <p>The 2V dome is the easiest to build. All struts fall into only two lengths (Type A: 8.20 ft, Type B: 9.27 ft).</p>
  <p><strong>PVC Assembly:</strong> 40–60 hours with 2–3 builders. Use PVC cement for connections or mechanical bolts through flattened ends. Standard 10-ft PVC sticks yield one strut each — buy 216 sticks total.</p>
  <p><strong>EMT Assembly:</strong> 60–90 hours with 3–4 builders. Flatten ends with arbor press, drill bolt holes. Heavier — use 3/4" plywood hubs and deeper footings.</p>
  <p><strong>Base:</strong> The dome sits perfectly flat on level ground. Anchor with rebar and guy-lines in wind-prone areas.</p>
</div>

<DownloadSection freq={2} strutTypes={strutGroups} {hubTypes} />
