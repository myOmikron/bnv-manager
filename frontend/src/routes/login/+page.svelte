<script lang="ts">
	import { goto } from "$app/navigation";
	import { getAccount, login } from "../../lib/user";
	import {
		Button,
		TextInput,
		PasswordInput,
		Tile,
		Form,
	} from "carbon-components-svelte";
	import Login from "carbon-icons-svelte/lib/Login.svelte";

	getAccount().then((acc) => (acc ? goto("/app") : null));
	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		let form = <HTMLFormElement>event.target;
		form.disabled = true;
		try {
			let data = new FormData(form);
			let username = data.get("username");
			let password = data.get("password");
			if (typeof username != "string" || typeof password != "string") {
				throw new Error("Unexpected Form data types");
			}
			let res = await window.bnv.showLoading(login(username, password));
			if (res) {
				goto("/app");
			}
		} finally {
			form.disabled = false;
		}
	}
</script>

<div class="login-page">
	<Tile class="tile">
		<h2>Bürgernetzverband &ndash; Verwaltung</h2>
		<Form class="fluid-form" on:submit={handleSubmit}>
			<TextInput
				light
				size="xl"
				name="username"
				labelText="Username"
				placeholder="Enter your username..."
				required
				tab-index="0"
			/>
			<PasswordInput
				light
				size="xl"
				name="password"
				labelText="Password"
				placeholder="Enter your password..."
				required
				type="password"
			/>
			<Button iconDescription="Login" icon={Login} type="submit">
				Login
			</Button>
		</Form>
	</Tile>
</div>

<style>
	.login-page {
		display: block;
		margin: 0 auto;
		width: 100%;
		max-width: 500px;
	}

	.login-page > :global(.tile) {
		margin-top: 3em;
		padding: 2em;
	}

	.login-page h2 {
		padding-bottom: 1em;
		text-align: center;
	}

	.login-page :global(.fluid-form) {
		width: 75%;
		margin: auto;
	}

	@media screen and (max-width: 500px) {
		.login-page > :global(.tile) {
			margin-top: 0;
			padding: 1em 4pt;
		}

		.login-page :global(.fluid-form) {
			width: 100%;
			margin: auto;
		}
	}
</style>
