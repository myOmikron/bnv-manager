export interface Account {
	username: string;
	isUser: boolean;
	isClubAdmin: boolean;
	isAdmin: boolean;
}

/**
 * Number of seconds how long to keep a /api/login or /api/me response cached in
 * sessionStorage. Raising this number means inconsistencies with the server DB
 * may occur, but fewer requests will be sent on page navigations. (user object
 * is kept in memory across page loads, APIs should still implement permission
 * checking for testing if users are allowed to do things)
 */
const ACCOUNT_CACHE_TTL = 10; // debug value
// const ACCOUNT_CACHE_TTL = 60 * 3;

export async function getAccount(): Promise<Account | null> {
	let state: any = window.sessionStorage.getItem("accountState");
	if (typeof state == "string") {
		try {
			state = JSON.parse(state);
		}
		catch (e) {
			state = null;
		}
	}
	if (typeof state == "object"
		&& state
		&& state._accessTime
		&& (new Date().getTime() - state._accessTime) < 1000 * ACCOUNT_CACHE_TTL)
		return <Account>state;

	let res = await fetch("/api/me");
	if (!res.ok)
		return null;

	let json = await res.json();
	let ret = makeAccount(json.username, json);
	window.sessionStorage.setItem("accountState", JSON.stringify(ret));
	return ret;
}

export async function login(username: string, password: string): Promise<Account | null> {
	let res = await fetch("/api/login", {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			username, password
		})
	});
	if (!res.ok)
		return null;

	let ret = makeAccount(username, await res.json());
	window.sessionStorage.setItem("accountState", JSON.stringify(ret));
	return ret;
}

function makeAccount(username: string, json: any): Account & { _accessTime: number } {
	return {
		username: username,
		isAdmin: json.is_admin,
		isClubAdmin: json.is_club_admin,
		isUser: !json.is_admin && !json.is_club_admin,
		_accessTime: new Date().getTime()
	};
}

export async function logout(): Promise<void> {
	let res = await fetch("/api/logout");
	if (res.ok)
		window.sessionStorage.removeItem("accountState");
	else {
		alert("Logout failed!");
		window.location.reload();
	}
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
	let res = await fetch("/api/me/password", {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			old_password: oldPassword,
			new_password: newPassword
		})
	});

	if (!res.ok)
		throw new Error(await res.text());
}
