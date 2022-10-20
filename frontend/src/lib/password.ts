const pwdChars =
	"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_'/.,<>:;[]{}";

export function validatePassword(
	password: string,
	minChars: number = 12,
	requireLetters: boolean = false,
	requireSpecial: boolean = true,
): string[] {
	if (!password || !password.length) return [];
	let ret: string[] = [];
	let hasUpper, hasLower, hasSpecial;
	for (let i = 0; i < password.length; i++) {
		const c = password[i];
		if (c >= "a" && c <= "z") hasLower = true;
		else if (c >= "A" && c <= "Z") hasUpper = true;
		else hasSpecial = true;
	}
	if (password.length < minChars)
		ret.push(`Passwort muss mindestens ${minChars} Zeichen lang sein`);
	if (requireLetters && !hasLower && !hasUpper)
		ret.push("Passwort muss Klein oder Großbuchstaben beinhalten");
	if (requireSpecial && !hasSpecial)
		ret.push("Passwort muss mindestens ein Sonderzeichen beinhalten");
	return ret;
}

/**
 * @returns a randomly generated password, or false if it fails to generate a
 * valid password.
 */
export function generatePassword(length: number = 16): string | false {
	const random = new Uint32Array(length);
	for (let i = 0; i < 100; i++) {
		if (window.Crypto && window.crypto)
			window.crypto.getRandomValues(random);
		else
			for (let n = 0; n < length; n++)
				random[n] = Math.floor(Math.random() * pwdChars.length);

		let password = "";
		for (let n = 0; n < length; n++)
			password += pwdChars[random[n] % pwdChars.length];
		if (validatePassword(password).length == 0) {
			return password;
		}
	}
	return false;
}
