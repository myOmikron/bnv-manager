<script lang="ts">

    import { createClubAdmin } from '../../../lib/admin';

    async function handleGeneratePasswordButton(event) {
        // TODO
        console.log("generate password button");
        alert("not implemented yet");
    }

    async function handleCreateClubAdmin(event: SubmitEvent) {
        // TODO
        console.log("handle create club admin submit")
    }
</script>

<div id="page">
    <h2>Admin</h2>

    <div class="clubadmins">
        Coming soon: List of all known clubadmins
        <form method="POST" on:submit|preventDefault={handleCreateClubAdmin}>
            <h3>Add a new club admin</h3>
            <label>
                <span>Vorname</span>
                <input name="firstname" type="text" />
            </label>
            <label>
                <span>Nachname</span>
                <input name="surname" type="text" />
            </label>
            <label>
                <span>Vereins-ID</span>
                <input name="surname" type="text" />
            </label>
            <br/>
            <label>
                <span>Passwort</span>
                <input name="password" type="text" />
                <input on:click={handleGeneratePasswordButton} name="generate" type="button" value="Generieren" />
            </label>
            <br/>
            <input type="submit" value="Anlegen" />
        </form>
    </div>
</div>

<style>
    /* Temporary */
    .clubadmins {
        border: 1px solid black;
    }

    /* Temporary */
    .clubadmins form {
        border: 1px solid grey;
    }
</style>
