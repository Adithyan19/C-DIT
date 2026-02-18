/**
 * Svelte 5 reactive stores for application state.
 * Uses an exported object with $state properties (Svelte 5 module pattern).
 */
import type { AnalysisResult, ChatMessage } from './types';

/** Reactive application state */
function createAppState() {
    let sessionId = $state<string | null>(null);
    let analysisResult = $state<AnalysisResult | null>(null);
    let chatMessages = $state<ChatMessage[]>([]);
    let isAnalyzing = $state(false);
    let isSendingFollowup = $state(false);
    let activeInputMode = $state<'image' | 'voice' | 'text' | null>(null);
    let errorMessage = $state<string | null>(null);

    return {
        get sessionId() { return sessionId; },
        set sessionId(v: string | null) { sessionId = v; },

        get analysisResult() { return analysisResult; },
        set analysisResult(v: AnalysisResult | null) { analysisResult = v; },

        get chatMessages() { return chatMessages; },
        set chatMessages(v: ChatMessage[]) { chatMessages = v; },

        get isAnalyzing() { return isAnalyzing; },
        set isAnalyzing(v: boolean) { isAnalyzing = v; },

        get isSendingFollowup() { return isSendingFollowup; },
        set isSendingFollowup(v: boolean) { isSendingFollowup = v; },

        get activeInputMode() { return activeInputMode; },
        set activeInputMode(v: 'image' | 'voice' | 'text' | null) { activeInputMode = v; },

        get errorMessage() { return errorMessage; },
        set errorMessage(v: string | null) { errorMessage = v; },

        /** Reset all state for a new session */
        resetSession() {
            sessionId = null;
            analysisResult = null;
            chatMessages = [];
            isAnalyzing = false;
            isSendingFollowup = false;
            activeInputMode = null;
            errorMessage = null;
        },

        /** Set analysis result and extract session info */
        setAnalysisResult(result: AnalysisResult) {
            analysisResult = result;
            sessionId = result.sessionId;
            chatMessages = [
                {
                    role: 'assistant',
                    content: result.advisory,
                    timestamp: result.timestamp,
                },
            ];
        },

        /** Add a chat message */
        addChatMessage(message: ChatMessage) {
            chatMessages = [...chatMessages, message];
        },
    };
}

export const appState = createAppState();
