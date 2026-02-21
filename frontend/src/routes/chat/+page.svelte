<script>
    import { onMount, tick } from "svelte";
    import { user } from "$lib/stores.js";
    import {
        listConversations,
        createConversation,
        getMessages,
        sendMessage,
    } from "$lib/api.js";
    import ChatBubble from "$lib/components/ChatBubble.svelte";
    import ChatInput from "$lib/components/ChatInput.svelte";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    let conversations = [];
    let activeConvId = null;
    let messages = [];
    let loading = false;
    let sending = false;
    let sidebarOpen = true;
    let messagesContainer;
    let location = null;

    onMount(async () => {
        // Get user location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    location = {
                        lat: pos.coords.latitude,
                        lng: pos.coords.longitude,
                    };
                },
                () => {
                    /* location denied */
                },
            );
        }
        await loadConversations();
    });

    async function loadConversations() {
        try {
            conversations = await listConversations();
        } catch (e) {
            console.error("Failed to load conversations", e);
        }
    }

    async function selectConversation(convId) {
        activeConvId = convId;
        loading = true;
        try {
            messages = await getMessages(convId);
            await tick();
            scrollToBottom();
        } catch (e) {
            console.error("Failed to load messages", e);
        } finally {
            loading = false;
        }
    }

    async function handleNewConversation() {
        try {
            const conv = await createConversation();
            conversations = [conv, ...conversations];
            await selectConversation(conv.id);
        } catch (e) {
            console.error("Failed to create conversation", e);
        }
    }

    async function handleSend(event) {
        const { text, image, voice } = event.detail;

        // Auto-create conversation if none active
        if (!activeConvId) {
            try {
                const conv = await createConversation();
                conversations = [conv, ...conversations];
                activeConvId = conv.id;
            } catch (e) {
                console.error("Failed to create conversation", e);
                return;
            }
        }

        sending = true;
        try {
            const newMsgs = await sendMessage(activeConvId, {
                text,
                image,
                voice,
                location_lat: location?.lat,
                location_lng: location?.lng,
            });
            messages = [...messages, ...newMsgs];
            await tick();
            scrollToBottom();
            await loadConversations();
        } catch (e) {
            console.error("Failed to send message", e);
        } finally {
            sending = false;
        }
    }

    function scrollToBottom() {
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString([], {
            month: "short",
            day: "numeric",
        });
    }
</script>

<div class="chat-layout">
    <!-- Sidebar -->
    <div class="sidebar" class:collapsed={!sidebarOpen}>
        <div class="sidebar-header">
            <h3>Conversations</h3>
            <button
                class="btn btn-sm btn-primary"
                on:click={handleNewConversation}>+ New</button
            >
        </div>
        <div class="conv-list">
            {#each conversations as conv}
                <button
                    class="conv-item"
                    class:active={activeConvId === conv.id}
                    on:click={() => selectConversation(conv.id)}
                >
                    <span class="conv-title">{conv.title}</span>
                    <span class="conv-date">{formatDate(conv.started_at)}</span>
                </button>
            {/each}
            {#if conversations.length === 0}
                <p class="empty-text">No conversations yet.</p>
            {/if}
        </div>
    </div>

    <!-- Toggle sidebar on mobile -->
    <button
        class="sidebar-toggle"
        on:click={() => (sidebarOpen = !sidebarOpen)}
    >
        {sidebarOpen ? "<" : ">"}
    </button>

    <!-- Chat area -->
    <div class="chat-main">
        <div class="messages-area" bind:this={messagesContainer}>
            {#if activeConvId && loading}
                <p class="loading-text">Loading messages...</p>
            {:else if activeConvId}
                {#each messages as msg}
                    <ChatBubble message={msg} />
                {/each}
                {#if sending}
                    <div class="bubble-wrapper bot">
                        <div class="bubble bot typing">
                            <span class="dot"></span><span class="dot"
                            ></span><span class="dot"></span>
                        </div>
                    </div>
                {/if}
            {:else}
                <div class="chat-welcome">
                    <h2>FarmBot Disease Assistant</h2>
                    <p>
                        Send a text message, photo of your crop, or voice
                        message to get disease diagnosis and treatment advice.
                    </p>
                </div>
            {/if}
        </div>

        <ChatInput on:send={handleSend} />
    </div>
</div>

<style>
    .chat-layout {
        display: flex;
        height: calc(100vh - 57px);
        overflow: hidden;
    }

    /* Sidebar */
    .sidebar {
        width: 280px;
        background: var(--surface);
        border-right: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        transition: width 0.2s;
    }
    .sidebar.collapsed {
        width: 0;
        overflow: hidden;
    }
    .sidebar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-bottom: 1px solid var(--border);
    }
    .sidebar-header h3 {
        font-size: 1rem;
        color: var(--text);
    }
    .conv-list {
        flex: 1;
        overflow-y: auto;
        padding: 8px;
    }
    .conv-item {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        width: 100%;
        padding: 12px;
        border: none;
        background: none;
        border-radius: var(--radius);
        cursor: pointer;
        text-align: left;
        transition: background 0.2s;
    }
    .conv-item:hover {
        background: #f0f0ea;
    }
    .conv-item.active {
        background: #e8f5e9;
    }
    .conv-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    .conv-date {
        font-size: 0.75rem;
        color: var(--text-light);
        margin-top: 2px;
    }
    .empty-text {
        text-align: center;
        color: var(--text-light);
        padding: 40px 16px;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .sidebar-toggle {
        position: fixed;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        z-index: 50;
        width: 24px;
        height: 48px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: none;
        border-radius: 0 6px 6px 0;
        cursor: pointer;
        font-size: 0.7rem;
        display: none;
    }

    /* Chat main */
    .chat-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-width: 0;
    }

    .messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 20px 0;
    }

    .chat-welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        padding: 40px;
    }
    .chat-welcome h2 {
        color: var(--primary-dark);
        margin-bottom: 8px;
    }
    .chat-welcome p {
        color: var(--text-secondary);
        max-width: 400px;
    }

    .loading-text {
        text-align: center;
        color: var(--text-light);
        padding: 40px;
    }

    /* Typing indicator */
    .typing {
        display: flex;
        gap: 4px;
        padding: 12px 18px !important;
    }
    .dot {
        width: 8px;
        height: 8px;
        background: var(--border);
        border-radius: 50%;
        animation: bounce 1.4s infinite both;
    }
    .dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    .dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes bounce {
        0%,
        80%,
        100% {
            transform: scale(0.6);
        }
        40% {
            transform: scale(1);
        }
    }

    .bubble-wrapper {
        display: flex;
        padding: 0 16px;
        margin-bottom: 12px;
    }
    .bubble-wrapper.bot {
        justify-content: flex-start;
    }
    .bubble {
        padding: 12px 16px;
        border-radius: 16px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-bottom-left-radius: 4px;
    }

    @media (max-width: 768px) {
        .sidebar {
            position: fixed;
            z-index: 90;
            height: calc(100vh - 57px);
            top: 57px;
        }
        .sidebar.collapsed {
            width: 0;
        }
        .sidebar-toggle {
            display: block;
        }
    }
</style>
