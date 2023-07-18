'use_strict';
const passwordField = document.getElementById('id_password');

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
