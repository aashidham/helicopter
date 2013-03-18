var eventData = null; //only non-null upon POST request
var editing = false;

function convertHM(date)
{
	return Math.round(date.getMinutes()/15)/4 + date.getHours();
}

function addEvent(data)
{
	var start = new Date(data["start"]);
	var end = new Date(data["end"]);
	var curr = new Date($("#day_header span").html());
	var paddingTop = 10; //this is unfortunately hard-coded at the moment
	if(curr.toDateString() == start.toDateString() && curr.toDateString() == end.toDateString())
	{
		var eventStart = convertHM(start);
		var eventLength = Math.floor((end - start)/900000) * .25;
		var height = ($("#hour_label").height() + 1)*eventLength - (paddingTop + 1);
		var top = ($("#hour_label").height() + 1)*eventStart;
		jQuery("<div/>",
		{id:"event",
		text:data["name"],
		}).css({"top":top+"px","height":height+"px",opacity:0.7}).corner("5px")
		.appendTo("#events");
	}
}

//refresh event list on day arrow click
function populateEvents()
{
	$("#events").empty();
	if($.cookie('blah') != null)
	{
		if(eventData == null)
		{
			$.post("loadall")
			.done(function(data) 
			{
				eventData = data;
				for(var i = 0; i < eventData.length; i++) {addEvent(eventData[i]);}
			});
		}
		else 
		{
			for(var i = 0; i < eventData.length; i++) {addEvent(eventData[i]);}
		}
	}
	else { document.location = "/login"; }
}

//contact the server to refresh eventData
function populateEventsRefresh()
{
	if($.cookie('blah') != null)
	{
		$.post("loadall")
		.done(function(data) 
		{
			eventData = data;
			populateEvents();
		});
	}
	else { document.location = "/login"; }
}

function durationToStr(duration)
{
	duration = parseInt(duration);
	return Math.floor(duration/3600) + "h:" + Math.floor((duration/60) % 60) + "m:" + duration % 60 + "s";
}

//contact the server to refresh tasks and events
function populateAll()
{
	$("#task_container").empty();
	if($.cookie('blah') != null)
	{
		$.post("loadtasks")
		.done(function(data)
		{
			for(var i = 0; i < data.length; i++)
			{
				var editPane = $('<div class="edit_task"><a data-role="button" data-inline="true" data-theme="d" data-icon="delete" data-iconpos="notext" class="ui-btn-right"></a></div>');
				editPane.click(function(){
					var position = $(this).parent().index();
					$.post("removetasks",{"position":position})
					.done(function(data)
					{
						populateAll();
					});
				});
				var alertPane = $('<div class="alert_task"><a href="#list_new" data-role="button" data-inline="true" data-theme="d" data-icon="alert" data-iconpos="notext" class="ui-btn-right"></a></div>');
				var outer = jQuery("<div/>",{id:"task"});
				var content = jQuery("<div/>",{id:"task_content"});
				var inner1 = jQuery("<div/>",{id:"task_title_1",text:data[i]["summary"]});
				var inner2 = jQuery("<div/>",{id:"task_duration_2",text:durationToStr(data[i]["duration"])});
				var deadline = data[i]["deadline"];
				deadline = new Date(parseInt(deadline));
				var inner3 = jQuery("<div/>",{id:"task_deadline_3",text:deadline.format("m/d/Y h:i A")});
				outer.appendTo("#task_container");
				content.append(inner1);
				content.append(inner2);
				content.append(inner3);
				outer.append(alertPane);
				outer.append(editPane);
				outer.append(content);
				content.click(function(){
					$(this).animate({opacity: 0.4});
					$(this).animate({opacity: 1.0});
					if(editing)
					{
						var position = $(this).parent().index();
						$.post("gettaskbypos",{"position":position})
						.done(function(data)
						{
							$("#name").val(data["summary"]);
							var deadline = new Date(parseInt(data["deadline"]));
							$("#deadline").val(deadline.toISOString());
							var duration = parseInt(data["duration"]);
							$("#duration_hours").val(Math.floor(duration/3600));
							$("#duration_minutes").val(Math.floor((duration/60) % 60));
							document.location = "#list_new";
						});
					}
				});
			}
			$("#task_container").trigger('create');
			populateEventsRefresh();
		});
	}
	else { document.location = "/login"; }
}

$(function(){
		var height = $("#day_header").height();
		$("#day_header").css("line-height",height+"px");
		alert(height);
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
				populateAll();
			});
		});
		$("#edit").click(function()
		{
			$(".edit_task").toggle();
			editing = !editing;
		});
		populateAll();
		$(".alert_task").show()
});