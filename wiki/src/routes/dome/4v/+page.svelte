<script>
import { browser } from '$app/environment';
import { base } from '$app/paths';
import DomePreview from '$lib/DomePreview.svelte';
import SpecTable from '$lib/SpecTable.svelte';
import StrutBreakdown from '$lib/StrutBreakdown.svelte';
import DownloadSection from '$lib/DownloadSection.svelte';

const strutGroups = [
  { type: 'A', chord_factor: 0.2532, length_ft: 3.80, count: 30, color: [0.906, 0.298, 0.235] },
  { type: 'B', chord_factor: 0.2945, length_ft: 4.42, count: 60, color: [0.204, 0.596, 0.859] },
  { type: 'C', chord_factor: 0.2952, length_ft: 4.43, count: 30, color: [0.180, 0.800, 0.443] },
  { type: 'D', chord_factor: 0.2986, length_ft: 4.48, count: 30, color: [0.953, 0.612, 0.071] },
  { type: 'E', chord_factor: 0.3129, length_ft: 4.69, count: 70, color: [0.608, 0.349, 0.714] },
  { type: 'F', chord_factor: 0.3249, length_ft: 4.87, count: 30, color: [0.102, 0.737, 0.612] },
];

const dimRows = [
  ['Property', 'Value'],
  ['Frequency', '4V'], ['Diameter', '30.00 ft'], ['Radius', '15.00 ft'],
  ['Height', '15.00 ft (perfect hemisphere)'], ['Floor Area', '706.86 sq ft'],
];

const structRows = [
  ['Property', 'Value'],
  ['Total Struts', '250'], ['Strut Types', '6 (A, B, C, D, E, F)'],
  ['Total Vertices', '91'], ['Nodes / Hubs', '91'],
  ['Hubs by valence', '20 × 4-way, 6 × 5-way, 65 × 6-way'],
  ['Assembly Complexity', 'High'], ['Wind Resistance', '60–100 mph'],
];

const hubTypes = [
  { valence: 4, count: 20 }, { valence: 5, count: 6 }, { valence: 6, count: 65 },
];

const costRows = [
  ['Item', 'PVC', '1" EMT', '2" EMT'],
  ['Pipe (434 × 10 ft)', '434 × $8.49 = $3,685', '434 × $19.98 = $8,671', '434 × $42.98 = $18,653'],
  ['Plywood Hubs (24–30 sheets)', '$1,560–1,950', '$1,560–1,950', '$1,560–1,950'],
  ['Bolts & Fasteners', '$1,000–1,875', '$1,500–2,813', '$1,500–2,813'],
  ['Tarps, Anchors, Rope, Misc', '$1,960–3,418', '$1,960–3,418', '$1,960–3,418'],
  ['PVC Primer/Cement', '$33', '—', '—'],
  ['Subtotal', '$8,211–10,939', '$13,664–16,830', '$23,646–26,812'],
  ['Tax (8–10%)', '$657–1,094', '$1,093–1,683', '$1,892–2,681'],
  ['Contingency (10%)', '$821–1,094', '$1,366–1,683', '$2,365–2,681'],
  ['Tools', '$180–260', '$180–260', '$180–260'],
  ['Total Build Cost', '$9,869–13,387', '$16,303–20,456', '$28,083–32,434'],
];

const emtCompare = [
  ['Property', 'PVC 1.5"', '1" EMT', '2" EMT'],
  ['Pipe Cost', '$3,685', '$8,671', '$18,653'],
  ['Total Weight', '2,170 lbs', '4,297 lbs', '9,331 lbs'],
  ['Weight per Stick', '5.0 lbs', '9.9 lbs', '21.5 lbs'],
  ['Wind Rating', '60–100 mph', '80–140 mph', '120+ mph'],
  ['Lifespan', '5+ years', '20–25 years', '25+ years'],
  ['Joining', 'PVC cement', 'Bolts at hubs', 'Bolts at hubs'],
  ['Cutting Tool', 'PVC cutter', 'Angle grinder', 'Angle grinder'],
];
</script>

<svelte:head><title>4V Dome — Geodesic Dome Wiki</title></svelte:head>

<h1>4V Geodesic Dome</h1>
<p class="tag">Six strut types. 250 struts total. Heavy-duty dome for exposed areas and year-round use.</p>

{#if browser}
<DomePreview modelUrl="{base}/models/4v/dome_4v.json" />
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
  <p>The 4V dome is a perfect hemisphere with a flat base. Even-V geometry gives a mathematically flat equator — the dome sits perfectly on level ground.</p>
  <p><strong>PVC Assembly:</strong> 80–120 hours with 4–6 builders. Six strut types require meticulous organization. Color-code each type during cutting.</p>
  <p><strong>EMT Assembly:</strong> 120–180 hours with 5–7 builders. At 2+ tons for 1" EMT, mechanical lifting is recommended. Cutting requires angle grinder with metal wheels.</p>
  <p><strong>Tip:</strong> The Type C and D struts are very close in length (difference ~0.4"). Mark them carefully to avoid mix-ups.</p>
</div>

<DownloadSection freq={4} strutTypes={strutGroups} {hubTypes} />
