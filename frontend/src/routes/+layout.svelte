<script lang="ts">
	import "carbon-components-svelte/css/all.css";

	export async function showLoading<T>(promise: Promise<T>): Promise<T> {
		startLoading();
		let res = await promise;
		stopLoading();
		return res;
	}

	window.bnv = {
		showLoading: showLoading,
		setTheme: (theme) => document.documentElement.setAttribute("theme", theme)
	};

	const dark_mode_enabled = () =>
		window.matchMedia &&
		window.matchMedia("(prefers-color-scheme: dark)").matches;

	window.bnv.setTheme(dark_mode_enabled() ? "g90" : "white");

	function startLoading() {
		(<any>document.getElementById("loading-indicator")).style.display = "";
	}

	function stopLoading() {
		(<any>document.getElementById("loading-indicator")).style.display = "none";
	}
</script>

<style>
	:global(.bx--label) {
		margin-top: .5rem;
		margin-bottom: 0;
	}

	#loading-indicator {
		display: block;
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		width: 100%;
		pointer-events: none;
		height: 4px;
		background: 
			linear-gradient(90deg, #00a2ff 300px, transparent 300px),
			linear-gradient(90deg, #00a2ff 300px, white 300px);
		background-size: 100vw 4px;
		background-position-x: 0vw;
		/* box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4); */
		animation: offset-bg infinite linear 4s;
	}

	@keyframes offset-bg {
		0% { background-position-x: 0, 0; }
		50% { background-position-x: 100vw, 50vw; }
		100% { background-position-x: 200vw, 100vw; }
	}
</style>

<div id="loading-indicator" style="display:none"></div>
<slot></slot>