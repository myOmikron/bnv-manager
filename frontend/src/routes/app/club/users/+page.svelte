<script lang="ts">
	import PageError from "$lib/components/PageError.svelte";
	import Tiles from "$lib/components/Tiles.svelte";
	import {
		Button,
		DataTable,
		DataTableSkeleton,
		TextInput,
		Tile,
		Toolbar,
		ToolbarBatchActions,
		ToolbarContent,
		ToolbarSearch,
	} from "carbon-components-svelte";
	import type {
		DataTableHeader,
		DataTableRow,
		DataTableValue,
	} from "carbon-components-svelte/types/DataTable/DataTable.svelte";
	import TrashCan from "carbon-icons-svelte/lib/TrashCan.svelte";
	import Password from "carbon-icons-svelte/lib/Password.svelte";
	import type { PageData } from "./$types";
	import FormDialog from "$lib/components/FormDialog.svelte";
	import GenPasswordField from "$lib/components/GenPasswordField.svelte";

	export let data: PageData;

	let rowsPromise: Promise<DataTableRow[]> = new Promise((resolve) =>
		setTimeout(
			() =>
				resolve([
					{
						id: "max.mustermann",
						username: "max.mustermann",
						firstname: "Max",
						surname: "Mustermann",
						email: "max.mustermann@pfaffenhofen.de",
					},
				]),
			2000
		)
	);

	let rowsLoaded = false;
	let rowsError: any;
	let rows: DataTableRow[] = [];
	rowsPromise
		.then((r) => {
			rowsLoaded = true;
			rows = r;
		})
		.catch((e) => {
			rowsError = e;
		});
	let naProcess = (v: DataTableValue) =>
		typeof v == "undefined" ? "n/a" : v;
	let headers: DataTableHeader[] = [
		{ key: "firstname", value: "Vorname", display: naProcess },
		{ key: "surname", value: "Nachname", display: naProcess },
		{ key: "username", value: "Verein-ID", display: naProcess },
		{ key: "email", value: "E-Mail", display: naProcess },
	];
	let active = false;
	let selectedRowIds: string[] = [];

	let showCreateUser = false;
	let createData = {
		saving: false,
		firstName: "",
		lastName: "",
		password: "",
		email: "",
		passwordVisible: false,
	};

	let resetPasswordId = "";
	let changeData = {
		saving: false,
		password: "",
	};
</script>

<Tiles style="max-width: 1200px">
	<Tile>
		<h2>Vereinsmitglieder</h2>

		{#if rowsError}
			<PageError
				light
				error={rowsError}
				message="Fehler beim Laden der Mitglieder"
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
								active = false;
							}}
						>
							Löschen
						</Button>
						<Button
							icon={Password}
							disabled={selectedRowIds.length !== 1}
							on:click={() => {
								if (selectedRowIds.length !== 1)
									throw new Error("unexpected selection");
								resetPasswordId = selectedRowIds[0];
								selectedRowIds = [];
								active = false;
							}}
						>
							Passwort Zurücksetzen
						</Button>
					</ToolbarBatchActions>
					<ToolbarContent>
						<ToolbarSearch persistent shouldFilterRows />
						<Button on:click={() => (showCreateUser = true)}>
							Mitglied Hinzufügen
						</Button>
					</ToolbarContent>
				</Toolbar>
			</DataTable>
		{:else}
			<DataTableSkeleton {headers} showHeader={false} />
		{/if}
	</Tile>
</Tiles>

<FormDialog
	bind:open={showCreateUser}
	name="Vereinsmitglied Hinzufügen"
	submitText="Erstellen"
	work={async () => {
		let res = await createClubUser(
			createData.firstName,
			createData.lastName,
			createData.email,
			createData.password,
			clubId
		);

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
	<TextInput
		light
		labelText="E-Mail"
		type="email"
		bind:value={createData.email}
		disabled={createData.saving}
		required
	/>

	<GenPasswordField
		light
		labelText="Passwort"
		bind:value={createData.password}
		bind:passwordVisible={createData.passwordVisible}
		disabled={createData.saving}
		required
	/>
</FormDialog>

<FormDialog
	open={resetPasswordId.length > 0}
	name="Passwort für Mitglied zurücksetzen"
	submitText="Zurücksetzen"
	workingText="Ändere Passwort..."
	danger
	bind:working={changeData.saving}
	bind:state={changeData}
	on:close={() => (resetPasswordId = "")}
	work={async () => {
		await changeClubUserPassword(clubId, resetPasswordId, changeData.password);
	}}
>
	<p>
		Passwort zurücksetzen für Benutzer <strong>{resetPasswordId}</strong>
	</p>

	<GenPasswordField
		light
		labelText="Neues Passwort"
		bind:value={changeData.password}
		disabled={changeData.saving}
		required
	/>

	<p>
		Bitte teile dem Mitglied das neue Passwort zeitnah zu, damit sie sich
		wieder einloggen können.
	</p>
</FormDialog>
