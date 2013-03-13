var eventData = null; //only non-null upon POST request

function convertHM(date)
{
	return Math.floor(date.getMinutes()/15)/4 + date.getHours();
}

function addEvent(data)
{
	var start = new Date(data["start"]);
	var end = new Date(data["end"]);
	var curr = new Date($("#day_header span").html());
	var paddingTop = 10; //this is unfortunately hard-coded at the moment
	if(curr.getDate() == start.getDate() && curr.getDate() == end.getDate())
	{
		var eventStart = convertHM(start);
		var eventLength = Math.floor((end - start)/900000) * .25;
		var height = ($("#hour_label").height() + 1)*eventLength - (paddingTop + 1);
		var top = ($("#hour_label").height() + 1)*eventStart;
		jQuery("<div/>",
		{id:"event",
		text:data["summary"],
		}).css({"top":top+"px","height":height+"px",opacity:0.7}).corner("5px")
		.appendTo("#events");
	}
}

function populateEvents()
{
	$("#events").empty();
	if($.cookie('blah') != null)
	{
		if(eventData == null)
		{
			$.post("../all.py")
			.done(function(data) 
			{
				eventData = data;
			   	for(var i = 0; i < data.length; i++) {addEvent(data[i]);}
			});
		}
		else
		{
			for(var i = 0; i < eventData.length; i++) {addEvent(eventData[i]);}
		}
	}
	else { document.location = "/login"; }
}

$(function(){
		var height = $("#day_header").height();
		$("#day_header").css("line-height",height+"px");
		height = $("#hour_label").height();
		$("#hour_label span").css("line-height",height+"px");
		
		if ($("#day_header span").html() === "")
		{
			var date = new Date();
			$("#day_header span").html(date.toDateString());
		}
		var date = new Date($("#day_header span").html());	
		$('.prev').click(function()
		{
			var date2 = date;
			date2.setDate(date2.getDate() - 1);
			$("#day_header span").html(date2.toDateString());
			populateEvents();
		});
		$('.next').click(function()
		{
			var date2 = date;
			date2.setDate(date2.getDate() + 1);
			$("#day_header span").html(date2.toDateString());
			populateEvents();
		});
		$("#submit_newtask").click(function()
		{
			$.post("addtask",{"deadline":$("#deadline").val(),"hours":$("#duration_hours").val(),"minutes":$("#duration_minutes").val(),"name":$("#name").val()})
			.done(function(data)
			{
				document.location = "#list";
			});
		});
		populateEvents();
});