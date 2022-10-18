<script lang="ts">
	import { goto } from "$app/navigation";
	import { getAccount, login } from "../../lib/user";

	let invalidForm = false;

	getAccount().then((acc) => (acc ? goto("/app") : null));
	async function handleSubmit(event: SubmitEvent) {
		let form = <HTMLFormElement>event.target;
		invalidForm = false;
		form.disabled = true;
		try {
			let data = new FormData(form);
			let username = data.get("username");
			let password = data.get("password");
			if (typeof username != "string" || typeof password != "string")
				throw new Error("Unexpected Form data types");
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

<div class="loginpage">
	<h1>Login</h1>
	<form
		class="login"
		method="post"
		class:invalid={invalidForm}
		on:submit|preventDefault={handleSubmit}
	>
		<label>
			<span>Benutzername</span>
			<input name="username" type="text" />
		</label>
		<label>
			<span>Passwort</span>
			<input name="password" type="password" />
		</label>
		<input type="submit" value="Login" />
	</form>
</div>

<style>
	form.invalid:before {
		content: "[invalid]";
		color: red;
		display: block;
	}
</style>
