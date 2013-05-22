var eventData = null; //only non-null upon POST request
var taskData = null;
var editing = false;
var globalAlert = false;
var tid = null;

function removeGlobalAlert()
{
	if(globalAlert)
	{
		console.log("in removeGlobalAlert");
		globalAlert = false;
		$("#global_alert").remove();
		$("#task_container").css("height","100%");
	}
}

function addGlobalAlert()
{
	if(!globalAlert) //only should be called once in a session
	{
		var toAdd = $('<div id="global_alert">You dont have enough free time to complete the tasks listed. Reduce the duration of your tasks to make your task list feasible again.</div>');
		toAdd.insertAfter($("#task_container"));
		$("#task_container").css("height","80%");
		globalAlert = true;
		$("#events").empty();
	}
	else console.log("ASSERT");
}

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
		if(data["type"] != 3)
		{
			jQuery("<div/>",
			{id:"event",
			text:data["name"] + " ("+start.format("h:i A")+ "-"+end.format("h:i A")+")",
			}).css({"top":top+"px","height":height+"px",opacity:0.7,background:"purple"}).corner("5px")
			.appendTo("#events");
		}
		else
		{
			jQuery("<div/>",
			{id:"event",
			text:data["name"] + " ("+start.format("h:i A")+ "-"+end.format("h:i A")+")",
			}).css({"top":top+"px","height":height+"px",opacity:0.7}).corner("5px")
			.appendTo("#events");		
		}
	}
}

//refresh event list on day arrow click
function populateEvents()
{
	$("#events").empty();
	if($.cookie('blah') != null)
	{
		if(eventData == null && !globalAlert)
		{
			$.post("loadall")
			.done(function(data) 
			{
				if(!data["error"])
				{
					eventData = data["data"];
					for(var i = 0; i < eventData.length; i++) {addEvent(eventData[i]);}
					removeGlobalAlert();
				}
				else addGlobalAlert();
			});
		}
		else if(eventData != null)
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
			 if(!data["error"])
			 {
				 eventData = data["data"];
				 populateEvents();
				 removeGlobalAlert();
			 }
			 else addGlobalAlert();
		 });
	}
	else { document.location = "/login"; }
}

function durationToStr(duration)
{
	duration = parseInt(duration);
	return Math.floor(duration/3600) + "h:" + Math.floor((duration/60) % 60) + "m:" + duration % 60 + "s";
}

function countdownDecrement(div,pos)
{
	console.log("in timer " + div.val());
	taskData[pos]["duration"] = Math.max(taskData[pos]["duration"] - 1,0);
	div.text(durationToStr(taskData[pos]["duration"]));
}

//contact the server to refresh tasks and events
function populateAll()
{
	$("#task_container").empty();
	editing = false;
	if($.cookie('blah') != null)
	{
		$.post("loadtasks")
		.done(function(data)
		{
			taskData = data;
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
				var alertPane = $('<div class="alert_task"><a data-role="button" data-inline="true" data-theme="d" data-icon="alert" data-iconpos="notext" class="ui-btn-right"></a></div>');
				alertPane.click(function(){
					alert("This task has a passed deadline and/or zero duration. Please fix this by editing the task.");
				});
				if ('showAlertPane' in data[i])
				{
					alertPane.show();
				}
				var outer = jQuery("<div/>",{class:"task",id:"task"});
				var content = jQuery("<div/>",{id:"task_content"});
				var inner1 = jQuery("<div/>",{id:"task_title_1",text:data[i]["summary"]});
				var inner2 = jQuery("<div/>",{id:"task_duration_2",class:"task_duration_2",text:durationToStr(data[i]["duration"])});
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
					var pos = $(this).parent().index();
					if(editing || 'showAlertPane' in taskData[pos])
					{
						$("#list_edit #name").val(taskData[pos]["summary"]);
						var deadline = new Date(parseInt(taskData[pos]["deadline"]));
						$("#list_edit #deadline").val(deadline.toISOString());
						var duration = parseInt(taskData[pos]["duration"]);
						$("#list_edit #duration_hours").val(Math.floor(duration/3600));
						$("#list_edit #duration_minutes").val(Math.floor((duration/60) % 60));
						$("#submit_edittask").click(function()
						{
							$.post("edittask",{"position":pos,"deadline":$("#list_edit #deadline").val(),"hours":$("#list_edit #duration_hours").val(),"minutes":$("#list_edit #duration_minutes").val(),"name":$("#list_edit #name").val()})
							.done(function(data)
							{
								$.mobile.navigate("#list");
								populateAll();
							});
						});
						document.location = "#list_edit";
					}
					else
					{
						$(this).animate({opacity: 0.4});
						$(this).animate({opacity: 1.0});
						$.post("startstop",{"position":pos})
						.done(function(data)
						{
							if(tid != null)
							{
								clearInterval(tid);
								tid = null;
							}
							populateAll();
						});
					}
				});
				if('startedTime' in data[i])
				{
					pos = i;
					taskData[pos]["duration"] = taskData[pos]["duration"] - (new Date().getTime() / 1000 - taskData[pos]["startedTime"])
					tid = setInterval(function(){countdownDecrement(inner2,pos);},1000);
				}

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
			$.post("addtask",{"deadline":$("#list_new #deadline").val(),"hours":$("#list_new #duration_hours").val(),"minutes":$("#list_new #duration_minutes").val(),"name":$("#list_new #name").val()})
			.done(function(data)
			{
				$.mobile.navigate("#list");
				populateAll();
			});
		});
		$("#edit").click(function()
		{
			$(".edit_task").toggle();
			editing = !editing;
		});
		populateAll();
});