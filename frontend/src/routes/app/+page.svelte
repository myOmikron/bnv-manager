<script lang="ts">
	import type { LayoutData } from "./$types";
	import { ButtonSet, Button, Tile } from "carbon-components-svelte";
	import Email from "carbon-icons-svelte/lib/Email.svelte";
	import Wikis from "carbon-icons-svelte/lib/Wikis.svelte";
	import UserAvatar from "carbon-icons-svelte/lib/UserAvatar.svelte";
	import Group from "carbon-icons-svelte/lib/Group.svelte";
	import GroupPresentation from "carbon-icons-svelte/lib/GroupPresentation.svelte";

	export let data: LayoutData;
</script>

<div class="overview">
	<Tile>
		<h2>Bürgernetz Verwaltung</h2>
		<p class="username">
			{data.account?.username || "(bitte neu anmelden)"}
		</p>

		<ButtonSet stacked class="buttonSet">
			{#if data.account?.isUser}
				<Button icon={Email} kind="ghost" href="/app/email">
					E-Mail
				</Button>
				<Button icon={Wikis} kind="ghost" href="/app/webspace">
					{data.account?.isClubAdmin ? "Benutzer-Webspace" : "Webspace"}
				</Button>
			{/if}
			{#if data.account?.isClubAdmin}
				<Button icon={Group} kind="ghost" href="/app/club/users">
					Benutzerverwaltung
				</Button>
				<Button icon={Wikis} kind="ghost" href="/app/club/webspace">
					{data.account?.isUser ? "Vereins-Webspace" : "Webspace"}
				</Button>
			{/if}
			{#if data.account?.isAdmin}
				<Button icon={GroupPresentation} kind="ghost" href="/app/admin">
					Clubverwaltung
				</Button>
			{/if}
			<Button icon={UserAvatar} kind="ghost" href="/app/account">
				Account
			</Button>
		</ButtonSet>
	</Tile>
</div>

<style>
	.overview {
		display: block;
		margin: 1em auto;
		max-width: 500px;
		text-align: center;
	}

	.overview h2 {
		margin-bottom: 1rem;
	}

	.overview .username {
		color: var(--cds-text-02);
		margin-bottom: 1rem;
	}

	.overview :global(.buttonSet),
	.overview :global(.buttonSet > a) {
		width: 100%;
		max-width: unset;
	}

	.overview :global(.buttonSet > a) {
		justify-content: flex-start;
	}

	.overview :global(.buttonSet > a > svg) {
		order: -1;
		margin-right: 16px;
	}
</style>
