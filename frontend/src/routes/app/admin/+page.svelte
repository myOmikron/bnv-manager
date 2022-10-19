<script lang="ts">
    import { createClubAdmin } from "$lib/admin";
    import type { ClubAdminResponse } from "$lib/admin";

    import {
        Button,
        DataTable,
        DataTableSkeleton,
        Modal,
        PasswordInput,
        ProgressBar,
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
    } from "carbon-components-svelte/types/DataTable/DataTable.svelte";

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

    let rowsPromise: Promise<DataTableRow[]> = new Promise((resolve) =>
        setTimeout(
            () =>
                resolve([
                    {
                        id: "u0",
                        firstname: "Alice",
                        surname: "Mustermann",
                        username: "max.mustermann",
                        email: "max.mustermann@pfaffenhofen.de",
                    },
                    {
                        id: "u1",
                        firstname: "Bob",
                        surname: "Mustermann",
                        username: "max.mustermann",
                        email: "max.mustermann@pfaffenhofen.de",
                    },
                    {
                        id: "u2",
                        firstname: "Max",
                        surname: "Mustermann",
                        username: "max.mustermann",
                        email: "max.mustermann@pfaffenhofen.de",
                    },
                ]),
            500
        )
    );

    let clubId = "testclub";
    let rowsLoaded = false;
    let rows: DataTableRow[] = [];
    rowsPromise.then((r) => {
        rowsLoaded = true;
        rows = r;
    });
    let headers: DataTableHeader[] = [
        { key: "firstname", value: "Vorname" },
        { key: "surname", value: "Nachname" },
        { key: "username", value: "Vereins-ID" },
        { key: "email", value: "E-Mail" },
    ];
    let active = false;
    let selectedRowIds: string[] = [];

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
                firstname: res.username,
                surname: createData.firstName,
                username: createData.lastName,
                email: "",
            });

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
        <h2>Verein-Admins</h2>

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
                            Verein-Admin Hinzufügen
                        </Button>
                    </ToolbarContent>
                </Toolbar>
            </DataTable>
        {:else}
            <DataTableSkeleton {headers} showHeader={false} />
        {/if}
    </Tile>
</div>

<Modal
    open={showCreateClubAdmin}
    modalHeading="Verein-Admin Hinzufügen"
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
    <form>
        <TextInput
            light
            labelText="Vorname"
            bind:value={createData.firstName}
            disabled={createData.saving}
            required
            invalid={createData.error.length > 0}
            invalidText={createData.error}
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
                kind="danger-ghost"
                tooltipAlignment="end"
                tooltipPosition="top"
                iconDescription="Zufällig Generieren"
            />
        </div>
    </form>

    {#if createData.saving}
        <ProgressBar helperText="Saving..." />
    {/if}
</Modal>

<style>
    #page {
        max-width: 1200px;
        margin: 1em auto;
    }

    .gen-password {
        display: flex;
        align-items: flex-start;
    }

    .gen-password > :global(:nth-child(2)) {
        margin-top: 16px;
    }

    .gen-password :global(.bx--form-requirement) {
        white-space: pre-wrap;
    }
</style>
