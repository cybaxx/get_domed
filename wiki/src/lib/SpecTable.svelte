<script>
  let { rows } = $props();
</script>

<div class="card">
  <table>
    <thead>
      <tr>
        {#each rows[0] as cell}
          <th>{cell}</th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each rows.slice(1) as row}
        <tr>
          {#each row as cell}
            <td>{@html String(cell)}</td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
