const submitButton = document.querySelector('#submit-button');
const inputBox = document.querySelector('#input-box');

const writeSuggestion = function(suggestion) {
  console.log(suggestion);
  document.querySelector('#suggestion').innerHTML = suggestion;
}

const getSuggestion = function() {
  let inputWord = inputBox.value;
  console.log(inputWord);
  $.get('/suggest/' + inputWord + '.json', success=writeSuggestion);
}

submitButton.addEventListener('click', getSuggestion);
