<script lang="ts">
	import type { LayoutData } from "./$types";
	import { ButtonSet, Button, Tile } from "carbon-components-svelte";
	import Email from "carbon-icons-svelte/lib/Email.svelte";
	import Wikis from "carbon-icons-svelte/lib/Wikis.svelte";
	import UserAvatar from "carbon-icons-svelte/lib/UserAvatar.svelte";
	import Group from "carbon-icons-svelte/lib/Group.svelte";
	import GroupPresentation from "carbon-icons-svelte/lib/GroupPresentation.svelte";
	import Tiles from "$lib/components/Tiles.svelte";

	export let data: LayoutData;
</script>

<Tiles>
	<Tile>
		<h2>Bürgernetz Verwaltung</h2>
		<p class="username">
			{data.account?.username || "(bitte neu anmelden)"}
		</p>

		<div class="buttons">
			<ButtonSet stacked class="buttonSet">
				{#if data.account?.isUser}
					<Button icon={Email} kind="ghost" href="/app/email">
						E-Mail
					</Button>
					<Button icon={Wikis} kind="ghost" href="/app/webspace">
						{data.account?.isClubAdmin
							? "Benutzer-Webspace"
							: "Webspace"}
					</Button>
				{/if}
				{#if data.account?.isClubAdmin}
					<Button icon={Group} kind="ghost" href="/app/club/users">
						Benutzerverwaltung
					</Button>
					<Button icon={Wikis} kind="ghost" href="/app/club/webspace">
						{data.account?.isUser ? "Verein-Webspace" : "Webspace"}
					</Button>
				{/if}
				{#if data.account?.isAdmin}
					<Button
						icon={GroupPresentation}
						kind="ghost"
						href="/app/admin"
					>
						Vereinsverwaltung
					</Button>
				{/if}
				<Button icon={UserAvatar} kind="ghost" href="/app/account">
					Account
				</Button>
			</ButtonSet>
		</div>
	</Tile>
</Tiles>

<style>
	h2, .username {
		text-align: center;
	}

	.username {
		color: var(--cds-text-02);
		margin-bottom: 1rem;
	}

	.buttons :global(.buttonSet),
	.buttons :global(.buttonSet > a) {
		width: 100%;
		max-width: unset;
	}

	.buttons :global(.buttonSet > a) {
		justify-content: flex-start;
	}

	.buttons :global(.buttonSet > a > svg) {
		order: -1;
		margin-right: 16px;
	}
</style>
