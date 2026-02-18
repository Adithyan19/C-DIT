/**
 * Frontend TypeScript interfaces matching backend API response shapes.
 */

export enum ConfidenceLevel {
    HIGH = 'HIGH',
    MEDIUM = 'MEDIUM',
    LOW = 'LOW',
    UNKNOWN = 'UNKNOWN',
}

export interface DiseaseClassification {
    label: string;
    confidence: number;
    confidenceLevel: ConfidenceLevel;
    isKnown: boolean;
}

export interface RetrievedContext {
    documentId: string;
    content: string;
    similarity: number;
    metadata: {
        diseaseName: string;
        category: string;
        source: string;
    };
}

export interface AnalysisResult {
    sessionId: string;
    disease: DiseaseClassification;
    advisory: string;
    retrievedContext: RetrievedContext[];
    followUpSuggestions: string[];
    timestamp: string;
    transcribedText?: string; // Only for voice analysis
}

export interface ChatMessage {
    role: 'farmer' | 'assistant';
    content: string;
    timestamp: string;
}

export interface ChatFollowupResponse {
    sessionId: string;
    reply: string;
    timestamp: string;
}

export interface FeedbackRequest {
    sessionId: string;
    rating: number;
    comment?: string;
    wasHelpful: boolean;
    correctDisease?: string;
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: { message: string };
}
