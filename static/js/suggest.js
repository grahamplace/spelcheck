const submitButton = document.querySelector('#submit-button');
const inputBox = document.querySelector('#input-box');
const resultsLimit = 10;

const writeSuggestion = function(suggestions) {
  console.log(suggestions);
  const suggestionList = document.querySelector('#suggestion-list')
  document.querySelector('#suggestion').innerHTML = suggestions;
  suggestionList.style.visibility = 'visible';
  for (i = 0; i < Math.min(resultsLimit, suggestions.length); i++) {
    suggestionList.innerHTML += '<button class="dropdown-item" type="button">' + suggestions[i] + '</button>';
  }
}

const getSuggestion = function() {
  let inputWord = inputBox.value;
  document.querySelector('#suggestion-list').innerHTML = '';
  $.get('/suggest/list/' + inputWord + '.json', success=writeSuggestion);
}

// submitButton.addEventListener('click', getSuggestion);
inputBox.addEventListener('keyup', getSuggestion);
