$(document).ready(function(){
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  var csrftoken = getCookie('csrftoken');

  $('.glyphicon').hover(function(){
    $(this).attr('class', 'glyphicon glyphicon-star');
    $(this).prevAll().attr('class', 'glyphicon glyphicon-star');
  }, function(){
    $(this).attr('class', 'glyphicon glyphicon-star-empty');
    $(this).prevAll().attr('class', 'glyphicon glyphicon-star-empty');
  })

  $('.glyphicon').click(function(){
    $(this).attr('class', 'glyphicon glyphicon-star');
    $(this).prevAll().attr('class', 'glyphicon glyphicon-star');
    $('.glyphicon').unbind('mouseenter mouseleave');
    $('.glyphicon').hide();
    var rating = $(this).attr('id');
    var item_id = $(this).siblings('#hidden').text();
    $.ajax({
      url: "/add_rating",
      type: 'POST',
      context: this,
      data: {'rating': rating, 'hidden': item_id, 'csrfmiddlewaretoken': csrftoken },
      dataType: "text",
      success: function(data){
        $(this).siblings('small').text('Rating submitted!')
      },
      error: function(data){
        console.log(data);
      }
    })
  })
})
