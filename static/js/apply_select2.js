'use strict';

$('.select2').select2({
	theme: 'bootstrap-5',

	language: {
		noResults: () => {
			return 'Результаты не найдены';
		},
	},
});

$(document).on('select2:open', () => {
	console.dir(document.getElementsByClassName('select2-search__field')[0]);
	document.getElementsByClassName('select2-search__field')[0].focus();
});
