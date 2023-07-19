'use_strict';
console.dir(document.querySelectorAll('input[type="password"]'));
const passwordField = document.querySelectorAll('input[type="password"]')[0];

function showPassword() {
	if (passwordField.type === 'password') {
		passwordField.type = 'text';
	} else {
		passwordField.type = 'password';
	}
}

function passwordGenerate() {
	const generatedPassword = Math.random().toString(36).slice(-10);
	passwordField.value = generatedPassword;
}
