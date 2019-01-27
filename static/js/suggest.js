const submitButton = document.querySelector('#submit-button');
const inputBox = document.querySelector('#input-box');
const resultsLimit = 10;

const writeSuggestion = function(suggestions) {
  const suggestionList = document.querySelector('#suggestion-list')
  suggestionList.style.visibility = 'visible';
  for (i = 0; i < Math.min(resultsLimit, suggestions.length); i++) {
    suggestionList.innerHTML += '<button class="dropdown-item" type="button">' + suggestions[i] + '</button>';
  }
}

const writeDefinitions = function(definitions) {
  $("#suggestion-list").empty();
  const definitionsRow = document.querySelector('#definitions')
  definitionsRow.style.visibility = 'visible';
  for (i = 0; i < definitions.length; i++) {
    definitionsRow.innerHTML +=
      '<div class="card col-4 mx-1 my-1">' +
       '<div class="card-body">' +
          '<h5 class="card-title">' + definitions[i]['hwi']['hw'] + '</h5>' +
          '<h6 class="card-subtitle mb-2 text-muted">' + definitions[i]['fl'] + '</h6>' +
          '<p class="card-text">' + definitions[i]['shortdef']+ '</p>' +
        '</div>' +
      '</div>'
      ;
  }
}

const getSuggestion = function() {
  let inputWord = inputBox.value;
  document.querySelector('#suggestion-list').innerHTML = '';
  $("#definitions").empty();
  $.get('/suggest/list/' + inputWord + '.json', success=writeSuggestion);
}

const getDefinition = function() {
  let inputWord = inputBox.value;
  document.querySelector('#suggestion-list').innerHTML = '';
  $("#definitions").empty();
  $.get('/define/' + inputWord + '.json', success=writeDefinitions);
}

$("#input-box").keydown(function (e){
    if(e.keyCode == 13){
        getDefinition();
    }
})

inputBox.addEventListener('keyup', getSuggestion);
submitButton.addEventListener('click', getDefinition);
