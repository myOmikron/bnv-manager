import type { LayoutLoad } from './$types';
import { getAccount } from '../../lib/user';
import { goto } from '$app/navigation';
 
export async function load() {
	let account = await getAccount();
	if (!account)
		goto("/login");

	return {
		account: await getAccount()
	}
}