<script lang="ts">
  let { message = 'Analyzing...' }: { message?: string } = $props();
</script>

<div class="flex flex-col items-center justify-center gap-4 py-12">
  <div class="relative flex items-center justify-center">
    <!-- Outer pulse ring -->
    <div class="absolute h-16 w-16 rounded-full bg-emerald-200 opacity-30" style="animation: pulse-ring 2s infinite;"></div>
    <!-- Spinning ring -->
    <div class="h-12 w-12 rounded-full border-[3px] border-emerald-100 border-t-emerald-600" style="animation: spin 0.8s linear infinite;"></div>
    <!-- Center icon -->
    <svg class="absolute h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z" />
    </svg>
  </div>
  <p class="text-sm font-medium text-neutral-500">{message}</p>
</div>
