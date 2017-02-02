$(document).ready(function(){
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
      data: {'rating': rating, 'hidden': item_id },
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
