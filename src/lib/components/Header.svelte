<script lang="ts">
	import { page } from '$app/state';

	const navLinks = [
		{ href: '/', label: 'Home' },
		{ href: '/analyze', label: 'Analyze' },
		{ href: '/history', label: 'History' },
		{ href: '/about', label: 'About' }
	];

	let mobileMenuOpen = $state(false);
</script>

<header
	class="fixed top-0 right-0 left-0 z-50 border-b border-emerald-100 bg-white/80 backdrop-blur-lg"
>
	<div class="mx-auto flex h-[72px] max-w-[1200px] items-center justify-between px-6">
		<a href="/" class="flex items-center gap-3 transition-opacity hover:opacity-80">
			<!-- Leaf icon -->
			<div
				class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-md"
			>
				<svg
					class="h-6 w-6 text-white"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="2"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z M17.5 2.5c0 0-1.5 3-1.5 6s1.5 6 1.5 6 M14 6c0 0 2 1 3.5 1s3.5-1 3.5-1"
					/>
				</svg>
			</div>
			<div>
				<h1 class="text-lg font-bold tracking-tight text-emerald-900">KrishiRakshak</h1>
				<p class="text-[11px] font-medium tracking-wide text-emerald-600 uppercase">
					Crop Disease Advisor
				</p>
			</div>
		</a>

		<!-- Desktop Navigation -->
		<nav class="hidden items-center gap-1 md:flex">
			{#each navLinks as link}
				<a
					href={link.href}
					class="rounded-lg px-3.5 py-2 text-sm font-medium transition-colors
            {page.url.pathname === link.href
						? 'bg-emerald-50 text-emerald-700'
						: 'text-neutral-500 hover:bg-neutral-50 hover:text-neutral-800'}"
				>
					{link.label}
				</a>
			{/each}
		</nav>

		<!-- Mobile menu button -->
		<button
			onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
			class="flex h-10 w-10 items-center justify-center rounded-lg text-neutral-500 hover:bg-neutral-100 md:hidden"
			aria-label="Toggle menu"
		>
			{#if mobileMenuOpen}
				<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
				</svg>
			{:else}
				<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
					/>
				</svg>
			{/if}
		</button>
	</div>

	<!-- Mobile Navigation -->
	{#if mobileMenuOpen}
		<div class="border-t border-neutral-100 bg-white/95 backdrop-blur-lg md:hidden">
			<nav class="mx-auto max-w-[1200px] px-6 py-3">
				{#each navLinks as link}
					<a
						href={link.href}
						onclick={() => (mobileMenuOpen = false)}
						class="block rounded-lg px-3 py-2.5 text-sm font-medium transition-colors
              {page.url.pathname === link.href
							? 'bg-emerald-50 text-emerald-700'
							: 'text-neutral-500 hover:bg-neutral-50 hover:text-neutral-800'}"
					>
						{link.label}
					</a>
				{/each}
			</nav>
		</div>
	{/if}
</header>
