<script lang="ts">

    import {createClubAdmin} from '$lib/admin';
    import type {ClubAdminResponse} from '$lib/admin';

    async function handleGeneratePasswordButton(event: PointerEvent) {
        // TODO
        console.log("generate password button");
        alert("not implemented yet");
    }

    function showSuccessPopUp(message: string) {
        // TODO: Build something like a toast or something
        alert(message);
    }

    function showErrorPopUp(message: string) {
        // TODO: Build something like a toast or something
        alert(message);
    }

    async function spinLoadingButton<T>(promise: Promise<T>): Promise<T> {
        // TODO
        console.log("password button: start loading");
        let res = await promise;
        console.log("password button: stop loading");
        return res;
    }

    async function handleCreateClubAdmin(event: SubmitEvent) {
        let form = <HTMLFormElement>event.target;
        form.disabled = true;
        try {
            let data = new FormData(form);
            let res: ClubAdminResponse = await spinLoadingButton(createClubAdmin(
                data.get("firstname").toString(),
                data.get("surname").toString(),
                data.get("password").toString(),
                data.get("club_id").toString()
            ));
            if (res.success) {
                showSuccessPopUp(`Nutzer ${res.username} wurde erstellt!`);
            } else {
                showErrorPopUp(`Nutzer wurde nicht angelegt: ${res.error}!`);
            }
        } finally {
            form.disabled = false;
        }
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
                <input name="club_id" type="text" />
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
