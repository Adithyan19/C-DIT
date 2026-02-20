<script>
    import { onMount } from "svelte";
    import { page } from "$app/state";
    import { user } from "$lib/stores.js";
    import { goto } from "$app/navigation";
    import { getPendingDetail, classifyDisease } from "$lib/api.js";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    let disease = $state(null);
    let loading = $state(true);
    let error = $state("");

    let diseaseName = $state("");
    let solution = $state("");
    let region = $state("");
    let submitting = $state(false);
    let successMsg = $state("");

    $effect(() => {
        const id = page.params.id;
        if (id) loadDisease(id);
    });

    async function loadDisease(id) {
        if (!currentUser || currentUser.role !== "mitl") {
            goto("/login");
            return;
        }
        loading = true;
        try {
            disease = await getPendingDetail(id);
            if (disease.disease_name) diseaseName = disease.disease_name;
            if (disease.solution) solution = disease.solution;
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    async function handleClassify() {
        if (!diseaseName.trim() || !solution.trim()) {
            error = "Disease name and solution are required";
            return;
        }
        submitting = true;
        error = "";
        try {
            await classifyDisease(disease.id, {
                disease_name: diseaseName,
                solution: solution,
                region: region || null,
            });
            successMsg =
                "Disease classified successfully. It has been added to the knowledge base.";
        } catch (e) {
            error = e.message;
        } finally {
            submitting = false;
        }
    }
</script>

<div class="classify-page">
    <a href="/dashboard" class="back-link">Back to Dashboard</a>

    {#if loading}
        <p class="loading-text">Loading...</p>
    {:else if disease}
        <h1>Classify Disease</h1>

        {#if successMsg}
            <div class="alert alert-success">{successMsg}</div>
            <a
                href="/dashboard"
                class="btn btn-primary"
                style="margin-top: 12px;">Return to Dashboard</a
            >
        {:else}
            <!-- Disease Details -->
            <div class="card section">
                <h2>Reported Information</h2>

                {#if disease.image_url}
                    <div class="disease-image-full">
                        <img src={disease.image_url} alt="Disease" />
                    </div>
                {/if}

                <div class="detail-row">
                    <span class="detail-label">Symptoms:</span>
                    <span>{disease.text_symptoms || "None provided"}</span>
                </div>
                {#if disease.location_lat}
                    <div class="detail-row">
                        <span class="detail-label">Location:</span>
                        <span
                            >{disease.location_lat.toFixed(4)}, {disease.location_lng.toFixed(
                                4,
                            )}</span
                        >
                    </div>
                {/if}
                <div class="detail-row">
                    <span class="detail-label">Reported:</span>
                    <span>{new Date(disease.created_at).toLocaleString()}</span>
                </div>
            </div>

            <!-- Classification Form -->
            <div class="card section">
                <h2>Classification</h2>

                {#if error}
                    <div class="alert alert-error">{error}</div>
                {/if}

                <form
                    onsubmit={(e) => {
                        e.preventDefault();
                        handleClassify();
                    }}
                >
                    <div class="form-group">
                        <label for="disease-name">Disease Name *</label>
                        <input
                            id="disease-name"
                            type="text"
                            bind:value={diseaseName}
                            placeholder="e.g. Late Blight"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label for="solution">Solution / Treatment *</label>
                        <textarea
                            id="solution"
                            bind:value={solution}
                            rows="5"
                            placeholder="Describe the recommended treatment or solution..."
                            required
                        ></textarea>
                    </div>
                    <div class="form-group">
                        <label for="region">Region (optional)</label>
                        <input
                            id="region"
                            type="text"
                            bind:value={region}
                            placeholder="e.g. South Asia, Tropical"
                        />
                    </div>
                    <button
                        class="btn btn-primary btn-block"
                        type="submit"
                        disabled={submitting}
                    >
                        {submitting
                            ? "Classifying..."
                            : "Classify and Add to Knowledge Base"}
                    </button>
                </form>
            </div>
        {/if}
    {:else}
        <div class="alert alert-error">{error || "Disease not found"}</div>
    {/if}
</div>

<style>
    .classify-page {
        padding: 24px;
        max-width: 700px;
        margin: 0 auto;
    }
    .back-link {
        display: inline-block;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: var(--primary);
    }
    .classify-page h1 {
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
    .disease-image-full {
        margin-bottom: 16px;
    }
    .disease-image-full img {
        max-width: 100%;
        max-height: 400px;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
    }
    .detail-row {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .detail-label {
        font-weight: 600;
        color: var(--text);
        min-width: 100px;
    }
    .loading-text {
        text-align: center;
        color: var(--text-light);
        padding: 40px;
    }
    textarea {
        resize: vertical;
    }
</style>
