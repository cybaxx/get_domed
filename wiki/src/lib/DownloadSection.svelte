<script>
  import { base } from '$app/paths';
  let { freq, strutTypes, hubTypes } = $props();
</script>

<div class="card">
  <h3>Download CAD Files for Fusion 360</h3>
  <p class="tag">All files generated from Berkeley geodesic math. Import STL/OBJ into Fusion 360 as mesh bodies. Use DXF for 2D CAM / laser cutting hub plates.</p>
  <div class="download-grid">
    <div class="download-card">
      <div class="icon">🏗️</div>
      <div class="label">Full Assembly</div>
      <div class="name">Complete {freq}V Dome</div>
      <a href="{base}/models/{freq}v/dome_{freq}v_full.stl" download>STL ⬇</a>
      <a href="{base}/models/{freq}v/dome_{freq}v_full.obj" download style="margin-left:4px;">OBJ ⬇</a>
    </div>
    {#each strutTypes as st}
      <div class="download-card">
        <div class="icon">🔩</div>
        <div class="label">Strut Type</div>
        <div class="name"><span class="badge badge-{st.type}">{st.type}</span> ({st.count}×)</div>
        <a href="{base}/models/{freq}v/dome_{freq}v_strut_{st.type}.stl" download>STL ⬇</a>
      </div>
    {/each}
    {#each hubTypes as h}
      <div class="download-card">
        <div class="icon">🔵</div>
        <div class="label">Hub Template</div>
        <div class="name">{h.valence}-way ({h.count}×)</div>
        <a href="{base}/models/{freq}v/hub_{h.valence}way.dxf" download>DXF ⬇</a>
      </div>
    {/each}
    <div class="download-card">
      <div class="icon">📋</div>
      <div class="label">Bill of Materials</div>
      <div class="name">PVC BOM</div>
      <a href="{base}/models/{freq}v/bom_{freq}v_PVC.csv" download>CSV ⬇</a>
    </div>
    <div class="download-card">
      <div class="icon">📋</div>
      <div class="label">Bill of Materials</div>
      <div class="name">1" EMT BOM</div>
      <a href="{base}/models/{freq}v/bom_{freq}v_1in_EMT.csv" download>CSV ⬇</a>
    </div>
    <div class="download-card">
      <div class="icon">📋</div>
      <div class="label">Bill of Materials</div>
      <div class="name">2" EMT BOM</div>
      <a href="{base}/models/{freq}v/bom_{freq}v_2in_EMT.csv" download>CSV ⬇</a>
    </div>
    <div class="download-card">
      <div class="icon">📦</div>
      <div class="label">All Files</div>
      <div class="name">Complete Bundle</div>
      <a href="{base}/models/{freq}v/dome_{freq}v_all.zip" download>ZIP ⬇</a>
    </div>
  </div>
</div>
