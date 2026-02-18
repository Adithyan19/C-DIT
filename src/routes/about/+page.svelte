<svelte:head>
	<title>About — KrishiRakshak</title>
</svelte:head>

<div class="mx-auto max-w-3xl">
	<!-- Hero -->
	<div class="mb-10 text-center">
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
			About <span
				class="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent"
				>KrishiRakshak</span
			>
		</h1>
		<p class="mx-auto max-w-lg text-base leading-relaxed text-neutral-500">
			AI-Powered Crop Disease Advisory System
		</p>
	</div>

	<!-- Content Cards -->
	<div class="space-y-5">
		<!-- What it does -->
		<div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-100">
			<h2 class="mb-3 text-lg font-semibold text-neutral-800">🌾 What is KrishiRakshak?</h2>
			<p class="text-sm leading-relaxed text-neutral-600">
				KrishiRakshak is an AI-powered agricultural advisory system designed to help farmers
				identify crop diseases quickly and receive expert-level treatment guidance. Simply upload a
				photo of your affected crop, record a voice description, or type your observations — our
				system will analyze the symptoms and provide actionable recommendations.
			</p>
		</div>

		<!-- How it works -->
		<div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-100">
			<h2 class="mb-3 text-lg font-semibold text-neutral-800">🤖 How It Works</h2>
			<div class="space-y-3">
				{#each [{ step: '1', title: 'Submit Your Input', desc: 'Upload an image, record voice, or type a description of your crop problem.' }, { step: '2', title: 'AI Analysis', desc: 'Our system uses image classification, NLP, and a knowledge base of 15+ crop diseases.' }, { step: '3', title: 'Get Advisory', desc: 'Receive a detailed diagnosis with treatment recommendations and prevention measures.' }, { step: '4', title: 'Follow-Up Chat', desc: 'Ask follow-up questions about dosage, organic alternatives, or disease spread.' }] as item}
					<div class="flex items-start gap-3">
						<span
							class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-xs font-bold text-emerald-700"
						>
							{item.step}
						</span>
						<div>
							<p class="text-sm font-medium text-neutral-700">{item.title}</p>
							<p class="text-xs text-neutral-500">{item.desc}</p>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Diseases covered -->
		<div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-100">
			<h2 class="mb-3 text-lg font-semibold text-neutral-800">🌿 Diseases Covered</h2>
			<div class="flex flex-wrap gap-2">
				{#each ['Rice Blast', 'Tomato Early Blight', 'Wheat Stem Rust', 'Potato Late Blight', 'Northern Corn Leaf Blight', 'Powdery Mildew', 'Downy Mildew', 'Bacterial Leaf Streak', 'Citrus Canker', 'Anthracnose', 'Fusarium Wilt', 'Bacterial Wilt', 'Tomato Leaf Curl Virus', 'Rice Sheath Blight', 'Coffee Leaf Rust'] as disease}
					<span
						class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-100"
					>
						{disease}
					</span>
				{/each}
			</div>
		</div>

		<!-- Tech stack -->
		<div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-100">
			<h2 class="mb-3 text-lg font-semibold text-neutral-800">⚙️ Technology</h2>
			<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
				{#each [{ label: 'Frontend', value: 'SvelteKit' }, { label: 'Backend', value: 'FastAPI' }, { label: 'Database', value: 'Supabase' }, { label: 'AI/ML', value: 'Custom Models' }] as tech}
					<div class="rounded-xl bg-neutral-50 p-3 text-center ring-1 ring-neutral-100">
						<p class="text-[10px] font-medium tracking-wider text-neutral-400 uppercase">
							{tech.label}
						</p>
						<p class="text-sm font-semibold text-neutral-700">{tech.value}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>

	<!-- CTA -->
	<div class="mt-8 text-center">
		<a
			href="/analyze"
			class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-200 transition-all hover:-translate-y-0.5 hover:shadow-xl"
		>
			Start Analyzing
			<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
				/>
			</svg>
		</a>
	</div>
</div>
