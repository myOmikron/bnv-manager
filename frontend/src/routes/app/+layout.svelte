<script lang="ts">
	import type { LayoutData } from "./$types";
	import { logout } from '$lib/user';
	import { goto } from '$app/navigation';
	import { Button, Link } from "carbon-components-svelte";
	import Language from "carbon-icons-svelte/lib/Language.svelte";

	export let data: LayoutData;

	async function doLogout() {
		console.log("logout");
		await window.bnv.showLoading(logout());
		goto("/login");
	}
</script>

<style>
	.logout {
		margin: 1em;
		text-align: center;
	}
</style>

<!-- <Button iconDescription="Change Language" icon={Language} kind="ghost"></Button> -->
<!-- <div>ROOT LAYOUT {data.account?.username}</div> -->
<slot></slot>
<div class="logout">
	<Link size="sm" on:click={() => doLogout()} href="#">Logout</Link>
</div>
