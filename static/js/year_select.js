'use strict';

const yearInput = document.getElementById('year-input');
const nextYearField = document.getElementById('next-year');

const setNextYear = () => {
	const year = parseInt(yearInput.value) + 1;
	if (year.toString() == 'NaN' || year < 1900 || year > 10000) {
		nextYearField.innerText = 'Введите год';
	} else {
		nextYearField.innerText = `/ ${year}`;
	}
};

yearInput.onchange = setNextYear;
setNextYear();
