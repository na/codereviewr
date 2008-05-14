/*
 * Commenting script for codereviewr.com
 *
 * Copyright (c) 2008 Nate Anderson
 *
 */
 
 $(document).ready(function(){
    
	$('.lineno').mouseover(function(){
        var line = $('a',this).text();
        $('#line-'+line).css('backgroundColor','#ccc2ac');
    });
    $('.lineno').mouseout(function(){
        var line = $('a',this).text();
        $('#line-'+line).css('backgroundColor','transparent');
    });
    
    $('#commentsLink').click(function(){
        $('#comment-wrap').slideDown('slow');
        loadComments();
        return false;
    });
    $('.linenos a').click(function(){
        //show comments
		var line = $(this);
		var wrap = $('#comment-wrap')
        var comments = $('#comments')
		var lineno = parseInt(line.text());
		var lineOverlay = $('#lineoverlay');
		var lineOffset = $(this).offset();
		var contentOffset = $('#page-content').offset();
		var offset = lineOffset.top-contentOffset.top;
		//url for ajax comments
        var url = "/code/1/comments/line/" + lineno;
		loadComments(lineno);
        //load them and when done attach event to the form for comment submission
        /*comments.load(url,function(){
            $('#commentform').submit(function(){
                submitComment(lineno);
                return false;
            });
        });*/
		//if this is first line number click then show the comments element and line overlay
        if (wrap.css('display')=='none'){
			wrap.css('top',offset);
			lineOverlay.css('top',offset);
			lineOverlay.animate(
				{width:"90%"},
				500,
				'swing',
				function(){
					wrap.slideDown('slow');
				}
			);
		//else move to line number clicked
        }else{
			wrap.animate({top:offset},500);
			lineOverlay.animate({top:offset},500);
		};
		//smooth scroll to the line clicked to ensure context of line
		if (location.pathname == this.pathname && location.host == this.host) {
					var target = $(this.hash);
					$target = target.size() && target || $("[@name=" + this.hash.slice(1) +']');
					if ($target.length) {
						var targetOffset = $target.offset().top;
					    $('html,body')
					    .animate({scrollTop: targetOffset-300}, 1000);
					    return false;
			       }
		};
       
		return false;
    });
 });
 
 /*
 Form handler for submitting comments and processing the response
 */
 function submitComment(lineno){
    var url = (lineno) ? "comments/line/" + lineno : "comments/";
    var formdata = $('#commentform :input').getFormData();
    $.post(url,formdata,function(data){
        $('#comments').html(data);
        incrementCommentFlags(lineno);
    }, "html");
 };
 
 
 function loadComments(line){
    
    var url = (line) ? "comments/line/" + line : "/code/1/comments/";
	//load them and when done attach event to the form for comment submission
    $('#comments').load(url,function(){
        $('#commentform').submit(function(){
            submitComment(line);
            return false;
        });
    });
    return false;
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
  
function incrementCommentFlags(line){
    //update commentsLink count
    $('#commentsLink').increment();
   
    // update Line flag count and class if line is given
    if (line) {
        var selector = '.linenos:eg('+line+') div'
        var el = $(selector);
        el.increment();
        el.addClass('hascomment');
    };
    
};
$.fn.increment = function(){
    var v = parseInt(this.text());
    
    if (v) {
        v += old; 
        this.text(v.toString());
    }
    return false;
};
