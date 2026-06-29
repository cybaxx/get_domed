<script>
  let { strutGroups, radius } = $props();
</script>

<div class="card">
  <h3>Strut Type Breakdown</h3>
  <table>
    <thead>
      <tr>
        <th>Type</th>
        <th>Color</th>
        <th>Chord Factor</th>
        <th>Length (ft)</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      {#each strutGroups as g}
        <tr>
          <td><span class="badge badge-{g.type}">{g.type}</span></td>
          <td><span style="display:inline-block;width:16px;height:16px;border-radius:3px;background:rgb({(g.color||[0.8,0.8,0.8]).map(c=>Math.round(c*255)).join(',')});vertical-align:middle;"></span></td>
          <td class="mono">{g.chord_factor.toFixed(4)}</td>
          <td class="mono heavy">{g.length_ft.toFixed(2)} ft</td>
          <td class="heavy">{g.count}</td>
        </tr>
      {/each}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="4" class="heavy">Total</td>
        <td class="heavy">{strutGroups.reduce((s,g) => s + g.count, 0)}</td>
      </tr>
    </tfoot>
  </table>
</div>
