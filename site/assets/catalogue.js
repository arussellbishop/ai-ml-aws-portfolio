'use strict';
const cards=[...document.querySelectorAll('article[data-category]')],search=document.querySelector('#search'),category=document.querySelector('#category'),audience=document.querySelector('#audience');
function filter(){let n=0;for(const card of cards){const show=card.textContent.toLowerCase().includes(search.value.toLowerCase())&&(!category.value||card.dataset.category===category.value)&&(!audience||!audience.value||card.dataset.audience.split(' ').includes(audience.value));card.hidden=!show;if(show)n++;}document.querySelector('#count').textContent=n+' of '+cards.length+' projects and workstreams';}
search.addEventListener('input',filter);category.addEventListener('change',filter);if(audience)audience.addEventListener('change',filter);filter();
