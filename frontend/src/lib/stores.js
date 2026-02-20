import { writable } from 'svelte/store';

function createAuthStore() {
    let initial = null;
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem('user');
        if (stored) {
            try { initial = JSON.parse(stored); } catch { initial = null; }
        }
    }
    const { subscribe, set, update } = writable(initial);

    return {
        subscribe,
        set: (user) => {
            if (typeof window !== 'undefined') {
                if (user) {
                    localStorage.setItem('user', JSON.stringify(user));
                } else {
                    localStorage.removeItem('user');
                }
            }
            set(user);
        },
        logout: () => {
            if (typeof window !== 'undefined') {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
            }
            set(null);
        }
    };
}

export const user = createAuthStore();
export const currentConversation = writable(null);
