<script lang="ts">
  import ConfidenceBar from './ConfidenceBar.svelte';
  import ErrorState from './ErrorState.svelte';
  import { ConfidenceLevel } from '$lib/types';
  import { appState } from '$lib/stores.svelte';

  let { onback }: { onback: () => void } = $props();

  const result = $derived(appState.analysisResult);
</script>

<div class="animate-slide-up space-y-5">
  {#if result}
    <!-- Disease Card -->
    <div class="overflow-hidden rounded-2xl bg-white shadow-lg ring-1 ring-neutral-100">
      <!-- Header with disease name -->
      <div class="relative bg-gradient-to-r from-emerald-600 to-green-600 px-6 py-5">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20viewBox%3D%220%200%2020%2020%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2210%22%20cy%3D%2210%22%20r%3D%221.5%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E')]"></div>
        <div class="relative">
          {#if result.disease.isKnown}
            <div class="mb-1 flex items-center gap-2">
              <span class="inline-flex items-center gap-1 rounded-full bg-white/20 px-2.5 py-0.5 text-xs font-medium text-white backdrop-blur-sm">
                {#if result.disease.confidenceLevel === ConfidenceLevel.HIGH}
                  ✓ Identified
                {:else}
                  ⚠ Suspected
                {/if}
              </span>
            </div>
            <h2 class="text-2xl font-bold text-white">{result.disease.label}</h2>
          {:else}
            <div class="mb-1 flex items-center gap-2">
              <span class="inline-flex items-center gap-1 rounded-full bg-amber-400/30 px-2.5 py-0.5 text-xs font-medium text-white backdrop-blur-sm">
                ⚠ Unidentified
              </span>
            </div>
            <h2 class="text-2xl font-bold text-white">Disease Not Identified</h2>
          {/if}
        </div>
      </div>

      <!-- Confidence bar -->
      <div class="border-b border-neutral-100 px-6 py-4">
        <ConfidenceBar confidence={result.disease.confidence} confidenceLevel={result.disease.confidenceLevel} />
      </div>

      <!-- Advisory text -->
      <div class="px-6 py-5">
        <h3 class="mb-3 flex items-center gap-2 text-sm font-semibold tracking-wide text-emerald-700 uppercase">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
          </svg>
          Expert Advisory
        </h3>
        <div class="prose prose-sm max-w-none text-neutral-700 leading-relaxed">
          {@html result.advisory.replace(/\n/g, '<br>').replace(/## (.*)/g, '<strong class="text-emerald-800">$1</strong>').replace(/### (.*)/g, '<strong class="text-neutral-800 text-sm">$1</strong>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/> (.*)/g, '<blockquote class="border-l-2 border-emerald-300 pl-3 italic text-neutral-500">$1</blockquote>')}
        </div>
      </div>
    </div>

    <!-- Low Confidence / Unknown warnings -->
    {#if result.disease.confidenceLevel === ConfidenceLevel.LOW}
      <ErrorState
        type="warning"
        message="The confidence score is low. We recommend consulting your local agricultural extension officer or Krishi Vigyan Kendra for a detailed diagnosis."
      />
    {:else if result.disease.confidenceLevel === ConfidenceLevel.UNKNOWN}
      <ErrorState
        type="warning"
        message="We couldn't identify a specific disease. This case has been flagged for expert review. Please consult your local agricultural office."
      />
    {/if}

    <!-- Follow-up suggestions -->
    {#if result.followUpSuggestions.length > 0}
      <div class="rounded-2xl bg-white p-5 shadow-lg ring-1 ring-neutral-100">
        <h3 class="mb-3 text-sm font-semibold text-neutral-700">Suggested Follow-up Questions</h3>
        <div class="flex flex-wrap gap-2">
          {#each result.followUpSuggestions as suggestion}
            <button
              class="rounded-full border border-emerald-200 bg-emerald-50 px-3.5 py-1.5 text-xs font-medium text-emerald-700 transition-all hover:bg-emerald-100 hover:shadow-sm active:scale-95"
            >
              {suggestion}
            </button>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Back button -->
    <button
      onclick={onback}
      class="flex items-center gap-2 text-sm font-medium text-neutral-500 transition-colors hover:text-emerald-600"
    >
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" />
      </svg>
      Analyze another crop
    </button>
  {/if}
</div>
