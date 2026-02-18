<script lang="ts">
	import ImageInput from '$lib/components/ImageInput.svelte';
	import VoiceInput from '$lib/components/VoiceInput.svelte';
	import TextInput from '$lib/components/TextInput.svelte';
	import ResultsPanel from '$lib/components/ResultsPanel.svelte';
	import ChatFollowup from '$lib/components/ChatFollowup.svelte';
	import ErrorState from '$lib/components/ErrorState.svelte';
	import { appState } from '$lib/stores.svelte';

	function selectMode(mode: 'image' | 'voice' | 'text') {
		appState.activeInputMode = mode;
		appState.errorMessage = null;
	}

	function goBack() {
		appState.resetSession();
	}

	// Input mode cards configuration
	const inputModes = [
		{
			id: 'image' as const,
			title: 'Upload Image',
			description: 'Take or upload a photo of the affected crop',
			icon: 'camera',
			gradient: 'from-emerald-500 to-teal-500',
			shadow: 'shadow-emerald-200'
		},
		{
			id: 'voice' as const,
			title: 'Voice Input',
			description: 'Describe symptoms using your voice',
			icon: 'microphone',
			gradient: 'from-blue-500 to-indigo-500',
			shadow: 'shadow-blue-200'
		},
		{
			id: 'text' as const,
			title: 'Text Description',
			description: 'Type a description of the crop problem',
			icon: 'text',
			gradient: 'from-amber-500 to-orange-500',
			shadow: 'shadow-amber-200'
		}
	];
</script>

<svelte:head>
	<title>Analyze — KrishiRakshak</title>
</svelte:head>

<div class="mx-auto max-w-3xl">
	{#if appState.analysisResult}
		<!-- Results View -->
		<ResultsPanel onback={goBack} />
		<div class="mt-6">
			<ChatFollowup />
		</div>
	{:else}
		<!-- Hero Section -->
		<div class="animate-fade-in mb-10 text-center">
			<div
				class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-200"
			>
				<svg
					class="h-8 w-8 text-white"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z M17.5 2.5c0 0-1.5 3-1.5 6s1.5 6 1.5 6 M14 6c0 0 2 1 3.5 1s3.5-1 3.5-1"
					/>
				</svg>
			</div>
			<h1 class="mb-2 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl">
				Crop Disease <span
					class="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent"
					>Analysis</span
				>
			</h1>
			<p class="mx-auto max-w-lg text-base leading-relaxed text-neutral-500">
				Upload a crop image, record your voice, or type a description — our AI will identify the
				disease and provide expert treatment guidance.
			</p>
		</div>

		<!-- Error display -->
		{#if appState.errorMessage}
			<div class="mb-6">
				<ErrorState
					message={appState.errorMessage}
					type="error"
					onretry={() => {
						appState.errorMessage = null;
					}}
				/>
			</div>
		{/if}

		{#if !appState.activeInputMode}
			<!-- Input Mode Selection Cards -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
				{#each inputModes as mode, i}
					<button
						onclick={() => selectMode(mode.id)}
						class="group relative overflow-hidden rounded-2xl bg-white p-6 text-left shadow-lg ring-1 ring-neutral-100 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl active:scale-[0.98]"
						style="animation: slideUp 0.4s ease-out {i * 100}ms both;"
					>
						<!-- Gradient accent bar -->
						<div
							class="absolute top-0 left-0 h-1 w-full bg-gradient-to-r {mode.gradient} opacity-0 transition-opacity group-hover:opacity-100"
						></div>

						<div
							class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br {mode.gradient} {mode.shadow} shadow-md transition-transform group-hover:scale-110"
						>
							{#if mode.icon === 'camera'}
								<svg
									class="h-6 w-6 text-white"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="1.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"
									/>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z"
									/>
								</svg>
							{:else if mode.icon === 'microphone'}
								<svg
									class="h-6 w-6 text-white"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="1.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"
									/>
								</svg>
							{:else}
								<svg
									class="h-6 w-6 text-white"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="1.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.573 48.573 0 0 0 5.886-.363c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
									/>
								</svg>
							{/if}
						</div>

						<h3 class="mb-1 text-base font-semibold text-neutral-800">{mode.title}</h3>
						<p class="text-sm leading-relaxed text-neutral-500">{mode.description}</p>

						<!-- Arrow indicator -->
						<div
							class="absolute right-4 bottom-5 -translate-x-2 opacity-0 transition-all group-hover:translate-x-0 group-hover:opacity-100"
						>
							<svg
								class="h-5 w-5 text-neutral-400"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
								/>
							</svg>
						</div>
					</button>
				{/each}
			</div>

			<!-- Features row -->
			<div class="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-4">
				{#each [{ icon: '🤖', label: 'AI-Powered Analysis' }, { icon: '🌿', label: '15+ Crop Diseases' }, { icon: '💊', label: 'Treatment Guidance' }, { icon: '🔄', label: 'Follow-up Chat' }] as feature}
					<div
						class="flex items-center gap-2.5 rounded-xl bg-white/70 px-3.5 py-2.5 text-sm text-neutral-600 ring-1 ring-neutral-100 backdrop-blur-sm"
					>
						<span class="text-lg">{feature.icon}</span>
						<span class="text-xs font-medium">{feature.label}</span>
					</div>
				{/each}
			</div>
		{:else}
			<!-- Active Input Mode -->
			<div class="mb-5">
				<button
					onclick={() => {
						appState.activeInputMode = null;
						appState.errorMessage = null;
					}}
					class="flex items-center gap-2 text-sm font-medium text-neutral-500 transition-colors hover:text-emerald-600"
				>
					<svg
						class="h-4 w-4"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="2"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
					</svg>
					Back to input options
				</button>
			</div>

			{#if appState.activeInputMode === 'image'}
				<ImageInput />
			{:else if appState.activeInputMode === 'voice'}
				<VoiceInput />
			{:else if appState.activeInputMode === 'text'}
				<TextInput />
			{/if}
		{/if}
	{/if}
</div>
