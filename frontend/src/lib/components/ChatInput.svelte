<script>
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    let text = "";
    let imageFile = null;
    let imagePreview = null;
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let voiceBlob = null;
    let voiceDuration = 0;
    let recordingTimer = null;
    let sending = false;

    let fileInput;

    function handleImageSelect(e) {
        const file = e.target.files[0];
        if (file) {
            imageFile = file;
            const reader = new FileReader();
            reader.onload = (ev) => {
                imagePreview = ev.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    function removeImage() {
        imageFile = null;
        imagePreview = null;
        if (fileInput) fileInput.value = "";
    }

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            voiceDuration = 0;

            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };
            mediaRecorder.onstop = () => {
                voiceBlob = new Blob(audioChunks, { type: "audio/webm" });
                stream.getTracks().forEach((t) => t.stop());
                clearInterval(recordingTimer);
            };

            mediaRecorder.start();
            isRecording = true;
            recordingTimer = setInterval(() => {
                voiceDuration += 1;
            }, 1000);
        } catch (err) {
            alert(
                "Could not access microphone. Please allow microphone access.",
            );
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
        }
    }

    function removeVoice() {
        voiceBlob = null;
        voiceDuration = 0;
    }

    async function handleSend() {
        if (sending) return;
        if (!text.trim() && !imageFile && !voiceBlob) return;

        sending = true;
        dispatch("send", {
            text: text.trim() || null,
            image: imageFile,
            voice: voiceBlob
                ? new File([voiceBlob], "voice.webm", { type: "audio/webm" })
                : null,
        });

        // Reset
        text = "";
        imageFile = null;
        imagePreview = null;
        voiceBlob = null;
        voiceDuration = 0;
        if (fileInput) fileInput.value = "";
        sending = false;
    }

    function handleKeydown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }
</script>

<div class="chat-input-container">
    {#if imagePreview}
        <div class="preview-bar">
            <div class="image-preview">
                <img src={imagePreview} alt="Preview" />
                <button class="remove-btn" on:click={removeImage}>✕</button>
            </div>
        </div>
    {/if}
    {#if voiceBlob}
        <div class="preview-bar">
            <div class="voice-preview">
                <span>🎤 Voice ({voiceDuration}s)</span>
                <button class="remove-btn" on:click={removeVoice}>✕</button>
            </div>
        </div>
    {/if}
    <div class="input-row">
        <button
            class="icon-btn"
            on:click={() => fileInput.click()}
            title="Attach image"
        >
            📷
        </button>
        <input
            type="file"
            accept="image/*"
            bind:this={fileInput}
            on:change={handleImageSelect}
            hidden
        />

        {#if isRecording}
            <button
                class="icon-btn recording"
                on:click={stopRecording}
                title="Stop recording"
            >
                ⏹️ {voiceDuration}s
            </button>
        {:else}
            <button
                class="icon-btn"
                on:click={startRecording}
                title="Record voice"
            >
                🎤
            </button>
        {/if}

        <textarea
            bind:value={text}
            on:keydown={handleKeydown}
            placeholder="Describe your crop issue..."
            rows="1"
        ></textarea>

        <button
            class="send-btn"
            on:click={handleSend}
            disabled={sending || (!text.trim() && !imageFile && !voiceBlob)}
        >
            ➤
        </button>
    </div>
</div>

<style>
    .chat-input-container {
        border-top: 1px solid var(--border);
        background: var(--surface);
        padding: 12px 16px;
    }
    .preview-bar {
        margin-bottom: 10px;
    }
    .image-preview {
        position: relative;
        display: inline-block;
    }
    .image-preview img {
        height: 60px;
        border-radius: 6px;
        border: 1px solid var(--border);
    }
    .remove-btn {
        position: absolute;
        top: -6px;
        right: -6px;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--error);
        color: #fff;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        cursor: pointer;
    }
    .voice-preview {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: #e8f5e9;
        border-radius: 20px;
        font-size: 0.85rem;
        color: var(--primary);
    }
    .voice-preview .remove-btn {
        position: static;
        width: 18px;
        height: 18px;
    }
    .input-row {
        display: flex;
        align-items: flex-end;
        gap: 8px;
    }
    .icon-btn {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #f0f0ea;
        border: none;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        flex-shrink: 0;
        transition: background 0.2s;
    }
    .icon-btn:hover {
        background: #e0e0d8;
    }
    .icon-btn.recording {
        background: var(--error);
        color: #fff;
        font-size: 0.8rem;
        width: auto;
        padding: 0 12px;
        border-radius: 20px;
    }
    textarea {
        flex: 1;
        resize: none;
        min-height: 40px;
        max-height: 120px;
        padding: 10px 14px;
        border: 1px solid var(--border);
        border-radius: 20px;
        font-size: 0.92rem;
        line-height: 1.4;
        outline: none;
    }
    textarea:focus {
        border-color: var(--primary);
    }
    .send-btn {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--primary);
        color: #fff;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }
    .send-btn:hover:not(:disabled) {
        background: var(--primary-dark);
    }
    .send-btn:disabled {
        opacity: 0.4;
        cursor: default;
    }
</style>
