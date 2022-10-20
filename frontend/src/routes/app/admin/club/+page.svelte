<script lang="ts">
    import { createClubAdmin, deleteClub, getClubAdmins } from "$lib/admin";
    import { generatePassword, validatePassword } from "$lib/password";
    import type { PageData } from "./$types";

    export let data: PageData;

    import {
        Button,
        DataTable,
        DataTableSkeleton,
        PasswordInput,
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
    import FormDialog from "$lib/components/FormDialog.svelte";
    import PageError from "$lib/components/PageError.svelte";
    import Tiles from "$lib/components/Tiles.svelte";

    let clubId = data.clubId;

    async function handleGeneratePasswordButton(event: MouseEvent) {
        let gen = generatePassword();
        if (gen)
            createData.password = gen;
        createData.passwordVisible = true;
    }

    let rowsPromise: Promise<DataTableRow[]> = getClubAdmins(clubId).then(
        (rows) =>
            rows.map((r) => {
                let row = <DataTableRow>(<any>r);
                row.id = r.username;
                return row;
            })
    );

    let rowsLoaded = false;
    let rowsError: any;
    let rows: DataTableRow[] = [];
    rowsPromise.then((r) => {
        rowsLoaded = true;
        rows = r;
    }).catch((e) => {
        rowsError = e;
    });
    let naProcess = (v: DataTableValue) =>
        typeof v == "undefined" ? "n/a" : v;
    let headers: DataTableHeader[] = [
        { key: "firstname", value: "Vorname", display: naProcess },
        { key: "surname", value: "Nachname", display: naProcess },
        { key: "username", value: "Vereins-ID", display: naProcess },
        { key: "email", value: "E-Mail", display: naProcess },
    ];
    let active = false;
    let selectedRowIds: string[] = [];

    let showDeleteDialog = false;
    let deleteDialogUnlockTime = 5;

    function deleteDialog() {
        showDeleteDialog = true;
        deleteDialogUnlockTime = 5;
        let timer: NodeJS.Timer = setInterval(function () {
            if (deleteDialogUnlockTime == 0 || !showDeleteDialog)
                return clearInterval(timer);
            deleteDialogUnlockTime--;
        }, 1000);
    }

    let showCreateClubAdmin = false;
    let createData = {
        saving: false,
        firstName: "",
        lastName: "",
        password: "",
        passwordVisible: false,
    };
</script>

<Tiles style="max-width: 1200px">
    <Tile>
        <h2>Vereins-Admins</h2>

        {#if rowsError}
            <PageError
                light
                error={rowsError}
                message="Fehler beim Laden der Admins"
            />
        {:else if rowsLoaded}
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
        <Button kind="danger-tertiary" on:click={() => deleteDialog()}>
            Verein Löschen
        </Button>
    </Tile>
</Tiles>

<FormDialog
    bind:open={showCreateClubAdmin}
    name="Vereins-Admin Hinzufügen"
    submitText="Erstellen"
    selectorPrimaryFocus="#db-name"
    work={async () => {
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
            email: undefined,
        });
        rows = rows;
    }}
    bind:state={createData}
    bind:working={createData.saving}
    preventCloseOnClickOutside
>
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
            invalid={validatePassword(createData.password).length > 0}
            invalidText={validatePassword(createData.password).join(".\n")}
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
</FormDialog>

<FormDialog
    bind:open={showDeleteDialog}
    name="Verein Löschen"
    primaryButtonDisabled={deleteDialogUnlockTime > 0}
    submitText={deleteDialogUnlockTime > 0
        ? "Verein Löschen (" + deleteDialogUnlockTime + ")"
        : "Verein Löschen"}
    primaryButtonIcon={TrashCan}
    work={async () => {
        await deleteClub(clubId);
        history.back();
    }}
    workingText="Verein wird gelöscht"
    danger
>
    <div class="wide-p">
        <p>
            <b>Achtung:</b> ein Verein ist nach dem Löschen
            <b>nicht Wiederherstellbar</b>!
        </p>
        <ul>
            <li>der Web-Space des Vereins wird gelöscht</li>
            <li>
                alle dem Verein zugeordneten Benutzer werden gelöscht, inkl.
                E-Mails und Postfächer
            </li>
        </ul>
        <p>
            Diese Aktion kann nicht abgebrochen werden, sobald sie angefangen
            wurde.
        </p>
    </div>
</FormDialog>

<style>
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

    .wide-p p,
    .wide-p ul,
    .wide-p li {
        margin: 1em 0;
        list-style: disc;
    }

    .wide-p li {
        margin-left: 1em;
    }
</style>
