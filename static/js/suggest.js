const submitButton = document.querySelector('#submit-button');
const inputBox = document.querySelector('#input-box');
const resultsLimit = 9;
let selectedId = 0;
let resultsDisplayed = 0;

const itemClick = function(event) {
  let word = event.target.value;
  inputBox.value = word;
  getDefinition(word);
}

const writeSuggestion = function(suggestions) {
  const suggestionList = document.querySelector('#suggestion-list')
  suggestionList.style.visibility = 'visible';
  $("#suggestion-list").empty();
  suggestionList.innerHTML += '<button class="dropdown-item" id="dd-1' + '" type="button" value="' + inputBox.value  + '">' + inputBox.value + '<span class="text-muted"> - Goggle Search</span></button>';
  resultsDisplayed = Math.min(resultsLimit, suggestions.length) + 1;
  for (i = 0; i < resultsDisplayed - 1; i++) {
    suggestionList.innerHTML += '<button class="dropdown-item" id="dd-' + (i+2) + '" type="button" value="' + suggestions[i]  + '">' + suggestions[i] + '</button>';
  }

  var dropdownItems = document.getElementsByClassName('dropdown-item');
  for (i = 0; i < dropdownItems.length; i++) {
    dropdownItems[i].addEventListener('click', itemClick);
  }
}

const writeDefinitions = function(definitions) {
  $("#suggestion-list").empty();
  if (definitions.length === 0) {
    const noResult = document.querySelector('#no-result');
    noResult.innerHTML = 'No definition found for ' + inputBox.value + '. Please search another word.';
    noResult.style.visibility = 'visible';
    setTimeout(function(){ noResult.style.visibility = 'hidden';}, 5000);
  } else {
    const definitionsRow = document.querySelector('#definitions')
    definitionsRow.style.visibility = 'visible';
    for (i = 0; i < definitions.length; i++) {
      definitionsRow.innerHTML +=
        '<div class="card col-4 mx-1 my-1">' +
         '<div class="card-body">' +
            '<h5 class="card-title">' + definitions[i]['word'] + '</h5>' +
            '<h6 class="card-subtitle mb-2 text-muted">' + definitions[i]['fl'] + '</h6>' +
            '<p class="card-text">' + definitions[i]['definition_str']+ '</p>' +
          '</div>' +
        '</div>'
        ;
    }
  }
}

const getSuggestion = function(event) {
  if ((event.keyCode >= 37 && event.keyCode <= 40) || event.keyCode == 13)
    return;
  $("#suggestion-list").empty();
  let inputWord = inputBox.value;

  selectedId = 0;
  document.querySelector('#suggestion-list').innerHTML = '';
  $("#definitions").empty();
  $.get('/suggest/list/' + inputWord + '.json', success=writeSuggestion);
}

const getDefinition = function() {
  let inputWord = inputBox.value;
  if (!inputWord)
    return;
  document.querySelector('#suggestion-list').innerHTML = '';
  $("#definitions").empty();
  $.get('/define/' + inputWord + '.json', success=writeDefinitions);
}

$("#input-box").keydown(function (e){
    if(e.keyCode == 13)
        getDefinition();
})

$("#input-box").keydown(function (e){
    let oldId = selectedId;
    let oldText = inputBox.value;
    if(e.keyCode == 38){ // up arrow key
        selectedId = Math.max(0, selectedId - 1);
    } else if (e.keyCode == 40) { // down arrow key
        selectedId = Math.min(resultsDisplayed, selectedId + 1);
    } else {
      return;
    }

    $('#dd-' + selectedId).addClass('active');

    if (selectedId != oldId)
      $('#dd-' + oldId).removeClass('active');

    let selection = $('#dd-' + selectedId).val();
    if (selection)
      inputBox.value = selection;
})

inputBox.addEventListener('keyup', getSuggestion);
submitButton.addEventListener('click', getDefinition);
