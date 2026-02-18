<script lang="ts">
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { analyzeImage as apiAnalyzeImage } from '$lib/api';
  import { appState } from '$lib/stores.svelte';

  let dragActive = $state(false);
  let selectedFile = $state<File | null>(null);
  let previewUrl = $state<string | null>(null);
  let additionalDescription = $state('');

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave() {
    dragActive = false;
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
    const file = e.dataTransfer?.files[0];
    if (file && file.type.startsWith('image/')) {
      selectFile(file);
    }
  }

  function handleFileInput(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) selectFile(file);
  }

  function selectFile(file: File) {
    selectedFile = file;
    previewUrl = URL.createObjectURL(file);
  }

  function removeFile() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    selectedFile = null;
    previewUrl = null;
  }

  async function handleSubmit() {
    if (!selectedFile) return;
    appState.isAnalyzing = true;
    appState.errorMessage = null;
    try {
      const result = await apiAnalyzeImage(selectedFile, appState.sessionId ?? undefined, additionalDescription || undefined);
      appState.setAnalysisResult(result);
    } catch (err) {
      appState.errorMessage = err instanceof Error ? err.message : 'Failed to analyze image. Please try again.';
    } finally {
      appState.isAnalyzing = false;
    }
  }
</script>

<div class="animate-slide-up space-y-5">
  {#if appState.isAnalyzing}
    <LoadingSpinner message="Analyzing your crop image..." />
  {:else if !selectedFile}
    <!-- Drop zone -->
    <div
      class="relative cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200
        {dragActive ? 'border-emerald-500 bg-emerald-50 scale-[1.01]' : 'border-neutral-300 bg-white hover:border-emerald-400 hover:bg-emerald-50/50'}"
      role="button"
      tabindex="0"
      ondragover={handleDragOver}
      ondragleave={handleDragLeave}
      ondrop={handleDrop}
      onclick={() => document.getElementById('image-input')?.click()}
      onkeydown={(e) => e.key === 'Enter' && document.getElementById('image-input')?.click()}
    >
      <input
        id="image-input"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/bmp"
        class="hidden"
        onchange={handleFileInput}
      />
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-100">
        <svg class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0 0 22.5 18.75V5.25A2.25 2.25 0 0 0 20.25 3H3.75A2.25 2.25 0 0 0 1.5 5.25v13.5A2.25 2.25 0 0 0 3.75 21Z" />
        </svg>
      </div>
      <p class="text-base font-semibold text-neutral-700">Drop your crop image here</p>
      <p class="mt-1 text-sm text-neutral-500">or click to browse · JPEG, PNG, WebP · Max 10 MB</p>
    </div>
  {:else}
    <!-- Preview -->
    <div class="overflow-hidden rounded-2xl bg-white shadow-lg ring-1 ring-neutral-100">
      <div class="relative">
        <img src={previewUrl} alt="Crop preview" class="h-64 w-full object-cover" />
        <button
          onclick={removeFile}
          aria-label="Remove selected image"
          class="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-sm transition-colors hover:bg-black/70"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="p-5">
        <p class="mb-3 text-sm text-neutral-500">
          <span class="font-medium text-neutral-700">{selectedFile.name}</span> · {(selectedFile.size / 1024).toFixed(0)} KB
        </p>
        <textarea
          bind:value={additionalDescription}
          placeholder="(Optional) Describe what you see — e.g., 'yellow spots on lower leaves since last week'"
          class="w-full resize-none rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-700 transition-colors placeholder:text-neutral-400 focus:border-emerald-400 focus:bg-white focus:ring-2 focus:ring-emerald-100 focus:outline-none"
          rows="2"
        ></textarea>
        <button
          onclick={handleSubmit}
          class="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-200 transition-all hover:from-emerald-700 hover:to-green-700 hover:shadow-xl active:scale-[0.98]"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          Analyze Image
        </button>
      </div>
    </div>
  {/if}
</div>
