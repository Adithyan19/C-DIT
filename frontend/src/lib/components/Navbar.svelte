<script>
    import { user } from "$lib/stores.js";
    import { logout } from "$lib/api.js";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    function handleLogout() {
        user.set(null);
        logout();
    }
</script>

<nav class="navbar">
    <a href="/" class="nav-logo">FarmBot</a>
    <div class="nav-links">
        {#if currentUser}
            {#if currentUser.role === "farmer"}
                <a href="/chat">Chat</a>
            {:else if currentUser.role === "mitl"}
                <a href="/dashboard">Dashboard</a>
            {:else if currentUser.role === "superadmin"}
                <a href="/admin">Admin</a>
            {/if}
            <a href="/profile">Profile</a>
            <button class="btn btn-sm" on:click={handleLogout}>Logout</button>
        {/if}
    </div>
</nav>

<style>
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 24px;
        background: var(--surface);
        border-bottom: 2px solid var(--primary);
        height: 56px;
    }
    .nav-logo {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--primary-dark);
        text-decoration: none;
    }
    .nav-links {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .nav-links a {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text);
        text-decoration: none;
    }
    .nav-links a:hover {
        color: var(--primary);
    }
</style>
