<script lang="ts">
    import { createClubAdmin, deleteClub, getClubAdmins } from "$lib/admin";
    import type { ClubAdminResponse } from "$lib/admin";
	import type { PageData } from "./$types";

	export let data: PageData;

    import {
        Button,
        DataTable,
        DataTableSkeleton,
        Modal,
        PasswordInput,
        ProgressBar,
        InlineLoading,
        TextInput,
        Tile,
        Toolbar,
        ToolbarBatchActions,
        ToolbarContent,
        ToolbarSearch,
    } from "carbon-components-svelte";
    import TrashCan from "carbon-icons-svelte/lib/TrashCan.svelte";
    import Renew from "carbon-icons-svelte/lib/Renew.svelte";
    import type {
        DataTableHeader,
        DataTableRow,
        DataTableValue,
    } from "carbon-components-svelte/types/DataTable/DataTable.svelte";

    let clubId = data.clubId;

    const pwdChars =
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_'/.,<>:;[]{}";
    async function handleGeneratePasswordButton(event: MouseEvent) {
        const random = new Uint32Array(16);
        for (let i = 0; i < 10; i++) {
            if (window.Crypto && window.crypto)
                window.crypto.getRandomValues(random);
            else
                for (let n = 0; n < 16; n++)
                    random[n] = Math.floor(Math.random() * pwdChars.length);

            let password = "";
            for (let n = 0; n < 16; n++)
                password += pwdChars[random[n] % pwdChars.length];
            if (validatePasswordImpl(password).length == 0) {
                createData.password = password;
                break;
            }
        }
        createData.passwordVisible = true;
    }

    function validatePassword(event: InputEvent): void {
        let errors = validatePasswordImpl(
            (<HTMLInputElement>event.target).value
        );
        createData.passwordInvalid = errors.length > 0;
        createData.passwordInvalidText = errors.join("\n");
    }

    function validatePasswordImpl(password: string): string[] {
        if (!password.length) return [];
        let ret: string[] = [];
        let hasUpper, hasLower, hasSpecial;
        for (let i = 0; i < password.length; i++) {
            const c = password[i];
            if (c >= "a" && c <= "z") hasLower = true;
            else if (c >= "A" && c <= "Z") hasUpper = true;
            else hasSpecial = true;
        }
        if (password.length < 12)
            ret.push("Passwort muss mindestens 12 Zeichen lang sein");
        if (!hasLower || !hasUpper)
            ret.push("Passwort muss Klein und Großbuchstaben beinhalten");
        if (!hasSpecial)
            ret.push("Passwort muss mindestens ein Sonderzeichen beinhalten");
        return ret;
    }

    let rowsPromise: Promise<DataTableRow[]> = getClubAdmins(clubId)
        .then(rows => rows.map(r => {
            let row = <DataTableRow><any>r;
            row.id = r.username;
            return row;
        }));

    let rowsLoaded = false;
    let rows: DataTableRow[] = [];
    rowsPromise.then((r) => {
        rowsLoaded = true;
        rows = r;
    });
    let naProcess = (v: DataTableValue) => typeof(v) == "undefined" ? "n/a" : v;
    let headers: DataTableHeader[] = [
        { key: "firstname", value: "Vorname", display: naProcess },
        { key: "surname", value: "Nachname", display: naProcess },
        { key: "username", value: "Vereins-ID", display: naProcess },
        { key: "email", value: "E-Mail", display: naProcess },
    ];
    let active = false;
    let selectedRowIds: string[] = [];

    let showDeleteDialog = false;
    let deletingClub = false;
    let deleteError = "";
    let deleteDialogUnlockTime = 5;

    function deleteDialog() {
        showDeleteDialog = true;
        deleteError = "";
        deleteDialogUnlockTime = 5;
        let timer: NodeJS.Timer = setInterval(function() {
            if (deleteDialogUnlockTime == 0 || !showDeleteDialog)
                return clearInterval(timer);
            deleteDialogUnlockTime--;
        }, 1000);
    }

    async function deleteClubConfirmed() {
        deletingClub = true;
        try
        {
            await deleteClub(clubId);
            showDeleteDialog = false;
        }
        catch (e)
        {
            deleteError = e + "";
        }
        finally
        {
            deletingClub = false;
        }
    }

    let showCreateClubAdmin = false;
    let createData = {
        saving: false,
        firstName: "",
        lastName: "",
        password: "",
        passwordInvalid: false,
        passwordInvalidText: "",
        passwordVisible: false,
        error: "",
    };
    function initCreate() {
        createData.saving = false;
        createData.firstName = "";
        createData.lastName = "";
        createData.password = "";
        createData.passwordInvalid = false;
        createData.passwordInvalidText = "";
        createData.passwordVisible = false;
        createData.error = "";
    }

    async function submitCreate() {
        createData.saving = true;
        try {
            let res = await createClubAdmin(
                createData.firstName,
                createData.lastName,
                createData.password,
                clubId
            );
            if (!res.success) throw new Error(res.error || "");

            rows.push({
                id: res.username,
                firstname: createData.firstName,
                surname: createData.lastName,
                username: res.username,
                email: "",
            });
            rows = rows;

            showCreateClubAdmin = false;
        } catch (e) {
            createData.error = e + "";
        } finally {
            createData.saving = false;
        }
    }
