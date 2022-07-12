let el = document.getElementById('dynatable-record-count-candidate-list');

if( !el )
  return 0;

return el.innerText.split('/ ')[1];