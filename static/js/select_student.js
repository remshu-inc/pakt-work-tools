'use strict';
const addSelect = document.getElementById('add-select');
const addLink = document.getElementById('add-link');

addLink.setAttribute('href', addSelect.value);

addSelect.onchange = () => {
	addLink.setAttribute('href', addSelect.value);
};
