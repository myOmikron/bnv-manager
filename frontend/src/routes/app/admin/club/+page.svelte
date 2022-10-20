<script lang="ts">
	import { deleteClub } from "$lib/admin";
	import type { PageData } from "./$types";

	export let data: PageData;

	import { Button, Tile } from "carbon-components-svelte";
	import TrashCan from "carbon-icons-svelte/lib/TrashCan.svelte";
	import FormDialog from "$lib/components/FormDialog.svelte";
	import Tiles from "$lib/components/Tiles.svelte";
	import ClubAdminList from "./ClubAdminList.svelte";

	let clubId = data.clubId;

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
</script>

<Tiles style="max-width: 1200px">
	<ClubAdminList {clubId} />

	<Tile>
		<Button kind="danger-tertiary" on:click={() => deleteDialog()}>
			Verein Löschen
		</Button>
	</Tile>
</Tiles>

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
			<li>der Webspace des Vereins wird gelöscht</li>
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
