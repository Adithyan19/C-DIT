const API_BASE = 'http://localhost:8000';

function getToken() {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('token');
}

async function request(path, options = {}) {
    const token = getToken();
    const headers = { ...options.headers };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Don't set Content-Type for FormData — browser sets it with boundary
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || 'Request failed');
    }

    return res.json();
}

// AUTH
export async function signup(email, password, full_name) {
    const data = await request('/api/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name }),
    });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
}

export async function login(email, password) {
    const data = await request('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
}

export function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

export async function getMe() {
    return request('/api/auth/me');
}

// USER
export async function getProfile() {
    return request('/api/users/profile');
}

export async function updateProfile(data) {
    return request('/api/users/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

export async function changePassword(current_password, new_password) {
    return request('/api/users/password', {
        method: 'PUT',
        body: JSON.stringify({ current_password, new_password }),
    });
}

// CHAT
export async function createConversation(title) {
    return request('/api/chat/conversations', {
        method: 'POST',
        body: JSON.stringify({ title: title || 'New Conversation' }),
    });
}

export async function listConversations() {
    return request('/api/chat/conversations');
}

export async function getMessages(conversationId) {
    return request(`/api/chat/conversations/${conversationId}/messages`);
}

export async function sendMessage(conversationId, { text, image, voice, location_lat, location_lng }) {
    const form = new FormData();
    form.append('conversation_id', conversationId);
    if (text) form.append('text', text);
    if (image) form.append('image', image);
    if (voice) form.append('voice', voice);
    if (location_lat != null) form.append('location_lat', location_lat);
    if (location_lng != null) form.append('location_lng', location_lng);

    return request('/api/chat/messages', {
        method: 'POST',
        body: form,
    });
}

// MITL
export async function getMitlStats() {
    return request('/api/mitl/stats');
}

export async function getPendingDiseases() {
    return request('/api/mitl/pending');
}

export async function getClassifiedDiseases() {
    return request('/api/mitl/classified');
}

export async function getPendingDetail(id) {
    return request(`/api/mitl/pending/${id}`);
}

export async function classifyDisease(id, data) {
    return request(`/api/mitl/classify/${id}`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ADMIN (superadmin)
export async function getAdminStats() {
    return request('/api/admin/stats');
}

export async function listAllUsers() {
    return request('/api/admin/users');
}

export async function createMitlAccount(email, password, full_name) {
    return request('/api/admin/create-mitl', {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name }),
    });
}
