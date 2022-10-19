<script lang="ts">
	import type { LayoutData } from "./$types";
	import { logout } from "$lib/user";
	import { goto } from "$app/navigation";
	import { Button, Link } from "carbon-components-svelte";
	import Language from "carbon-icons-svelte/lib/Language.svelte";
	import ArrowLeft from "carbon-icons-svelte/lib/ArrowLeft.svelte";
	import { page } from "$app/stores";

	export let data: LayoutData;

	async function doLogout() {
		console.log("logout");
		await window.bnv.showLoading(logout());
		goto("/login");
	}

	let pageTitle = "";
	page.subscribe((value) => {
		if (value.data.title) {
			pageTitle = value.data.title;
		} else {
		}
	});
</script>

<div class="header-wrapper" class:hidden={$page.data.title == undefined}>
	<div class="header">
		<Button
			class="back-btn"
			kind="ghost"
			icon={ArrowLeft}
			iconDescription="Zurück"
			on:click={() => window.history.back()}
		/>
		<div class="h1">
			<h1>{pageTitle}</h1>
		</div>
		<Button
			class="lang-btn"
			kind="ghost"
			icon={Language}
			iconDescription="Sprache"
		/>
	</div>
</div>

<!-- <Button iconDescription="Change Language" icon={Language} kind="ghost"></Button> -->
<!-- <div>ROOT LAYOUT {data.account?.username}</div> -->
<slot />
<div class="logout">
	<Link size="sm" on:click={() => doLogout()} href="#">Logout</Link>
</div>

<style>
	.header-wrapper {
		background-color: var(--cds-ui-01);
		height: 50px;
		transition: background-color 0.2s ease-in, transform 0.3s ease-out;
	}

	.header-wrapper.hidden {
		background-color: transparent;
		position: absolute;
		width: 100%;
		left: 0;
		top: 0;
	}

	.header {
		display: flex;
		max-width: 1000px;
		margin: 0 auto;
		transition: transform 0.3s ease-out, opacity 0.15s ease-in;
	}

	.header h1,
	.header :global(.back-btn),
	.header :global(.lang-btn) {
		transition: transform 0.3s ease-out, opacity 0.15s ease-in;
	}

	.hidden {
		transform: translateY(-100%);
	}

	.hidden .header h1,
	.hidden .header :global(.back-btn) {
		transform: translateY(100%);
		opacity: 0;
		pointer-events: none;
	}

	.hidden .header :global(.back-btn),
	.hidden .header :global(.lang-btn) {
		transform: translateY(100%);
		/* opacity: 0; */
	}

	.header .h1 {
		flex-grow: 1;
		text-align: center;
		overflow: hidden;
	}

	.header h1 {
		line-height: 50px;
		font-size: 30px;
	}

	.logout {
		margin: 1em;
		text-align: center;
	}
</style>
