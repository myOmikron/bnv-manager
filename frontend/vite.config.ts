import { sveltekit } from '@sveltejs/kit/vite';
import type { UserConfig } from 'vite';


const config: UserConfig = {
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8080',
				changeOrigin: true
			}
		}
	}
};

export default config;
