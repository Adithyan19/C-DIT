<script>
    import { login } from "$lib/api.js";
    import { user } from "$lib/stores.js";
    import { goto } from "$app/navigation";

    let email = "";
    let password = "";
    let error = "";
    let loading = false;

    async function handleLogin() {
        error = "";
        loading = true;
        try {
            const data = await login(email, password);
            user.set(data.user);
            if (data.user.role === "superadmin") {
                goto("/admin");
            } else if (data.user.role === "mitl") {
                goto("/dashboard");
            } else {
                goto("/chat");
            }
        } catch (err) {
            error = err.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="auth-page">
    <div class="card auth-card">
        <h1>Welcome Back</h1>
        <p class="subtitle">Sign in to FarmBot Disease Assistant</p>

        {#if error}
            <div class="alert alert-error">{error}</div>
        {/if}

        <form on:submit|preventDefault={handleLogin}>
            <div class="form-group">
                <label for="email">Email</label>
                <input
                    id="email"
                    type="email"
                    bind:value={email}
                    placeholder="your@email.com"
                    required
                />
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    placeholder="Enter password"
                    required
                />
            </div>
            <button
                class="btn btn-primary btn-block"
                type="submit"
                disabled={loading}
            >
                {loading ? "Signing in..." : "Sign In"}
            </button>
        </form>

        <p
            style="text-align: center; margin-top: 20px; font-size: 0.9rem; color: var(--text-secondary);"
        >
            Don't have an account? <a href="/signup">Sign Up</a>
        </p>
    </div>
</div>
