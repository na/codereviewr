/*
 * Commenting script for codereviewr.com
 *
 * Copyright (c) 2008 Nate Anderson
 *
 */
 
$(document).ready(function(){
	$('.linenos a').click(function(){
		//show comments
		var line = $(this);
		var comments = $('#comments');
		var lineno = parseInt(line.text());
		var lineOverlay = $('#lineoverlay');
		var lineOffset = $(this).offset();
		var marginTop = parseFloat($('pre').css('margin-top'));
		var offset = this.offsetTop-3;
		
		$('#commentlist').load("/code/1/comments #comments li");
		if ($('#commentlist').css('display')=='none'){
			comments.css('top',offset);
			lineOverlay.css('top',offset);
			lineOverlay.animate(
				{width:"90%"},
				500,
				'swing',
				function(){
					$('#commentlist').slideDown('slow');
				}
			);
		}else{
			comments.animate({top:offset},500);
			lineOverlay.animate({top:offset},500);
		};
		
		if (location.pathname == this.pathname && location.host == this.host) {
			var target = $(this.hash);
			$target = target.size() && target || $("[@name=" + this.hash.slice(1) +']');
			if ($target.length) {
				var targetOffset = $target.offset().top;
				$('html,body').animate({scrollTop: targetOffset-300}, 1000);
				return false;
			}
		};
		return false;
	});
});
