(function($) {
"use strict";

    /* ==========================
    Video - set player
    ========================== */


    var $video = $('.video-prev');
    $video.append(''); 
    $video.append('<span class="icon play" />');
	$video.append('<span class="overlay" />');
	$video.append(''); 
	$('.video-prev').each(function() {
    	var term = $(this).data("name");
		$("<div class='name'>"+term+"</div>").appendTo(this);
	});
	
    $('.video-play-here').click(function () { 
        $(this).html($('<iframe />', {
            src: this.href,
			
        }));
		$('.video-prev iframe').attr("allowfullscreen", "allowfullscreen");
        return false;
		
    });
	
	$(window).scroll(function() {    
		var scroll = $(window).scrollTop();

		if (scroll >= 300) {
			$(".navbar").addClass("dark");
		} else {
			$(".navbar").removeClass("dark");
		}
	});

	$(document).on('click', '.browse', function(){
	  var file = $(this).parent().parent().parent().find('.file');
	  file.trigger('click');
	});
	$(document).on('change', '.file', function(){
	  $(this).parent().find('.form-control').val($(this).val().replace(/C:\\fakepath\\/i, ''));
	});
	
})(jQuery);