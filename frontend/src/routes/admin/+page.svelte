<script>
    import { onMount } from "svelte";
    import { user } from "$lib/stores.js";
    import { goto } from "$app/navigation";
    import {
        getAdminStats,
        listAllUsers,
        createMitlAccount,
    } from "$lib/api.js";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    let stats = { total_users: 0, total_farmers: 0, total_mitl: 0 };
    let users = [];
    let loading = true;

    // Create MITL form
    let showForm = false;
    let mitlName = "";
    let mitlEmail = "";
    let mitlPassword = "";
    let formError = "";
    let formSuccess = "";
    let formLoading = false;

    onMount(async () => {
        if (!currentUser || currentUser.role !== "superadmin") {
            goto("/login");
            return;
        }
        await loadData();
    });

    async function loadData() {
        loading = true;
        try {
            stats = await getAdminStats();
            users = await listAllUsers();
        } catch (e) {
            console.error("Admin load error", e);
        } finally {
            loading = false;
        }
    }

    async function handleCreateMitl() {
        formError = "";
        formSuccess = "";
        if (!mitlName.trim() || !mitlEmail.trim() || !mitlPassword.trim()) {
            formError = "All fields are required";
            return;
        }
        if (mitlPassword.length < 6) {
            formError = "Password must be at least 6 characters";
            return;
        }
        formLoading = true;
        try {
            await createMitlAccount(mitlEmail, mitlPassword, mitlName);
            formSuccess = "Man-in-the-Loop account created successfully";
            mitlName = "";
            mitlEmail = "";
            mitlPassword = "";
            await loadData();
        } catch (e) {
            formError = e.message;
        } finally {
            formLoading = false;
        }
    }

    function getRoleLabel(role) {
        if (role === "superadmin") return "Super Admin";
        if (role === "mitl") return "MITL";
        return "Farmer";
    }

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString([], {
            month: "short",
            day: "numeric",
            year: "numeric",
        });
    }
</script>

<div class="admin-page">
    <h1>Admin Panel</h1>

    {#if loading}
        <p class="loading-text">Loading...</p>
    {:else}
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats.total_users}</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.total_farmers}</div>
                <div class="stat-label">Farmers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.total_mitl}</div>
                <div class="stat-label">MITL Reviewers</div>
            </div>
        </div>

        <!-- Create MITL Account -->
        <div class="card section">
            <div class="section-header">
                <h2>Create Man-in-the-Loop Account</h2>
                <button
                    class="btn btn-sm btn-primary"
                    on:click={() => (showForm = !showForm)}
                >
                    {showForm ? "Cancel" : "+ New Account"}
                </button>
            </div>

            {#if showForm}
                {#if formError}
                    <div class="alert alert-error">{formError}</div>
                {/if}
                {#if formSuccess}
                    <div class="alert alert-success">{formSuccess}</div>
                {/if}

                <form on:submit|preventDefault={handleCreateMitl}>
                    <div class="form-group">
                        <label for="mitl-name">Full Name</label>
                        <input
                            id="mitl-name"
                            type="text"
                            bind:value={mitlName}
                            placeholder="Reviewer name"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label for="mitl-email">Email</label>
                        <input
                            id="mitl-email"
                            type="email"
                            bind:value={mitlEmail}
                            placeholder="reviewer@email.com"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label for="mitl-pw">Password</label>
                        <input
                            id="mitl-pw"
                            type="password"
                            bind:value={mitlPassword}
                            placeholder="Min 6 characters"
                            required
                        />
                    </div>
                    <button
                        class="btn btn-primary"
                        type="submit"
                        disabled={formLoading}
                    >
                        {formLoading ? "Creating..." : "Create Account"}
                    </button>
                </form>
            {/if}
        </div>

        <!-- User List -->
        <div class="card section">
            <h2>All Users ({users.length})</h2>
            <div class="user-list">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each users as u}
                            <tr>
                                <td>{u.full_name}</td>
                                <td>{u.email}</td>
                                <td>
                                    <span
                                        class="badge {u.role === 'farmer'
                                            ? 'badge-pending'
                                            : 'badge-classified'}"
                                    >
                                        {getRoleLabel(u.role)}
                                    </span>
                                </td>
                                <td>{formatDate(u.created_at)}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>

<style>
    .admin-page {
        padding: 24px;
        max-width: 900px;
        margin: 0 auto;
    }
    .admin-page h1 {
        font-size: 1.5rem;
        color: var(--primary-dark);
        margin-bottom: 24px;
    }
    .section {
        margin-bottom: 24px;
    }
    .section h2 {
        font-size: 1.1rem;
        margin-bottom: 16px;
    }
    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .section-header h2 {
        margin-bottom: 0;
    }
    .user-list {
        overflow-x: auto;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th,
    td {
        text-align: left;
        padding: 10px 12px;
        border-bottom: 1px solid var(--border);
        font-size: 0.9rem;
    }
    th {
        font-weight: 600;
        color: var(--text);
        background: #f5f5f0;
    }
    td {
        color: var(--text-secondary);
    }
    .loading-text {
        text-align: center;
        color: var(--text-light);
        padding: 40px;
    }
</style>
