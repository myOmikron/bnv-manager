// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
// and what to do when importing types
declare namespace App {
	// interface Locals {}
	interface LayoutData {
		account?: import("$lib/user").Account & {
			userInfo?: {
				firstName: string,
				lastName: string,
				primaryMail: string
			}
		}
	}
	// interface Error {}
	// interface Platform {}
}
