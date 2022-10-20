<script lang="ts">
	import { generatePassword, validatePassword } from "$lib/password";
	import { Button, PasswordInput } from "carbon-components-svelte";
	import Renew from "carbon-icons-svelte/lib/Renew.svelte";

	async function handleGeneratePasswordButton(event: MouseEvent) {
		let gen = generatePassword();
		if (gen) value = gen;
		passwordVisible = true;
	}

	let value: string;
	let disabled: boolean = false;
	let required: boolean = false;
	let light: boolean = false;
	let passwordVisible: boolean = false;
	let labelText: string = "Passwort";
	let tooltipAlignment: "start" | "center" | "end" | undefined = undefined;
	let tooltipPosition: "top" | "right" | "bottom" | "left" | undefined =
		undefined;
</script>

<div class="gen-password">
	<PasswordInput
		{light}
		{labelText}
		{required}
		bind:value
		{disabled}
		{tooltipAlignment}
		{tooltipPosition}
		invalid={validatePassword(value).length > 0}
		invalidText={validatePassword(value).join(".\n")}
	/>
	<!-- TODO: show PasswordInput text with passwordVisible (no API for that yet) -->
	<Button
		icon={Renew}
		on:click={handleGeneratePasswordButton}
		{disabled}
		size="field"
		kind="danger-ghost"
		tooltipAlignment="end"
		tooltipPosition="top"
		iconDescription="Zufällig Generieren"
	/>
</div>

<style>
	.gen-password {
		display: flex;
		align-items: flex-start;
	}

	.gen-password > :global(:nth-child(2)) {
		margin-top: 24px;
	}

	.gen-password :global(.bx--form-requirement) {
		white-space: pre-wrap;
	}
</style>
