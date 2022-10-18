<script lang="ts">
	import { goto } from '$app/navigation';
	import { getAccount, login } from '../../lib/user';

	getAccount().then(acc => acc ? goto("/app") : null);
	async function handleSubmit(event: SubmitEvent) {
		let form = <HTMLFormElement>event.target;
		form.classList.remove("invalid");
		form.disabled = true;
		try
		{
			let data = new FormData(form);
			let res = await showLoading(login(data.get("username"), data.get("password")));
			if (res) {
				goto("/app");
			} else {
				form.classList.add("invalid");
			}
		}
		finally
		{
			form.disabled = false;
		}
	}
</script>
<style>
	form.invalid:before {
		content: "[invalid]";
		color: red;
		display: block;
	}
</style>
<form class="login" method="post" on:submit|preventDefault={handleSubmit}>
	<h1>Login</h1>
	<label>
		<span>Benutzername</span>
		<input name="username" type="text">
	</label>
	<label>
		<span>Passwort</span>
		<input name="password" type="password">
	</label>
	<input type="submit" value="Login">
</form>