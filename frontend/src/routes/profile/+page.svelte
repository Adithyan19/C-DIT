<script>
    import { onMount } from "svelte";
    import { user } from "$lib/stores.js";
    import { getProfile, updateProfile, changePassword } from "$lib/api.js";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    let profile = { full_name: "", email: "", location: "", role: "" };
    let profileMsg = "";
    let profileErr = "";
    let profileLoading = false;

    let currentPassword = "";
    let newPassword = "";
    let confirmPassword = "";
    let pwMsg = "";
    let pwErr = "";
    let pwLoading = false;

    onMount(async () => {
        try {
            profile = await getProfile();
        } catch (e) {
            profileErr = e.message;
        }
    });

    async function handleUpdateProfile() {
        profileMsg = "";
        profileErr = "";
        profileLoading = true;
        try {
            const updated = await updateProfile({
                full_name: profile.full_name,
                location: profile.location,
            });
            profile = updated;
            user.set(updated);
            profileMsg = "Profile updated successfully";
        } catch (e) {
            profileErr = e.message;
        } finally {
            profileLoading = false;
        }
    }

    async function handleChangePassword() {
        pwMsg = "";
        pwErr = "";
        if (newPassword !== confirmPassword) {
            pwErr = "Passwords do not match";
            return;
        }
        if (newPassword.length < 6) {
            pwErr = "Password must be at least 6 characters";
            return;
        }
        pwLoading = true;
        try {
            await changePassword(currentPassword, newPassword);
            pwMsg = "Password changed successfully";
            currentPassword = "";
            newPassword = "";
            confirmPassword = "";
        } catch (e) {
            pwErr = e.message;
        } finally {
            pwLoading = false;
        }
    }

    function getRoleLabel(role) {
        if (role === "superadmin") return "Super Admin";
        if (role === "mitl") return "Man-in-the-Loop";
        return "Farmer";
    }
</script>

<div class="profile-page">
    <div class="profile-container">
        <h1>Profile</h1>

        <!-- Profile Info -->
        <div class="card section">
            <h2>Personal Information</h2>
            <div class="role-badge">
                <span
                    class="badge {profile.role === 'superadmin'
                        ? 'badge-classified'
                        : profile.role === 'mitl'
                          ? 'badge-classified'
                          : 'badge-pending'}"
                >
                    {getRoleLabel(profile.role)}
                </span>
            </div>

            {#if profileMsg}
                <div class="alert alert-success">{profileMsg}</div>
            {/if}
            {#if profileErr}
                <div class="alert alert-error">{profileErr}</div>
            {/if}

            <form on:submit|preventDefault={handleUpdateProfile}>
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input
                        id="name"
                        type="text"
                        bind:value={profile.full_name}
                    />
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        value={profile.email}
                        disabled
                    />
                </div>
                <div class="form-group">
                    <label for="location">Location</label>
                    <input
                        id="location"
                        type="text"
                        bind:value={profile.location}
                        placeholder="e.g. Wayanad, Idukki, Thrissur"
                    />
                </div>
                <button
                    class="btn btn-primary"
                    type="submit"
                    disabled={profileLoading}
                >
                    {profileLoading ? "Saving..." : "Save Changes"}
                </button>
            </form>
        </div>

        <!-- Change Password -->
        <div class="card section">
            <h2>Change Password</h2>

            {#if pwMsg}
                <div class="alert alert-success">{pwMsg}</div>
            {/if}
            {#if pwErr}
                <div class="alert alert-error">{pwErr}</div>
            {/if}

            <form on:submit|preventDefault={handleChangePassword}>
                <div class="form-group">
                    <label for="current-pw">Current Password</label>
                    <input
                        id="current-pw"
                        type="password"
                        bind:value={currentPassword}
                        required
                    />
                </div>
                <div class="form-group">
                    <label for="new-pw">New Password</label>
                    <input
                        id="new-pw"
                        type="password"
                        bind:value={newPassword}
                        placeholder="Min 6 characters"
                        required
                    />
                </div>
                <div class="form-group">
                    <label for="confirm-pw">Confirm New Password</label>
                    <input
                        id="confirm-pw"
                        type="password"
                        bind:value={confirmPassword}
                        required
                    />
                </div>
                <button
                    class="btn btn-primary"
                    type="submit"
                    disabled={pwLoading}
                >
                    {pwLoading ? "Changing..." : "Change Password"}
                </button>
            </form>
        </div>
    </div>
</div>

<style>
    .profile-page {
        padding: 24px;
        max-width: 600px;
        margin: 0 auto;
    }
    .profile-page h1 {
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
        color: var(--text);
    }
    .role-badge {
        margin-bottom: 16px;
    }
    .profile-container {
        width: 100%;
    }
</style>
