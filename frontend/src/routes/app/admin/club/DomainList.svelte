<script lang="ts">
	import FormDialog from "$lib/components/FormDialog.svelte";
	import PageError from "$lib/components/PageError.svelte";
	import {
		Button,
		DataTable,
		DataTableSkeleton,
		Pagination,
		Tile,
		Toolbar,
		ToolbarBatchActions,
		ToolbarContent,
		ToolbarSearch,
	} from "carbon-components-svelte";
	import type {
		DataTableHeader,
		DataTableRow,
	} from "carbon-components-svelte/types/DataTable/DataTable.svelte";
	import TrashCan from "carbon-icons-svelte/lib/TrashCan.svelte";

	export let clubId: string;

	let rowsPromise: Promise<DataTableRow[]> = new Promise((resolve) =>
		setTimeout(
			() =>
				resolve([
					{
						id: "pfaffenhofen.de",
						domain: "pfaffenhofen.de",
						noUsers: 42,
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
	let headers: DataTableHeader[] = [
		{ key: "domain", value: "Domain-Name" },
		{ key: "noUsers", value: "Anzahl Benutzer" },
	];
	let active = false;
	let selectedRowIds: string[] = [];

	let showAddDomain = false;
	let changeData = {
		saving: false,
		selected: undefined,
	};

	let pageSize = 5;
	let page = 1;
	let filteredRowIds: string[] = [];

	let domainSearch = "";
	let availableDomainsLoaded = false;
	let availableDomainsPromise: Promise<DataTableRow[]>;
	let selectedAssociateRowIds: string[] = [];
</script>

<Tile>
	<h2>Domains</h2>
	<p>
		Zugeteilte Domains werden für die E-Mail Konfiguration verwendet. Das
		Erstellen erfolgt über das Mailcow System, hier können die Domains nur
		zugewiesen und gelöscht werden.
	</p>

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
							active = false;
						}}
					>
						Löschen
					</Button>
				</ToolbarBatchActions>
				<ToolbarContent>
					<ToolbarSearch persistent shouldFilterRows />
					<Button on:click={() => (showAddDomain = true)}>
						Domain Verknüpfen
					</Button>
				</ToolbarContent>
			</Toolbar>
		</DataTable>
	{:else}
		<DataTableSkeleton {headers} showHeader={false} />
	{/if}
</Tile>

<FormDialog
	bind:open={showAddDomain}
	name="Domain Verknüpfen"
	bind:state={changeData}
	bind:working={changeData.saving}
	on:open={() => {
		availableDomainsLoaded = false;
		availableDomainsPromise = new Promise((resolve) =>
			setTimeout(() => resolve([{ id: "pfaffenhofen.de" }]), 1000)
		).then((rows) => {
			availableDomainsLoaded = true;
			return rows;
		});
		selectedAssociateRowIds = [];
		domainSearch = "";
	}}
	preventCloseOnClickOutside
	work={async () => {
		if (!selectedAssociateRowIds.length)
			throw new Error("Bitte Auswahl treffen");
		await new Promise((resolve) => setTimeout(resolve, 2000));
	}}
	primaryButtonDisabled={!availableDomainsLoaded}
>
	{#await availableDomainsPromise}
		<DataTableSkeleton
			zebra
			headers={[{ key: "id", value: "Domain" }]}
			showHeader={false}
			showToolbar={false}
			size="short"
		/>

		<Pagination
			bind:pageSize
			bind:page
			totalItems={filteredRowIds.length}
			pageSizeInputDisabled
		/>
	{:then availableDomains}
		<DataTable
			size="short"
			bind:selectedRowIds={selectedAssociateRowIds}
			batchSelection
			zebra
			headers={[{ key: "id", value: "Domain" }]}
			rows={availableDomains}
			{pageSize}
			{page}
		>
			<Toolbar>
				<ToolbarContent>
					<ToolbarSearch
						bind:value={domainSearch}
						persistent
						shouldFilterRows
						bind:filteredRowIds
					/>
				</ToolbarContent>
			</Toolbar>
		</DataTable>

		<Pagination
			bind:pageSize
			bind:page
			totalItems={filteredRowIds.length}
			pageSizeInputDisabled
		/>
	{:catch}
		<p class="error">Failed to list available domains.</p>
	{/await}
</FormDialog>
