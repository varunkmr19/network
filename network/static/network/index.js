$('.followButton').on('click', function(e) {
  e.preventDefault();
  $button = $(this);
  $followerCount = parseInt($('#followerCount').text());
  if($button.hasClass('btn-success')) {
    // $.ajax(); Do Unfollow
    var url_ = $button.attr("data-value")
    $.ajax({
      url: url_,
      method: "GET",
      data: {},
      success: function(data) {
        // decrement follower count
        $followerCount -= 1;
        $('#followerCount').text($followerCount)
      }, error: function(error) {
        console.log(error)
      }
    });
    $button.removeClass('btn-success');
    $button.removeClass('btn-danger');
    $button.addClass('btn-primary');
    $button.text('Follow');
  } else {
    // $.ajax(); Do Follow
    var url_ = $button.attr("data-value")
    $.ajax({
      url: url_,
      method: "GET",
      data: {},
      success: function(data) {
        $followerCount += 1;
        $('#followerCount').text($followerCount)
      }, error: function(error) {
        console.log(error)
      }
    })
    $button.addClass('btn-success');
    $button.text('Following');
  }
});

$('button.followButton').hover(function() {
  $button = $(this);
  if($button.hasClass('btn-success')) {
    $button.addClass('btn-danger');
    $button.text('Unfollow');
  }
},function() {
  if($button.hasClass('btn-success')) {
    $button.removeClass('btn-danger');
    $button.text('Following');
  }
});


// like or unlike
$(document).ready(function() {
  $(".like").on("click", function(e) {
    e.preventDefault();
    $likeButton = $(this);
    $likesCount = parseInt($('span', $likeButton).text());
    let url_ = $likeButton.attr("href");

    if($likeButton.hasClass('liked')) {
      // Do Unlike
      $.ajax({
        url: url_,
        method: "GET",
        data: {},
        success: function(data) {
          $likesCount -= 1;
          $('span', $likeButton).text($likesCount);
        }, error: function(error) {
          console.log(error)
        }
      });
      $likeButton.removeClass('liked');
    } else {
      // Do Like
      $.ajax({
        url: url_,
        method: "GET",
        data: {},
        success: function(data) {
          $likesCount += 1;
          $('span', $likeButton).text($likesCount);
        }, error: function(error) {
          console.log(error)
        }
      });
      $likeButton.addClass('liked');
    }
  });
});

$('#delete').on('show.bs.modal', function(e) {
  let postId = $(e.relatedTarget).data('id');
  let url = `/post/delete/${postId}`;
  
  $('#deleteForm').attr('action', url);
});

$('#edit').on('show.bs.modal', function(e) {
  const postId = $(e.relatedTarget).data('id');
  console.log(postId);
  const prevContent = $(e.relatedTarget).data('content');
  const url = `/post/edit/${postId}`;
  
  $('.editTextarea').text(prevContent);
  $('#editForm').attr('action', url);
});