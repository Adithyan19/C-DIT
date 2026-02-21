<script>
    import { signup } from "$lib/api.js";
    import { user } from "$lib/stores.js";
    import { goto } from "$app/navigation";

    let full_name = "";
    let email = "";
    let password = "";
    let confirmPassword = "";
    let error = "";
    let loading = false;

    async function handleSignup() {
        error = "";
        if (password !== confirmPassword) {
            error = "Passwords do not match";
            return;
        }
        if (password.length < 6) {
            error = "Password must be at least 6 characters";
            return;
        }
        loading = true;
        try {
            const data = await signup(email, password, full_name);
            user.set(data.user);
            goto("/chat");
        } catch (err) {
            error = err.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="auth-page">
    <div class="card auth-card">
        <h1>Create Account</h1>
        <p class="subtitle">Join FarmBot to get crop disease help</p>

        {#if error}
            <div class="alert alert-error">{error}</div>
        {/if}

        <form on:submit|preventDefault={handleSignup}>
            <div class="form-group">
                <label for="name">Full Name</label>
                <input
                    id="name"
                    type="text"
                    bind:value={full_name}
                    placeholder="Your full name"
                    required
                />
            </div>
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
                    placeholder="Min 6 characters"
                    required
                />
            </div>
            <div class="form-group">
                <label for="confirm">Confirm Password</label>
                <input
                    id="confirm"
                    type="password"
                    bind:value={confirmPassword}
                    placeholder="Repeat password"
                    required
                />
            </div>
            <button
                class="btn btn-primary btn-block"
                type="submit"
                disabled={loading}
            >
                {loading ? "Creating account..." : "Sign Up"}
            </button>
        </form>

        <p
            style="text-align: center; margin-top: 20px; font-size: 0.9rem; color: var(--text-secondary);"
        >
            Already have an account? <a href="/login">Sign In</a>
        </p>
    </div>
</div>
