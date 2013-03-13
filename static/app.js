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
			});
		}
		else
		{
			for(var i = 0; i < eventData.length; i++) {addEvent(eventData[i]);}
		}
	}
	else { document.location = "/login"; }
}

function populateTasks()
{
	$("#task_container").empty();
	if($.cookie('blah') != null)
	{
		$.post("loadtasks")
		.done(function(data)
		{
			for(var i = 0; i < data.length; i++)
			{
				var editPane = $('<div id="edit_task"><a data-role="button" data-inline="true" data-theme="d" data-icon="delete" data-iconpos="notext" class="ui-btn-right"></a></div>')
				var alertPane = $('<div id="alert_task"><a href="#list_new" data-role="button" data-inline="true" data-theme="d" data-icon="alert" data-iconpos="notext" class="ui-btn-right"></a></div>')
				var outer = jQuery("<div/>",{id:"task"});
				var content = jQuery("<div/>",{id:"task_content"});
				var inner1 = jQuery("<div/>",{id:"task_title_1",text:data[i]["summary"]});
				var inner2 = jQuery("<div/>",{id:"task_duration_2",text:data[i]["duration"]});
				var inner3 = jQuery("<div/>",{id:"task_deadline_3",text:data[i]["deadline"]});
				content.append(inner1);
				content.append(inner2);
				content.append(inner3);
				outer.append(alertPane);
				outer.append(editPane);
				outer.append(content);
				outer.appendTo("#task_container");
			}
			$("#task_container").trigger('create');
		});
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
				populateTasks();
			});
		});
		$("#edit").click(function()
		{
			$("div #edit_task").toggle();
		});
		$("div#edit_task").click(function()
		{
			console.log("ehY");
			//.siblings("#task_content").children("#task_title_1").text());
		});
		populateEvents();
		populateTasks();
});