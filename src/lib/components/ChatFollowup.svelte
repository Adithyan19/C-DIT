<script lang="ts">
  import { sendFollowup } from '$lib/api';
  import { appState } from '$lib/stores.svelte';
  import { tick } from 'svelte';

  let message = $state('');
  let chatContainer: HTMLDivElement | undefined = $state();

  async function scrollToBottom() {
    await tick();
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  async function handleSend() {
    const text = message.trim();
    if (!text || !appState.sessionId || appState.isSendingFollowup) return;

    // Add farmer message
    appState.addChatMessage({
      role: 'farmer',
      content: text,
      timestamp: new Date().toISOString(),
    });
    message = '';
    appState.isSendingFollowup = true;
    await scrollToBottom();

    try {
      const response = await sendFollowup(appState.sessionId, text);
      appState.addChatMessage({
        role: 'assistant',
        content: response.reply,
        timestamp: response.timestamp,
      });
    } catch {
      appState.addChatMessage({
        role: 'assistant',
        content: 'Sorry, I couldn\'t process your question. Please try again.',
        timestamp: new Date().toISOString(),
      });
    } finally {
      appState.isSendingFollowup = false;
      await scrollToBottom();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  // Auto-scroll when messages change
  $effect(() => {
    if (appState.chatMessages.length > 0) {
      scrollToBottom();
    }
  });
</script>

<div class="animate-slide-up">
  <div class="overflow-hidden rounded-2xl bg-white shadow-lg ring-1 ring-neutral-100">
    <!-- Chat header -->
    <div class="flex items-center gap-3 border-b border-neutral-100 px-5 py-3.5">
      <div class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100">
        <svg class="h-4 w-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
        </svg>
      </div>
      <div>
        <p class="text-sm font-semibold text-neutral-800">Follow-up Questions</p>
        <p class="text-xs text-neutral-400">Ask anything about the diagnosis or treatment</p>
      </div>
    </div>

    <!-- Messages -->
    <div
      bind:this={chatContainer}
      class="max-h-[400px] min-h-[200px] space-y-4 overflow-y-auto px-5 py-4"
    >
      {#each appState.chatMessages as msg, i}
        <div class="flex {msg.role === 'farmer' ? 'justify-end' : 'justify-start'} animate-fade-in" style="animation-delay: {i * 50}ms">
          {#if msg.role === 'assistant'}
            <div class="flex max-w-[85%] gap-2.5">
              <div class="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-100">
                <svg class="h-3.5 w-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z" />
                </svg>
              </div>
              <div class="rounded-2xl rounded-tl-sm bg-neutral-50 px-4 py-3 text-sm leading-relaxed text-neutral-700 ring-1 ring-neutral-100">
                {@html msg.content.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
              </div>
            </div>
          {:else}
            <div class="max-w-[85%] rounded-2xl rounded-tr-sm bg-emerald-600 px-4 py-3 text-sm leading-relaxed text-white">
              {msg.content}
            </div>
          {/if}
        </div>
      {/each}

      {#if appState.isSendingFollowup}
        <div class="flex justify-start">
          <div class="flex gap-2.5">
            <div class="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-100">
              <svg class="h-3.5 w-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z" />
              </svg>
            </div>
            <div class="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-neutral-50 px-4 py-3 ring-1 ring-neutral-100">
              <div class="h-2 w-2 rounded-full bg-neutral-400" style="animation: pulse-ring 1s infinite 0ms;"></div>
              <div class="h-2 w-2 rounded-full bg-neutral-400" style="animation: pulse-ring 1s infinite 300ms;"></div>
              <div class="h-2 w-2 rounded-full bg-neutral-400" style="animation: pulse-ring 1s infinite 600ms;"></div>
            </div>
          </div>
        </div>
      {/if}
    </div>

    <!-- Input -->
    <div class="border-t border-neutral-100 px-4 py-3">
      <div class="flex items-end gap-2">
        <textarea
          bind:value={message}
          onkeydown={handleKeydown}
          placeholder="Type your follow-up question..."
          rows="1"
          class="flex-1 resize-none rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-2.5 text-sm text-neutral-700 transition-colors placeholder:text-neutral-400 focus:border-emerald-400 focus:bg-white focus:ring-2 focus:ring-emerald-100 focus:outline-none"
        ></textarea>
        <button
          onclick={handleSend}
          disabled={!message.trim() || appState.isSendingFollowup}
          aria-label="Send message"
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-all
            {message.trim() && !appState.isSendingFollowup
              ? 'bg-emerald-600 text-white shadow-md hover:bg-emerald-700 active:scale-95 cursor-pointer'
              : 'bg-neutral-100 text-neutral-400 cursor-not-allowed'}"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
