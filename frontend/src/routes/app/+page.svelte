<script lang="ts">
	import type { LayoutData } from "./$types";

	export let data: LayoutData;
</script>

<h2>User Page</h2>
<div>USER PAGE {data.account?.username}</div>