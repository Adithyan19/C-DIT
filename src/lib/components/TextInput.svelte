<script lang="ts">
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { analyzeText as apiAnalyzeText } from '$lib/api';
  import { appState } from '$lib/stores.svelte';

  let description = $state('');
  const MAX_LENGTH = 2000;
  const MIN_LENGTH = 5;

  const charCount = $derived(description.length);
  const isValid = $derived(description.trim().length >= MIN_LENGTH);

  async function handleSubmit() {
    if (!isValid) return;
    appState.isAnalyzing = true;
    appState.errorMessage = null;
    try {
      const result = await apiAnalyzeText(description, appState.sessionId ?? undefined);
      appState.setAnalysisResult(result);
    } catch (err) {
      appState.errorMessage = err instanceof Error ? err.message : 'Failed to analyze description. Please try again.';
    } finally {
      appState.isAnalyzing = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && isValid) {
      handleSubmit();
    }
  }
</script>

<div class="animate-slide-up">
  {#if appState.isAnalyzing}
    <LoadingSpinner message="Analyzing your crop description..." />
  {:else}
    <div class="rounded-2xl bg-white p-6 shadow-lg ring-1 ring-neutral-100">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100">
          <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.573 48.573 0 0 0 5.886-.363c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
          </svg>
        </div>
        <div>
          <p class="text-base font-semibold text-neutral-700">Describe Your Crop Problem</p>
          <p class="text-sm text-neutral-500">Tell us about the symptoms you've observed</p>
        </div>
      </div>

      <textarea
        bind:value={description}
        onkeydown={handleKeydown}
        placeholder="e.g., My tomato plant leaves have dark brown spots with yellow edges. The spots started appearing about a week ago on the lower leaves and are spreading upward..."
        maxlength={MAX_LENGTH}
        class="w-full resize-none rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3.5 text-sm leading-relaxed text-neutral-700 transition-colors placeholder:text-neutral-400 focus:border-emerald-400 focus:bg-white focus:ring-2 focus:ring-emerald-100 focus:outline-none"
        rows="5"
      ></textarea>

      <div class="mt-2 flex items-center justify-between">
        <p class="text-xs text-neutral-400">
          {#if charCount < MIN_LENGTH}
            <span class="text-amber-500">Minimum {MIN_LENGTH} characters</span>
          {:else}
            <span class="text-emerald-500">✓ Ready to analyze</span>
          {/if}
        </p>
        <p class="text-xs tabular-nums {charCount > MAX_LENGTH * 0.9 ? 'text-amber-500' : 'text-neutral-400'}">
          {charCount}/{MAX_LENGTH}
        </p>
      </div>

      <button
        onclick={handleSubmit}
        disabled={!isValid}
        class="mt-4 flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white shadow-lg transition-all active:scale-[0.98]
          {isValid
            ? 'bg-gradient-to-r from-emerald-600 to-green-600 shadow-emerald-200 hover:from-emerald-700 hover:to-green-700 hover:shadow-xl cursor-pointer'
            : 'bg-neutral-300 shadow-none cursor-not-allowed'}"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
        </svg>
        Analyze Description
        <span class="ml-1 text-xs font-normal opacity-70">(Ctrl+Enter)</span>
      </button>
    </div>
  {/if}
</div>
