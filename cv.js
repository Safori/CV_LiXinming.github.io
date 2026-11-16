'use strict';
const button = document.querySelector('#print-cv');
button.hidden = false;
button.addEventListener('click', () => window.print());
