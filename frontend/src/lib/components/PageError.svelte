<script lang="ts">
    import { Button } from "carbon-components-svelte";

	export let message: string;
	export let error: any;
	export let light: boolean = false;
</script>

<div class:error={!light}>
	<p class="msg">
		{message}
	</p>
	{#if error}
		<p class="details">
			{error}
		</p>
	{/if}
	<Button href="/" kind="secondary">Zurück zur Startseite</Button>
</div>

<style>
	.error {
		max-width: 600px;
		margin: 1em auto;
		background-color: var(--cds-ui-01);
		padding: 2em;
		box-sizing: border-box;
	}

	.error .msg {
		margin-top: 0;
	}

	p {
		margin: 1em 0;
	}
</style>