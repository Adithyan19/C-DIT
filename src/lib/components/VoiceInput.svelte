<script lang="ts">
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { analyzeVoice as apiAnalyzeVoice } from '$lib/api';
  import { appState } from '$lib/stores.svelte';

  let isRecording = $state(false);
  let recordingTime = $state(0);
  let audioBlob = $state<Blob | null>(null);
  let audioUrl = $state<string | null>(null);
  let transcribedText = $state<string | null>(null);

  let mediaRecorder: MediaRecorder | null = null;
  let timerInterval: ReturnType<typeof setInterval> | null = null;
  let audioChunks: BlobPart[] = [];

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        audioBlob = blob;
        audioUrl = URL.createObjectURL(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      isRecording = true;
      recordingTime = 0;
      timerInterval = setInterval(() => {
        recordingTime++;
      }, 1000);
    } catch {
      appState.errorMessage = 'Microphone access denied. Please allow microphone access in your browser settings.';
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    isRecording = false;
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function resetRecording() {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    audioBlob = null;
    audioUrl = null;
    transcribedText = null;
    recordingTime = 0;
  }

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  async function handleSubmit() {
    if (!audioBlob) return;
    appState.isAnalyzing = true;
    appState.errorMessage = null;
    try {
      const result = await apiAnalyzeVoice(audioBlob, appState.sessionId ?? undefined);
      transcribedText = result.transcribedText ?? null;
      appState.setAnalysisResult(result);
    } catch (err) {
      appState.errorMessage = err instanceof Error ? err.message : 'Failed to analyze voice recording. Please try again.';
    } finally {
      appState.isAnalyzing = false;
    }
  }
</script>

<div class="animate-slide-up space-y-5">
  {#if appState.isAnalyzing}
    <LoadingSpinner message="Processing your voice recording..." />
  {:else if !audioBlob}
    <!-- Recording UI -->
    <div class="flex flex-col items-center gap-6 rounded-2xl bg-white p-8 shadow-lg ring-1 ring-neutral-100">
      <div class="relative">
        {#if isRecording}
          <div class="absolute -inset-4 rounded-full bg-red-100 opacity-40" style="animation: pulse-ring 1.5s infinite;"></div>
        {/if}
        <button
          onclick={isRecording ? stopRecording : startRecording}
          aria-label={isRecording ? 'Stop recording' : 'Start recording'}
          class="relative flex h-20 w-20 items-center justify-center rounded-full transition-all duration-300
            {isRecording
              ? 'bg-red-500 shadow-lg shadow-red-200 hover:bg-red-600'
              : 'bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-200 hover:from-emerald-600 hover:to-green-700'
            } active:scale-95"
        >
          {#if isRecording}
            <svg class="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          {:else}
            <svg class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
            </svg>
          {/if}
        </button>
      </div>

      {#if isRecording}
        <div class="text-center">
          <p class="text-2xl font-bold tabular-nums text-red-600">{formatTime(recordingTime)}</p>
          <p class="mt-1 text-sm text-neutral-500">Recording... Tap the button to stop</p>
        </div>
      {:else}
        <div class="text-center">
          <p class="text-base font-semibold text-neutral-700">Tap to start recording</p>
          <p class="mt-1 text-sm text-neutral-500">Describe your crop's symptoms in your own words</p>
        </div>
      {/if}
    </div>
  {:else}
    <!-- Playback & Submit -->
    <div class="rounded-2xl bg-white p-6 shadow-lg ring-1 ring-neutral-100">
      <div class="mb-4 flex items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100">
          <svg class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
          </svg>
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium text-neutral-700">Voice Recording</p>
          <p class="text-xs text-neutral-400">{formatTime(recordingTime)} duration</p>
        </div>
        <button onclick={resetRecording} class="text-sm font-medium text-red-500 hover:text-red-600">Re-record</button>
      </div>

      {#if audioUrl}
        <audio controls src={audioUrl} class="mb-4 w-full rounded-lg"></audio>
      {/if}

      {#if transcribedText}
        <div class="mb-4 rounded-xl bg-emerald-50 p-4">
          <p class="mb-1 text-xs font-semibold tracking-wide text-emerald-600 uppercase">Transcribed Text</p>
          <p class="text-sm text-neutral-700">{transcribedText}</p>
        </div>
      {/if}

      <button
        onclick={handleSubmit}
        class="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-200 transition-all hover:from-emerald-700 hover:to-green-700 hover:shadow-xl active:scale-[0.98]"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
        </svg>
        Analyze Recording
      </button>
    </div>
  {/if}
</div>
