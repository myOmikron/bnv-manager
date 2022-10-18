<script lang="ts">
	import type { LayoutLoad } from './$types';
	import { logout } from '$lib/user';
    import { goto } from '$app/navigation';

	export let data: LayoutLoad;

	async function doLogout() {
		console.log("logout");
		await window.bnv.showLoading(logout());
		goto("/login");
	}
</script>
<div>ROOT LAYOUT {data.account?.username}</div>
<slot></slot>
<button on:click={() => doLogout()}>Logout</button>