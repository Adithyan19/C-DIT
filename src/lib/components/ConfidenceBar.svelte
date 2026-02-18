<script lang="ts">
  import { ConfidenceLevel } from '$lib/types';

  let { confidence, confidenceLevel }: { confidence: number; confidenceLevel: ConfidenceLevel } = $props();

  const percentage = $derived(Math.round(confidence * 100));

  function getColor(level: ConfidenceLevel): string {
    switch (level) {
      case ConfidenceLevel.HIGH: return 'bg-emerald-500';
      case ConfidenceLevel.MEDIUM: return 'bg-amber-500';
      case ConfidenceLevel.LOW: return 'bg-orange-500';
      case ConfidenceLevel.UNKNOWN: return 'bg-red-500';
    }
  }

  function getLabel(level: ConfidenceLevel): string {
    switch (level) {
      case ConfidenceLevel.HIGH: return 'High Confidence';
      case ConfidenceLevel.MEDIUM: return 'Moderate Confidence';
      case ConfidenceLevel.LOW: return 'Low Confidence';
      case ConfidenceLevel.UNKNOWN: return 'Unknown';
    }
  }

  function getTextColor(level: ConfidenceLevel): string {
    switch (level) {
      case ConfidenceLevel.HIGH: return 'text-emerald-700';
      case ConfidenceLevel.MEDIUM: return 'text-amber-700';
      case ConfidenceLevel.LOW: return 'text-orange-700';
      case ConfidenceLevel.UNKNOWN: return 'text-red-700';
    }
  }
</script>

<div class="space-y-2">
  <div class="flex items-center justify-between text-sm">
    <span class="font-medium {getTextColor(confidenceLevel)}">{getLabel(confidenceLevel)}</span>
    <span class="font-bold {getTextColor(confidenceLevel)}">{percentage}%</span>
  </div>
  <div class="h-2.5 w-full overflow-hidden rounded-full bg-neutral-100">
    <div
      class="h-full rounded-full transition-all duration-700 ease-out {getColor(confidenceLevel)}"
      style="width: {percentage}%"
    ></div>
  </div>
</div>
