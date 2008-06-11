/*
 * Commenting script for codereviewr.com
 *
 * Copyright (c) 2008 Nate Anderson
 *
 */

$(document).ready(function(){
	//$('#comments').dialog();
	//$('#comments').dialog('close');
	
	$('.linenos a').click(function(){
		//show comments

		var line = $(this);
		var comments = $('#comments');
		var lineno = parseInt(line.text());
		var lineOverlay = $('#lineoverlay');
		var lineOffset = $(this).offset();
		var contentOffset = $('#page-content').offset();
		var offset = lineOffset.top-contentOffset.top;
		var url = "/code/1/comments/line/" + lineno;
		comments.load(url,function(){
            $('#commentform').submit(function(){
                submitComment(lineno);
                return false;
            });
        });
		if (comments.css('display')=='none'){
			comments.css('top',offset);
			lineOverlay.css('top',offset);
			lineOverlay.animate(
				{width:"90%"},
				500,
				'swing',
				function(){
					comments.slideDown('slow');
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
 
 function submitComment(lineno){
    var formdata = $('#commentform :input').getFormData();
    $.post("comments/line/" + lineno,formdata,function(data){
        process(data);
    }, "html");
 };
 function process(data){
    $('#comments').html(data);
 };
 $.fn.getFormData = function(){
    var data = {}    
    this.each(function(){
        var type = this.type, tag = this.tagName.toLowerCase();
        var name = this.name;
        if (tag == 'form')
            return $(':input',this).getFormData();
        if (type == 'text' || type == 'password' || tag == 'textarea' || tag== 'select')
            var val = this.value;
        else if (type == 'checkbox' || type == 'radio')
            var val = this.checked;
        
        var extend = new Array; 
        extend[name] = val
        $.extend(data,extend)
    });
    return data;
  };
