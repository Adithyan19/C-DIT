<script lang="ts">
  import './layout.css';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';

  let { children } = $props();
</script>

<svelte:head>
  <title>KrishiRakshak — Crop Disease Advisor</title>
</svelte:head>

<div class="flex min-h-screen flex-col">
  <Header />
  <main class="mx-auto mt-[72px] w-full max-w-[1200px] flex-1 px-4 py-8 sm:px-6">
    {@render children()}
  </main>
  <Footer />
</div>
