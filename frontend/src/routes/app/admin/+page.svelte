<script lang="ts">
	import { goto } from "$app/navigation";
	import { getClubs, type Club, createClub } from "$lib/admin";
	import {
		Button,
		ButtonSet,
		ClickableTile,
		InlineLoading,
		Modal,
		SkeletonPlaceholder,
		SkeletonText,
		TextInput,
	} from "carbon-components-svelte";
	import Add from "carbon-icons-svelte/lib/Add.svelte";

	let clubs: Club[];
	let clubsLoaded = false;

	getClubs().then((c) => {
		clubs = c;
		clubsLoaded = true;
	});

	let showCreateDialog = false;
	let createData = {
		saving: false,
		name: "",
		id: "",
		error: "",
	};

	function initCreateDialog() {
		createData.saving = false;
		createData.name = "";
		createData.id = "";
		createData.error = "";
	}

	async function createClubImpl() {
		createData.saving = true;
		try
		{
			let form = <HTMLFormElement>document.getElementById("createForm");
			if (!form.reportValidity())
				return;

			let club = await createClub(createData.id, createData.name);
			clubs.push(club);
			clubs = clubs;

			showCreateDialog = false;
		}
		catch (e)
		{
			createData.error = e + "";
		}
		finally
		{
			createData.saving = false;
		}
	}
</script>

<div id="page">
	{#if clubsLoaded}
		{#if clubs.length == 0}
			<p class="empty">Noch keine Clubs angelegt.</p>
		{/if}
		<div class="clubs">
			{#each clubs as club}
				<ClickableTile
					on:click={(e) => {
						e.preventDefault();
						goto(
							"/app/admin/club?club=" +
								encodeURIComponent(club.id) +
								"&name=" +
								encodeURIComponent(club.name)
						);
					}}
				>
					{club.name || club.id}
				</ClickableTile>
			{/each}
			<ClickableTile
				light
				title="Neuen Verein erstellen"
				on:click={() => (showCreateDialog = true)}
			>
				<Add size="32" />
			</ClickableTile>
		</div>
	{:else}
		<div class="clubs">
			<SkeletonText />
		</div>
	{/if}
</div>

<Modal
	open={showCreateDialog}
	modalHeading="Verein Erstellen"
	preventCloseOnClickOutside
	primaryButtonText="Verein Erstellen"
	secondaryButtonText="Abbrechen"
	on:click:button--secondary={() =>
		createData.saving ? null : (showCreateDialog = false)}
	on:open={initCreateDialog}
	on:close={() => (showCreateDialog = false)}
	on:submit={createClubImpl}
>
	{#if createData.saving}
		<InlineLoading status="active" description="Saving..." />
	{:else if createData.error.length > 0}
		<InlineLoading status="error" description={createData.error} />
	{/if}

	<form id="createForm">
		<TextInput
			light
			labelText="LDAP ID"
			pattern="^[a-zA-Z]+$"
			bind:value={createData.id}
			disabled={createData.saving}
			required
		/>
		<TextInput
			light
			labelText="Vereins-Name"
			bind:value={createData.name}
			disabled={createData.saving}
			required
		/>
	</form>
</Modal>

<style>
	.clubs {
		display: flex;
		margin: 2em auto;
		max-width: 1000px;
		flex-wrap: wrap;
		gap: 1em;
		padding: 0 1em;
	}
</style>
