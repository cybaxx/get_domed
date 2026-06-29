<script>
  import { onMount } from 'svelte';
  import '../app.css';
  let { children } = $props();
  let dark = $state(false);

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

  const nav = [
    { label: 'Overview', links: [
      { href: '/', text: 'Home' },
      { href: '/dome/2v', text: '2V Dome' },
      { href: '/dome/3v', text: '3V Dome' },
      { href: '/dome/4v', text: '4V Dome' },
    ]},
    { label: 'Reference', links: [
      { href: '/math', text: 'Geodesic Math' },
      { href: '/build', text: 'Construction Guide' },
      { href: '/downloads', text: 'Downloads' },
    ]},
  ];
</script>

<div class="layout">
  <nav class="sidebar">
    <a href="/" class="brand">Geodesic Domes</a>
    <p class="tag" style="padding:0 0.75rem;margin-bottom:1rem;">Berkeley Math Circle · 30 ft</p>
    <button class="theme-toggle" onclick={toggleTheme}>
      {dark ? '☀️ Light' : '🌙 Dark'}
    </button>
    {#each nav as section}
      <h2>{section.label}</h2>
      {#each section.links as link}
        <a href={link.href}>{link.text}</a>
      {/each}
    {/each}
  </nav>
  <main class="content">
    {@render children()}
  </main>
</div>
