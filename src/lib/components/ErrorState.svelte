<script lang="ts">
  let {
    message = 'Something went wrong.',
    type = 'error',
    onretry,
  }: {
    message?: string;
    type?: 'error' | 'warning' | 'info';
    onretry?: () => void;
  } = $props();

  const styles: Record<string, { bg: string; border: string; icon: string; text: string }> = {
    error: { bg: 'bg-red-50', border: 'border-red-200', icon: 'text-red-500', text: 'text-red-700' },
    warning: { bg: 'bg-amber-50', border: 'border-amber-200', icon: 'text-amber-500', text: 'text-amber-700' },
    info: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'text-blue-500', text: 'text-blue-700' },
  };
  const s = $derived(styles[type]);
</script>

<div class="animate-fade-in rounded-xl border {s.border} {s.bg} p-6 text-center">
  <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full {s.bg}">
    {#if type === 'error'}
      <svg class="h-6 w-6 {s.icon}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
      </svg>
    {:else if type === 'warning'}
      <svg class="h-6 w-6 {s.icon}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
      </svg>
    {:else}
      <svg class="h-6 w-6 {s.icon}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
      </svg>
    {/if}
  </div>
  <p class="mb-4 text-sm font-medium {s.text}">{message}</p>
  {#if onretry}
    <button
      onclick={onretry}
      class="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-neutral-700 shadow-sm ring-1 ring-neutral-200 transition-all hover:bg-neutral-50 hover:shadow-md"
    >
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
      </svg>
      Try Again
    </button>
  {/if}
</div>
