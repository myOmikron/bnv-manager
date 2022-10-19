<script lang="ts">
	export let style: string = "";

	let div: HTMLDivElement;

	$: div?.setAttribute("style", style);
</script>

<div class="tiles" bind:this={div}>
	<slot></slot>
</div>

<style>
	.tiles {
		display: block;
		margin: 1em auto;
		width: 100%;
		max-width: 500px;
	}

	.tiles > :global(.bx--tile) {
		padding: 3em;
		min-width: 0;
		margin-bottom: 1em;
	}

	@media screen and (max-width: 500px) {
		.tiles {
			margin-top: 0;
		}

		.tiles > :global(.bx--tile) {
			padding: 1em 4pt;
		}

		.tiles :global(h2) {
			padding: 0 50px; /* for still showing UI buttons */
		}
	}

	.tiles :global(h2) {
		margin-bottom: 1rem;
	}
</style>