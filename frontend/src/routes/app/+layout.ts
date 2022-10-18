import type { LayoutLoad } from './$types';
import { getAccount } from '../../lib/user';
 
export async function load() {
	return {
		account: await getAccount()
	}
}