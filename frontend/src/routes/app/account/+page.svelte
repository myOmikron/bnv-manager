<script lang="ts">
	import Tiles from "$lib/components/Tiles.svelte";
	import type { LayoutData } from "./$types";
	import {
		StructuredList,
		StructuredListCell,
		StructuredListBody,
		StructuredListRow,
		Link,
		PasswordInput,
	} from "carbon-components-svelte";
	import FormDialog from "$lib/components/FormDialog.svelte";
	import { validatePassword } from "$lib/password";
	import { changePassword, login } from "$lib/user";

	export let data: LayoutData;

	let openPasswordChange = false;
	let pwChangeState = {
		updating: false,
		oldPassword: "",
		newPassword: "",
		newPassword2: "",
	};
</script>

<Tiles>
	<StructuredList>
		<StructuredListBody>
			<StructuredListRow>
				<StructuredListCell>Nutzername</StructuredListCell>
				<StructuredListCell>
					{data.account?.username}
				</StructuredListCell>
			</StructuredListRow>
			<StructuredListRow>
				<StructuredListCell>Konto-Typ</StructuredListCell>
				<StructuredListCell>
					{#if data.account?.isAdmin}
						Super-Admin
					{:else if data.account?.isUser}
						Benutzer
						{#if data.account?.isClubAdmin}
							+ Verein-Manager
						{/if}
					{:else if data.account?.isClubAdmin}
						Verein-Manager
					{:else}
						Eingeschränkt
					{/if}
				</StructuredListCell>
			</StructuredListRow>
			<StructuredListRow>
				<StructuredListCell>Passwort</StructuredListCell>
				<StructuredListCell>
					<Link
						href="#"
						on:click={() => {
							openPasswordChange = true;
						}}>Ändern</Link
					>
				</StructuredListCell>
			</StructuredListRow>
		</StructuredListBody>
	</StructuredList>
</Tiles>

<FormDialog
	bind:open={openPasswordChange}
	name="Passwort Ändern"
	bind:state={pwChangeState}
	bind:working={pwChangeState.updating}
	work={async () => {
		let pwValidation = validatePassword(pwChangeState.newPassword);
		if (pwValidation.length) throw new Error(pwValidation.join("\n"));
		if (pwChangeState.newPassword != pwChangeState.newPassword2)
			throw new Error("Passwörter stimmen nicht überein");

		let username = data.account?.username;
		await changePassword(
			pwChangeState.oldPassword,
			pwChangeState.newPassword
		);

		let stillLoggedIn = await fetch("/api/me");
		if (!stillLoggedIn.ok) await login(username, pwChangeState.newPassword);
	}}
>
	<PasswordInput
		light
		labelText="Altes Passwort"
		required
		bind:value={pwChangeState.oldPassword}
		disabled={pwChangeState.updating}
		tooltipAlignment="end"
		tooltipPosition="left"
	/>
	<div class="gen-password">
		<PasswordInput
			light
			labelText="Neues Passwort"
			required
			bind:value={pwChangeState.newPassword}
			disabled={pwChangeState.updating}
			tooltipAlignment="end"
			tooltipPosition="left"
			invalid={validatePassword(pwChangeState.newPassword).length > 0}
			invalidText={validatePassword(pwChangeState.newPassword).join(
				".\n"
			)}
		/>
	</div>
	<PasswordInput
		light
		labelText="Passwort Wiederholen"
		required
		bind:value={pwChangeState.newPassword2}
		disabled={pwChangeState.updating}
		tooltipAlignment="end"
		tooltipPosition="left"
		invalid={pwChangeState.newPassword2 != "" &&
			pwChangeState.newPassword2 != pwChangeState.newPassword}
		invalidText="Passwort stimmt nicht mit dem oberen überein"
	/>
</FormDialog>
