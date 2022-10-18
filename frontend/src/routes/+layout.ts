declare global {
	interface Window {
		bnv: BNVManager;
	}

	/**
	 * BNV manager specific functions, defined by the root layout, so they can
	 * be used globally.
	 * 
	 * This is defined as a global on `window.bnv` because module systems don't
	 * seem to work here (client-side / SPA only code + running in different
	 * component scope)
	 */
	interface BNVManager {
		showLoading<T>(promise: Promise<T>): Promise<T>;
	}
}

export const prerender = true;
export const ssr = false;
