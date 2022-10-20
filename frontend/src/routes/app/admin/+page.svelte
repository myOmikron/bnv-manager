<script lang="ts">
	import { goto } from "$app/navigation";
	import { getClubs, type Club, createClub } from "$lib/admin";
    import FormDialog from "$lib/components/FormDialog.svelte";
    import PageError from "$lib/components/PageError.svelte";
	import {
		ClickableTile,
		SkeletonText,
		TextInput,
	} from "carbon-components-svelte";
	import Add from "carbon-icons-svelte/lib/Add.svelte";

	let clubsPromise: Promise<Club[]> = getClubs();
	let localClubs: Club[] = [];

	let showCreateDialog = false;
	let createData = {
		saving: false,
		name: "",
		id: "",
	};
</script>

<div id="page">
	{#await clubsPromise}
		<div class="clubs">
			<SkeletonText />
		</div>
	{:then clubs}
		{#if clubs.length == 0}
			<p class="empty">Noch kein Verein angelegt.</p>
		{/if}
		<div class="clubs">
			{#each clubs.concat(localClubs).sort((a, b) => a.name.localeCompare(b.name)) as club}
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
	{:catch error}
		<PageError
			message="Fehler bei Vereinsauflistung"
			error={error}
		/>
	{/await}
</div>

<FormDialog
	name="Verein Erstellen"
	bind:open={showCreateDialog}
	bind:state={createData}
	bind:working={createData.saving}
	preventCloseOnClickOutside
	work={async () => {
		let club = await createClub(createData.id, createData.name);
		localClubs.push(club);
		localClubs = localClubs;
	}}
>
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
		labelText="Verein-Name"
		bind:value={createData.name}
		disabled={createData.saving}
		required
	/>
</FormDialog>

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
