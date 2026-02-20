<script>
	import "../app.css";
	import Navbar from "$lib/components/Navbar.svelte";
	import { user } from "$lib/stores.js";
	import { page } from "$app/state";

	let { children } = $props();

	const publicPaths = ["/login", "/signup"];
	let currentUser;
	user.subscribe((v) => (currentUser = v));

	$effect(() => {
		if (typeof window !== "undefined") {
			const path = page.url?.pathname;
			if (!currentUser && !publicPaths.includes(path)) {
				window.location.href = "/login";
			}
		}
	});
</script>

{#if page.url?.pathname === "/login" || page.url?.pathname === "/signup"}
	{@render children()}
{:else}
	<Navbar />
	{@render children()}
{/if}
