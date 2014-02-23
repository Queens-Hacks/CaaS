$('.tabs .button').on('click', function() {
  $('.tabs .button').toggleClass('selected');
  $('.use').toggleClass('selected');
});

$('.i-want-to select').on('change', function() {
  $('.compiler').text($('select option:selected').text());
});
