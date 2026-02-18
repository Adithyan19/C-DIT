<svelte:head>
	<title>KrishiRakshak — Crop Disease Advisor</title>
</svelte:head>

<div class="mx-auto max-w-4xl">
	<!-- Hero Section -->
	<div class="animate-fade-in mb-12 text-center">
		<div
			class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-xl shadow-emerald-200"
		>
			<svg
				class="h-10 w-10 text-white"
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
		<h1 class="mb-3 text-4xl font-bold tracking-tight text-neutral-900 sm:text-5xl">
			Protect Your <span
				class="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent"
				>Crops</span
			> with AI
		</h1>
		<p class="mx-auto max-w-2xl text-lg leading-relaxed text-neutral-500">
			Upload a photo, record your voice, or describe symptoms — KrishiRakshak identifies crop
			diseases instantly and provides expert treatment guidance tailored for farmers.
		</p>
		<div class="mt-8 flex flex-wrap items-center justify-center gap-4">
			<a
				href="/analyze"
				class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-emerald-200 transition-all hover:-translate-y-0.5 hover:shadow-xl active:scale-[0.98]"
			>
				Start Analysis
				<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
					/>
				</svg>
			</a>
			<a
				href="/about"
				class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-base font-semibold text-neutral-700 shadow-sm ring-1 ring-neutral-200 transition-all hover:-translate-y-0.5 hover:shadow-md active:scale-[0.98]"
			>
				Learn More
			</a>
		</div>
	</div>

	<!-- Feature Cards -->
	<div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
		{#each [{ icon: '📷', title: 'Image Analysis', description: 'Upload a photo of your affected crop and get instant disease identification powered by AI classification.', color: 'emerald' }, { icon: '🎙️', title: 'Voice Input', description: 'Describe your crop symptoms by speaking — our speech-to-text engine handles the rest.', color: 'blue' }, { icon: '📝', title: 'Text Description', description: 'Type a detailed description of the issue and receive a thorough analysis with treatment advice.', color: 'amber' }] as feature, i}
			<div
				class="group rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-100 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
				style="animation: slideUp 0.4s ease-out {i * 100 + 200}ms both;"
			>
				<span class="mb-4 block text-3xl">{feature.icon}</span>
				<h3 class="mb-2 text-lg font-semibold text-neutral-800">{feature.title}</h3>
				<p class="text-sm leading-relaxed text-neutral-500">{feature.description}</p>
			</div>
		{/each}
	</div>

	<!-- Stats Row -->
	<div class="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-4">
		{#each [{ value: '15+', label: 'Crop Diseases' }, { value: 'AI', label: 'Powered Analysis' }, { value: '3', label: 'Input Methods' }, { value: '24/7', label: 'Available' }] as stat, i}
			<div
				class="rounded-xl bg-white p-4 text-center shadow-sm ring-1 ring-neutral-100"
				style="animation: slideUp 0.3s ease-out {i * 80 + 500}ms both;"
			>
				<p
					class="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-2xl font-bold text-transparent"
				>
					{stat.value}
				</p>
				<p class="text-xs font-medium text-neutral-500">{stat.label}</p>
			</div>
		{/each}
	</div>
</div>
