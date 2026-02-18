/**
 * API service layer — typed client for communicating with the C-DIT backend.
 */
import type { AnalysisResult, ChatFollowupResponse, ApiResponse, FeedbackRequest } from './types';

const API_BASE = 'http://localhost:3001';
const REQUEST_TIMEOUT = 30000; // 30 seconds

/**
 * Generic fetch wrapper with timeout and error handling.
 */
async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        });

        const json = (await response.json()) as ApiResponse<T>;

        if (!response.ok || !json.success) {
            throw new Error(json.error?.message || `Request failed with status ${response.status}`);
        }

        return json.data as T;
    } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
            throw new Error('Request timed out. The server may be busy — please try again.');
        }
        throw error;
    } finally {
        clearTimeout(timeout);
    }
}

/**
 * Analyze a crop image for disease classification.
 */
export async function analyzeImage(
    imageFile: File,
    sessionId?: string,
    description?: string
): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('image', imageFile);
    if (sessionId) formData.append('sessionId', sessionId);
    if (description) formData.append('description', description);

    return apiFetch<AnalysisResult>(`${API_BASE}/analyze/image`, {
        method: 'POST',
        body: formData,
    });
}

/**
 * Analyze a voice recording for disease advisory.
 */
export async function analyzeVoice(audioBlob: Blob, sessionId?: string): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    if (sessionId) formData.append('sessionId', sessionId);

    return apiFetch<AnalysisResult>(`${API_BASE}/analyze/voice`, {
        method: 'POST',
        body: formData,
    });
}

/**
 * Analyze a text description for disease advisory.
 */
export async function analyzeText(
    description: string,
    sessionId?: string
): Promise<AnalysisResult> {
    return apiFetch<AnalysisResult>(`${API_BASE}/analyze/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, sessionId }),
    });
}

/**
 * Send a follow-up question in an existing session.
 */
export async function sendFollowup(
    sessionId: string,
    message: string
): Promise<ChatFollowupResponse> {
    return apiFetch<ChatFollowupResponse>(`${API_BASE}/chat/followup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, message }),
    });
}

/**
 * Submit farmer feedback.
 */
export async function submitFeedback(feedback: FeedbackRequest): Promise<void> {
    return apiFetch<void>(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedback),
    });
}

/**
 * Check if the backend is available.
 */
export async function healthCheck(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
        return response.ok;
    } catch {
        return false;
    }
}
