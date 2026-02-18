<script lang="ts">
	import { onMount } from 'svelte';

	interface Session {
		id: string;
		input_type: string;
		created_at: string;
	}

	let sessions = $state<Session[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const API_BASE = 'http://localhost:3001';

	onMount(async () => {
		try {
			const res = await fetch(`${API_BASE}/sessions`);
			const json = await res.json();
			if (json.success) {
				sessions = json.data || [];
			} else {
				error = 'Failed to load session history.';
			}
		} catch {
			error = 'Could not connect to the server.';
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-IN', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function getInputIcon(type: string) {
		if (type === 'image') return '📷';
		if (type === 'voice') return '🎙️';
		return '📝';
	}
</script>

<svelte:head>
	<title>History — KrishiRakshak</title>
</svelte:head>

<div class="mx-auto max-w-3xl">
	<div class="mb-8 text-center">
		<h1 class="mb-2 text-3xl font-bold tracking-tight text-neutral-900">
			Session <span
				class="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent"
				>History</span
			>
		</h1>
		<p class="text-base text-neutral-500">View your past analysis sessions and results.</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-16">
			<div
				class="h-8 w-8 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600"
			></div>
		</div>
	{:else if error}
		<div class="rounded-xl bg-red-50 p-6 text-center text-red-700 ring-1 ring-red-100">
			<p class="font-medium">{error}</p>
			<p class="mt-1 text-sm text-red-500">Make sure the backend server is running.</p>
		</div>
	{:else if sessions.length === 0}
		<div class="rounded-xl bg-neutral-50 p-12 text-center ring-1 ring-neutral-100">
			<div
				class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-neutral-100"
			>
				<svg
					class="h-7 w-7 text-neutral-400"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
					/>
				</svg>
			</div>
			<h3 class="text-lg font-semibold text-neutral-700">No sessions yet</h3>
			<p class="mt-1 text-sm text-neutral-500">
				Start by <a href="/analyze" class="font-medium text-emerald-600 hover:text-emerald-700"
					>analyzing a crop</a
				> to see your history here.
			</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each sessions as session, i}
				<div
					class="group rounded-xl bg-white p-5 shadow-sm ring-1 ring-neutral-100 transition-all hover:shadow-md"
					style="animation: slideUp 0.3s ease-out {i * 50}ms both;"
				>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-3">
							<span class="text-2xl">{getInputIcon(session.input_type)}</span>
							<div>
								<p class="font-medium text-neutral-800 capitalize">{session.input_type} Analysis</p>
								<p class="font-mono text-xs text-neutral-400">{session.id.slice(0, 8)}…</p>
							</div>
						</div>
						<span class="text-sm text-neutral-500">{formatDate(session.created_at)}</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
