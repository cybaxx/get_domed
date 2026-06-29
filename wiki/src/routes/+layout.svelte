<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import '../app.css';
  let { children } = $props();
  let dark = $state(false);
  let menuOpen = $state(false);

  onMount(() => {
    dark = localStorage.getItem('theme') === 'dark';
    applyTheme();
  });

  function toggleTheme() {
    dark = !dark;
    localStorage.setItem('theme', dark ? 'dark' : 'light');
    applyTheme();
  }

  function applyTheme() {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : '');
  }

  function closeMenu() { menuOpen = false; }

  const nav = [
    { label: 'Overview', links: [
      { href: base + '/', text: 'Home' },
      { href: base + '/dome/2v', text: '2V Dome' },
      { href: base + '/dome/3v', text: '3V Dome' },
      { href: base + '/dome/4v', text: '4V Dome' },
    ]},
    { label: 'Reference', links: [
      { href: base + '/math', text: 'Geodesic Math' },
      { href: base + '/build', text: 'Construction Guide' },
      { href: base + '/downloads', text: 'Downloads' },
    ]},
  ];
</script>

<button class="menu-toggle" onclick={() => menuOpen = !menuOpen}>
  {menuOpen ? '✕' : '☰'}
</button>

{#if menuOpen}
  <div class="sidebar-overlay visible" onclick={closeMenu}></div>
{/if}

<div class="layout">
  <nav class="sidebar" class:open={menuOpen}>
    <a href={base + '/'} class="brand">Geodesic Domes</a>
    <p class="tag" style="padding:0 0.75rem;margin-bottom:1rem;">Berkeley Math Circle · 30 ft</p>
    <button class="theme-toggle" onclick={toggleTheme}>
      {dark ? '☀️ Light' : '🌙 Dark'}
    </button>
    {#each nav as section}
      <h2>{section.label}</h2>
      {#each section.links as link}
        <a href={link.href} onclick={closeMenu}>{link.text}</a>
      {/each}
    {/each}
  </nav>
  <main class="content">
    {@render children()}
  </main>
</div>