</script>

<div id="page">
    <Tile>
        <h2>Vereins-Admins</h2>

        {#if rowsLoaded}
            <DataTable bind:selectedRowIds batchSelection {headers} {rows}>
                <Toolbar>
                    <ToolbarBatchActions
                        bind:active
                        on:cancel={(e) => {
                            e.preventDefault();
                            active = false;
                        }}
                    >
                        <Button
                            icon={TrashCan}
                            disabled={selectedRowIds.length === 0}
                            on:click={() => {
                                rows = rows.filter(
                                    (row) => !selectedRowIds.includes(row.id)
                                );
                                selectedRowIds = [];
                            }}
                        >
                            Delete
                        </Button>
                    </ToolbarBatchActions>
                    <ToolbarContent>
                        <ToolbarSearch />
                        <Button on:click={() => (showCreateClubAdmin = true)}>
                            Vereins-Admin Hinzufügen
                        </Button>
                    </ToolbarContent>
                </Toolbar>
            </DataTable>
        {:else}
            <DataTableSkeleton {headers} showHeader={false} />
        {/if}
    </Tile>

    <Tile>
        <Button
            kind="danger-tertiary"
            on:click={() => deleteDialog()}
        >
            Verein Löschen
        </Button>
    </Tile>
</div>

<Modal
    open={showCreateClubAdmin}
    modalHeading="Vereins-Admin Hinzufügen"
    primaryButtonText="Erstellen"
    secondaryButtonText="Abbrechen"
    selectorPrimaryFocus="#db-name"
    on:click:button--secondary={() =>
        createData.saving ? null : (showCreateClubAdmin = false)}
    on:open={initCreate}
    on:close={() => (showCreateClubAdmin = false)}
    on:submit={submitCreate}
    disabled={createData.saving}
    primaryButtonDisabled={createData.saving}
    preventCloseOnClickOutside
>
    {#if createData.saving}
        <InlineLoading status="active" description="Saving..." />
    {:else if createData.error.length > 0}
        <InlineLoading status="error" description={createData.error} />
    {/if}

    <form>
        <TextInput
            light
            labelText="Vorname"
            bind:value={createData.firstName}
            disabled={createData.saving}
            required
        />
        <TextInput
            light
            labelText="Nachname"
            bind:value={createData.lastName}
            disabled={createData.saving}
            required
        />

        <div class="gen-password">
            <PasswordInput
                light
                labelText="Passwort"
                required
                bind:value={createData.password}
                disabled={createData.saving}
                tooltipAlignment="end"
                tooltipPosition="left"
                invalid={validatePasswordImpl(createData.password).length > 0}
                invalidText={validatePasswordImpl(createData.password).join(
                    ".\n"
                )}
            />
            <!-- TODO: show PasswordInput text with createData.passwordVisible (no API for that yet) -->
            <Button
                icon={Renew}
                on:click={handleGeneratePasswordButton}
                disabled={createData.saving}
                size="field"
                kind="danger-ghost"
                tooltipAlignment="end"
                tooltipPosition="top"
                iconDescription="Zufällig Generieren"
            />
        </div>
    </form>
</Modal>

<Modal
    open={showDeleteDialog}
    modalHeading="Verein Löschen"
    primaryButtonDisabled={deleteDialogUnlockTime > 0 || deletingClub}
    preventCloseOnClickOutside={deletingClub}
    primaryButtonText={
        deleteDialogUnlockTime > 0
            ? "Verein Löschen (" + deleteDialogUnlockTime + ")"
            : "Verein Löschen"}
    primaryButtonIcon={TrashCan}
    secondaryButtonText="Abbrechen"
    on:click:button--secondary={() =>
        deletingClub ? null : (showDeleteDialog = false)}
    on:close={() => (showDeleteDialog = false)}
    on:submit={deleteClubConfirmed}
    danger
>
    <div class="wide-p">
        {#if deletingClub}
            <InlineLoading status="active" description="Verein wird gelöscht..." />
        {:else if deleteError.length > 0}
            <InlineLoading status="error" description={deleteError} />
        {/if}
        <p>
            <b>Achtung:</b> ein Verein ist nach dem Löschen <b>nicht Wiederherstellbar</b>!
        </p>
        <ul>
            <li>der Web-Space des Vereins wird gelöscht</li>
            <li>alle dem Verein zugeordneten Benutzer werden gelöscht, inkl. E-Mails und Postfächer</li>
        </ul>
        <p>
            Diese Aktion kann nicht abgebrochen werden, sobald sie angefangen wurde.
        </p>
    </div>
</Modal>

<style>
    #page {
        max-width: 1200px;
        margin: 1em auto;
    }

    #page > :global(*) {
        margin-bottom: 1em;
    }

    .gen-password {
        display: flex;
        align-items: flex-start;
    }

    .gen-password > :global(:nth-child(2)) {
        margin-top: 24px;
    }

    .gen-password :global(.bx--form-requirement) {
        white-space: pre-wrap;
    }

    .wide-p p, .wide-p ul, .wide-p li {
        margin: 1em 0;
        list-style: disc;
    }

    .wide-p li {
        margin-left: 1em;
    }
</style>
