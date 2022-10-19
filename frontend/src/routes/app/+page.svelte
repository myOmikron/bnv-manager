<script lang="ts">
	import type { LayoutData } from "./$types";
	import { ButtonSet, Button, Tile } from "carbon-components-svelte";
	import Email from "carbon-icons-svelte/lib/Email.svelte";
	import Wikis from "carbon-icons-svelte/lib/Wikis.svelte";
	import User from "carbon-icons-svelte/lib/User.svelte";

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
				<Button icon={Email} kind="ghost" href="/app/email"
					>E-Mail</Button
				>
				<Button icon={Wikis} kind="ghost" href="/app/webspace"
					>Webspace</Button
				>
			{/if}
			<Button icon={User} kind="ghost" href="/app/account"
				>Account</Button
			>
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
