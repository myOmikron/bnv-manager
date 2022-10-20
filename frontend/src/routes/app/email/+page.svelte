<script lang="ts">
	import PageError from "$lib/components/PageError.svelte";
	import Tiles from "$lib/components/Tiles.svelte";
</script>

<Tiles>
	<PageError
		error={null}
		message="E-Mail Zugang ist noch im Aufbau, schau später nochmal vorbei"
	/>
</Tiles>
