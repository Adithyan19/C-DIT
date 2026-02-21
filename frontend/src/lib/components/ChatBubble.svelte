<script>
    export let message;

    function formatTime(dateStr) {
        const d = new Date(dateStr);
        return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    // Simple markdown-like bold rendering
    function renderText(text) {
        if (!text) return "";
        return text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");
    }
</script>

<div class="bubble-wrapper {message.sender}">
    <div class="bubble {message.sender}">
        {#if message.image_url}
            <div class="bubble-image">
                <img src={message.image_url} alt="Uploaded" />
            </div>
        {/if}
        {#if message.voice_url}
            <div class="bubble-voice">
                <audio controls src={message.voice_url}></audio>
            </div>
        {/if}
        {#if message.text_content}
            <div class="bubble-text">
                {@html renderText(message.text_content)}
            </div>
        {/if}
        <div class="bubble-time">{formatTime(message.created_at)}</div>
    </div>
</div>

<style>
    .bubble-wrapper {
        display: flex;
        margin-bottom: 12px;
        padding: 0 16px;
    }
    .bubble-wrapper.user {
        justify-content: flex-end;
    }
    .bubble-wrapper.bot {
        justify-content: flex-start;
    }
    .bubble {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 0.92rem;
        line-height: 1.5;
        word-break: break-word;
    }
    .bubble.user {
        background: var(--primary);
        color: #fff;
        border-bottom-right-radius: 4px;
    }
    .bubble.bot {
        background: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        border-bottom-left-radius: 4px;
    }
    .bubble-image {
        margin-bottom: 8px;
    }
    .bubble-image img {
        max-width: 100%;
        max-height: 250px;
        border-radius: 8px;
        display: block;
    }
    .bubble-voice audio {
        max-width: 100%;
    }
    .bubble-time {
        font-size: 0.7rem;
        margin-top: 6px;
        opacity: 0.6;
        text-align: right;
    }
    .bubble.user .bubble-time {
        color: rgba(255, 255, 255, 0.7);
    }
</style>
