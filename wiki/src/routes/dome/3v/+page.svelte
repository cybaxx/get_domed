<script>
import { browser } from '$app/environment';
import { base } from '$app/paths';
import DomePreview from '$lib/DomePreview.svelte';
import SpecTable from '$lib/SpecTable.svelte';
import StrutBreakdown from '$lib/StrutBreakdown.svelte';
import DownloadSection from '$lib/DownloadSection.svelte';

const strutGroups = [
  { type: 'A', chord_factor: 0.3486, length_ft: 5.23, count: 30, color: [0.906, 0.298, 0.235] },
  { type: 'B', chord_factor: 0.4035, length_ft: 6.05, count: 40, color: [0.204, 0.596, 0.859] },
  { type: 'C', chord_factor: 0.4124, length_ft: 6.19, count: 50, color: [0.180, 0.800, 0.443] },
];

const dimRows = [
  ['Property', 'Value'],
  ['Frequency', '3V'], ['Diameter', '30.00 ft'], ['Radius', '15.00 ft'],
  ['Height', '~15.2 ft (slightly larger than hemisphere)'], ['Floor Area', '~707 sq ft'],
];

const structRows = [
  ['Property', 'Value'],
  ['Total Struts', '120'], ['Strut Types', '3 (A, B, C)'],
  ['Total Vertices', '46'], ['Nodes / Hubs', '46'],
  ['Hubs by valence', '15 × 4-way, 6 × 5-way, 25 × 6-way'],
  ['Assembly Complexity', 'Medium'], ['Wind Resistance', '40–60 mph'],
];

const hubTypes = [
  { valence: 4, count: 15 }, { valence: 5, count: 6 }, { valence: 6, count: 25 },
];

const costRows = [
  ['Item', 'PVC', '1" EMT', '2" EMT'],
  ['Pipe (324 × 10 ft)', '324 × $8.49 = $2,751', '324 × $19.98 = $6,474', '324 × $42.98 = $13,926'],
  ['Plywood Hubs (18 sheets)', '18 × $65 = $1,170', '18 × $65 = $1,170', '18 × $65 = $1,170'],
  ['Bolts & Fasteners', '$900–1,350', '$1,350–2,025', '$1,350–2,025'],
  ['Tarps, Anchors, Rope, Misc', '$1,960–3,418', '$1,960–3,418', '$1,960–3,418'],
  ['PVC Primer/Cement', '$22–33', '—', '—'],
  ['Subtotal', '$6,781–8,694', '$10,927–13,065', '$18,379–20,517'],
  ['Tax (9%) + Contingency (10%)', '+$1,288–1,652', '+$2,076–2,482', '+$3,492–3,898'],
  ['Tools', '$180–260', '$180–260', '$180–260'],
  ['Total Build Cost', '$8,201–10,726', '$13,183–15,807', '$22,051–24,675'],
];

const emtCompare = [
  ['Property', 'PVC 1.5"', '1" EMT', '2" EMT'],
  ['Pipe Cost', '$2,751', '$6,474', '$13,926'],
  ['Total Weight', '1,620 lbs', '3,208 lbs', '6,966 lbs'],
  ['Weight per Stick', '5.0 lbs', '9.9 lbs', '21.5 lbs'],
  ['Wind Rating', '40–60 mph', '60–120 mph', '100–150 mph'],
  ['Lifespan', '3–5 years', '15–20 years', '20–25 years'],
  ['Joining', 'PVC cement', 'Bolts at hubs', 'Bolts at hubs'],
  ['Cutting Tool', 'PVC cutter', 'Angle grinder', 'Angle grinder'],
];
</script>

<svelte:head><title>3V Dome — Geodesic Dome Wiki</title></svelte:head>

<h1>3V Geodesic Dome</h1>
<p class="tag">Three strut types. 120 struts total. Good for moderate wind zones and semi-permanent camping.</p>

{#if browser}
<DomePreview modelUrl="{base}/models/3v/dome_3v.json" />
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
  <p>The 3V dome has no natural equator — it's slightly larger than a pure hemisphere. The base sits nearly flat (within ~1 inch on a 30 ft diameter).</p>
  <p><strong>PVC Assembly:</strong> 60–80 hours with 3–4 builders. Three strut lengths mean careful sorting and labeling is essential.</p>
  <p><strong>EMT Assembly:</strong> 90–130 hours with 4–5 builders. Weight demands mechanical assistance for upper rings. Use angle grinder for cutting.</p>
  <p><strong>Hubs:</strong> 5-way hubs appear only at the 6 original icosahedron vertices. Most interior vertices are 6-way. Base ring has 4-way hubs.</p>
</div>

<DownloadSection freq={3} strutTypes={strutGroups} {hubTypes} />
