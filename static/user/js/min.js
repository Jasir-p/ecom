const signUpButton = document.getElementById('signUp');

const container = document.getElementById('container');
const signInButton = document.getElementById('signIn');
signUpButton.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});