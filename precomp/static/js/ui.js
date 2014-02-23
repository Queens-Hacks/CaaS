$('.tabs .button').on('click', function() {
  $('.tabs .button').toggleClass('selected');
  $('.use').toggleClass('selected');
});

$('.i-want-to select').on('change', function() {
  $('.processor').text($('select option:selected').text());
});
