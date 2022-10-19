<script lang="ts">
	import { goto } from "$app/navigation";
	import { getAccount, login } from "../../lib/user";
	import {
		Button,
		FluidForm,
		TextInput,
		PasswordInput,
	} from "carbon-components-svelte";
	import Login from "carbon-icons-svelte/lib/Login.svelte";

	let invalidForm = false;

	getAccount().then((acc) => (acc ? goto("/app") : null));
	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		let form = <HTMLFormElement>event.target;
		invalidForm = false;
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
			} else {
				invalidForm = true;
			}
		} finally {
			form.disabled = false;
		}
	}
</script>

<div class="login-page">
	<h2>Bürgernetzverband &ndash; Verwaltung</h2>
	<FluidForm class="fluid-form" on:submit={handleSubmit}>
		<TextInput name="username" labelText="Username" placeholder="Enter your username..." required tab-index=0 />
		<PasswordInput name="password" labelText="Password" placeholder="Enter your password..." required type="password" />
		<Button iconDescription="Login" icon={Login} type="submit">Login</Button>
	</FluidForm>
</div>

<style>
	:global(body) {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 256px;
	}

	.login-page {
		margin-top: 3em;
		padding: 2em;
		background-color: var(--level-2);
	}

	.login-page h2 {
		color: var(--prim-dark);
		padding-bottom: 1em;
	}

	.login-page :global(.fluid-form) {
		width: 75%;
		margin: auto;
	}
</style>
