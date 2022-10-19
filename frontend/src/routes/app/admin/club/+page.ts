import { goto } from '$app/navigation';
import type { PageLoad } from './$types';

export var load: PageLoad = function(event) {
	let url = event.url;
	let query = url.search.substring(1).split('&');
	let clubId = "";
	let clubName = "";
	query.forEach(q => {
		if (q.startsWith("club="))
			clubId = decodeURIComponent(q.substring(5));
		else if (q.startsWith("name="))
			clubName = decodeURIComponent(q.substring(5));
	});
	if (!clubId) {
		console.log("Missing state", url);
		goto("/app/admin");
		return;
	}

	return {
		clubId: clubId,
		title: clubName || clubId
	}
}