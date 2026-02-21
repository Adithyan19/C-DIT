<script>
    import { onMount } from "svelte";
    import { user } from "$lib/stores.js";
    import { goto } from "$app/navigation";
    import {
        getMitlStats,
        getPendingDiseases,
        getClassifiedDiseases,
    } from "$lib/api.js";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    let stats = {
        pending_count: 0,
        classified_count: 0,
        total_farmers: 0,
        total_conversations: 0,
    };
    let pending = [];
    let classified = [];
    let activeTab = "pending";
    let loading = true;

    onMount(async () => {
        if (!currentUser || currentUser.role !== "mitl") {
            goto("/login");
            return;
        }
        try {
            stats = await getMitlStats();
            pending = await getPendingDiseases();
            classified = await getClassifiedDiseases();
        } catch (e) {
            console.error("Dashboard load error", e);
        } finally {
            loading = false;
        }
    });

    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString([], {
            month: "short",
            day: "numeric",
            year: "numeric",
        });
    }
</script>

<div class="dashboard-page">
    <h1>Disease Review Dashboard</h1>

    <!-- Stats -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats.pending_count}</div>
            <div class="stat-label">Pending Review</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.classified_count}</div>
            <div class="stat-label">Classified</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.total_farmers}</div>
            <div class="stat-label">Farmers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.total_conversations}</div>
            <div class="stat-label">Conversations</div>
        </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
        <button
            class="tab"
            class:active={activeTab === "pending"}
            on:click={() => (activeTab = "pending")}
        >
            Pending ({pending.length})
        </button>
        <button
            class="tab"
            class:active={activeTab === "classified"}
            on:click={() => (activeTab = "classified")}
        >
            Classified ({classified.length})
        </button>
    </div>

    <!-- Disease List -->
    {#if loading}
        <p class="loading-text">Loading...</p>
    {:else}
        <div class="disease-list">
            {#each activeTab === "pending" ? pending : classified as disease}
                <a href="/dashboard/{disease.id}" class="disease-card card">
                    <div class="disease-card-content">
                        {#if disease.image_url}
                            <div class="disease-thumb">
                                <img src={disease.image_url} alt="Disease" />
                            </div>
                        {:else}
                            <div class="disease-thumb no-image">No Image</div>
                        {/if}
                        <div class="disease-info">
                            <div class="disease-header">
                                <span
                                    class="badge {disease.status === 'pending'
                                        ? 'badge-pending'
                                        : 'badge-classified'}"
                                >
                                    {disease.status}
                                </span>
                                <span class="disease-date"
                                    >{formatDate(disease.created_at)}</span
                                >
                            </div>
                            {#if disease.disease_name}
                                <h3>{disease.disease_name}</h3>
                            {/if}
                            <p class="disease-symptoms">
                                {disease.text_symptoms || "No text symptoms"}
                            </p>
                            {#if disease.location_lat}
                                <p class="disease-location">
                                    Location: {disease.location_lat.toFixed(2)}, {disease.location_lng.toFixed(
                                        2,
                                    )}
                                </p>
                            {/if}
                        </div>
                    </div>
                </a>
            {:else}
                <p class="empty-text">No {activeTab} diseases.</p>
            {/each}
        </div>
    {/if}
</div>

<style>
    .dashboard-page {
        padding: 24px;
        max-width: 900px;
        margin: 0 auto;
    }
    .dashboard-page h1 {
        font-size: 1.5rem;
        color: var(--primary-dark);
        margin-bottom: 24px;
    }
    .tabs {
        display: flex;
        gap: 0;
        margin-bottom: 20px;
        border-bottom: 2px solid var(--border);
    }
    .tab {
        padding: 10px 20px;
        background: none;
        border: none;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-secondary);
        cursor: pointer;
        transition:
            color 0.2s,
            border-color 0.2s;
    }
    .tab.active {
        color: var(--primary);
        border-bottom-color: var(--primary);
    }
    .disease-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .disease-card {
        text-decoration: none;
        color: inherit;
        transition: box-shadow 0.2s;
        display: block;
    }
    .disease-card:hover {
        box-shadow: var(--shadow-md);
        text-decoration: none;
    }
    .disease-card-content {
        display: flex;
        gap: 16px;
    }
    .disease-thumb {
        width: 80px;
        height: 80px;
        border-radius: var(--radius);
        overflow: hidden;
        flex-shrink: 0;
    }
    .disease-thumb img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .disease-thumb.no-image {
        background: #f0f0ea;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        color: var(--text-light);
    }
    .disease-info {
        flex: 1;
        min-width: 0;
    }
    .disease-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }
    .disease-date {
        font-size: 0.8rem;
        color: var(--text-light);
    }
    .disease-info h3 {
        font-size: 1rem;
        margin-bottom: 4px;
    }
    .disease-symptoms {
        font-size: 0.85rem;
        color: var(--text-secondary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .disease-location {
        font-size: 0.8rem;
        color: var(--text-light);
        margin-top: 4px;
    }
    .loading-text,
    .empty-text {
        text-align: center;
        color: var(--text-light);
        padding: 40px;
    }
</style>
