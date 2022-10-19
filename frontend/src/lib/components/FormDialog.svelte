<script lang="ts">
	import { InlineLoading, Modal } from "carbon-components-svelte";

	export let open: boolean = false;
	export let preventCloseOnClickOutside: boolean = false;
	export let danger: boolean = false;
	export let primaryButtonDisabled: boolean = false;
	export let name: string;
	export let submitText: string | undefined = undefined;
	export let cancelText: string = "Abbrechen";
	export let working: boolean = false;
	export let error: string | undefined = undefined;
	export let selectorPrimaryFocus: string | undefined = undefined;
	export let workingText: string = "Saving...";
	export let state: any = undefined;
	export let primaryButtonIcon: any = undefined;

	// for duplicating JSON
	let resetStateData = JSON.stringify(state);

	export let init: Function | undefined = undefined;
	export let work: Function;

	let validator: HTMLFormElement;

	async function initState() {
		working = false;
		error = undefined;
		state = JSON.parse(resetStateData);
		if (init) await init();
	}

	async function handleSubmit() {
		error = undefined;
		working = true;
		try {
			if (!validator.reportValidity()) return;

			await work(state);
			open = false;
		} catch (e) {
			error = e + "";
		} finally {
			working = false;
		}
	}
</script>

<Modal
	{open}
	preventCloseOnClickOutside={preventCloseOnClickOutside || working}
	{danger}
	modalHeading={name}
	primaryButtonText={submitText || name}
	disabled={working}
	{selectorPrimaryFocus}
	{primaryButtonIcon}
	primaryButtonDisabled={working || primaryButtonDisabled}
	secondaryButtonText={cancelText}
	on:click:button--secondary={() => (working ? null : (open = false))}
	on:open={initState}
	on:close={() => (open = false)}
	on:submit={handleSubmit}
>
	{#if working}
		<InlineLoading status="active" description={workingText} />
	{:else if error && error.length}
		<InlineLoading status="error" description={error} />
	{/if}

	<form bind:this={validator}>
		<slot />
	</form>
</Modal>
