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
    import Tiles from "$lib/components/Tiles.svelte";

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
	<Tiles>
		<Tile>
			<h2>Bürgernetzverband &ndash; Verwaltung</h2>
			<Form class="fluid-form" on:submit={handleSubmit}>
				<TextInput
					light
					size="xl"
					name="username"
					labelText="Username"
					placeholder="Enter your username..."
					required
					autofocus
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
	</Tiles>
</div>

<style>
	h2 {
		text-align: center;
	}

	.login-page :global(.fluid-form) {
		width: 75%;
		margin: auto;
	}

	@media screen and (max-width: 500px) {
		.login-page :global(.fluid-form) {
			width: 100%;
		}
	}
</style>
