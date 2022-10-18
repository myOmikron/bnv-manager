import { goto } from "$app/navigation";
import { getAccount } from "../lib/user";

export async function load(event: import('./$types').PageLoadEvent) {
	let user = await getAccount();
	if (user) {
		goto("/app");
	} else {
		goto("/login");
	}
}
