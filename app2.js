$(document).on("mobileinit", function(){
  $.mobile.touchOverflowEnabled = true;
});

//onload
$(function(){
	var height = $("#day_header").height();
	$("#day_header").css("line-height",height+"px");
});