<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { user } from "$lib/stores.js";

    let currentUser;
    user.subscribe((v) => (currentUser = v));

    onMount(() => {
        if (currentUser) {
            if (currentUser.role === "superadmin") {
                goto("/admin");
            } else if (currentUser.role === "mitl") {
                goto("/dashboard");
            } else {
                goto("/chat");
            }
        } else {
            goto("/login");
        }
    });
</script>

<div class="auth-page">
    <p>Redirecting...</p>
</div>
