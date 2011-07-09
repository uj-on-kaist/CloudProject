
function edit_description(){
    if($("#topic_desc").is(":visible")){
		$("#topic_desc").hide();
		$(".edit_btn").hide();
		$("form.newDesc").show();
	}else{
		$("#topic_desc").show();
		$(".edit_btn").show();
		$("form.newDesc").hide();
	}
	return false;
}

function update_description(){
    var ed = tinyMCE.get('newDesc');
    var new_desc = ed.getContent();
    
    var topic_id = $("form.newDesc #topic_id").val();
    var tokenValue = $("#csrf_token").text();
    
    data= "topic_id=" + topic_id + "&desc=" + encodeURIComponent(new_desc);
    data +="&csrfmiddlewaretoken="+tokenValue;
    
	$.ajax({
		type : "POST",
		url : "/api/feed/update/desc",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            $("#topic_desc").html(new_desc);
            edit_description();
          }
		},
		error : function(data){
		  console.log(data);
		}  
	});
	
    
}

function load_dialog(){
    var url="/api/sidebar/dialog/get";
    
    $.ajax({
		type : "GET",
		url : url,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  /* console.log(json); */
          if(json.success){
            display_dialogs(json.dialogs);
          }else{console.log(json);}
		},
		error : function(data){
		  console.log(data);
		}
	});
}
function display_dialogs(dialogs){
    for(var i=0; i<dialogs.length; i++){
        var dialog = dialogs[i];
        var last = false;
        if(i == dialogs.length-1)
            last = true;

        $("#dialog_list").append(make_dialog_layout(dialog, last));
    }
}
function make_dialog_layout(dialog, last){
    var dialog_layout = $("#dialog_list .dialog_item.template").clone();
        
    dialog_layout.removeClass("template");
    dialog_layout.addClass("dialog");
    dialog_layout.attr("id","dialog_"+dialog.id);
    dialog_layout.attr("dialog_id",dialog.id);
    if(last)
        dialog_layout.addClass("last");
    
    
    dialog_layout.find('.user_link').text(dialog.user);
    dialog_layout.find('.author_name').text(dialog.username);
    dialog_layout.find('p.dialog_message').html(dialog.contents);
    dialog_layout.find('abbr.dialog_time').text(humane_date(dialog.reg_date));
    
    if(dialog.user == $("#user_name_info").text()){
        dialog_layout.find('.stream_element_delete').show();
        dialog_layout.find('.stream_element_delete').attr('dialog_id',dialog.id);
        dialog_layout.find('.stream_element_delete').click(function(){
            delete_dialog($(this));
        });
    }else{
        dialog_layout.find('.stream_element_delete').remove();
    }
    return dialog_layout;
}

function upload_dialog(){

    var dialog=$('input#dialog_input').val();
    if(dialog.replace(" ","") == ""){
        return false;
    }
    $('input#dialog_input').val("");
    var tokenValue = $("#csrf_token").text();
    
    data= "dialog=" + dialog;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/api/sidebar/dialog/add",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            var dialog_layout = make_dialog_layout(json.dialog,false);
            $("#dialog_list").prepend(dialog_layout);
            dialog_layout.hide();
            dialog_layout.slideToggle();
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function delete_dialog(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var dialog_id=item.attr('dialog_id');
    var tokenValue = $("#csrf_token").text();
    
    $.ajax({
        type : "POST",
        url : "/api/sidebar/dialog/delete",
        data : "dialog_id="+dialog_id+"&csrfmiddlewaretoken="+tokenValue,
        dataType : "JSON",
        cache : false,
        success : function(json) {
            console.log(json);
            if(json.success){
                $("#dialog_"+dialog_id).slideToggle("",function(){
                    $(this).remove();
                    $(".dialog_item").last().addClass("last");  
                });  
            }
            },
        error : function(data){
            console.log(data);
        }
    });

}


function send_invite(item){
    var emails = item.val().replace(' ',"|");
    item.val("");
    $.ajax({
		type : "GET",
		url : "/api/sidebar/invite",
		data : "&emails="+emails,
		cache : false,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
		  item.parent().parent().find('.invi_sent').fadeIn(500).delay(2000).fadeOut(500)
		},
		error : function(data){
		  console.log(data);
		}
  });
}


function get_month_event_info(year, month, callback){
  if(month == '' || year == ''){
      var now = new Date();
      year = now.getFullYear();
      month = now.getMonth()+1;
  }
  $.ajax({
		type : "GET",
		async : false,
		cache : false,
		url : "/api/event/get_info",
		data : "&year="+year+"&month="+month,
		dataType : "JSON",
		success : function(json) {
		  callback(json.events);
		},
		error : function(data){
		  callback(json.events);
		}
  });
}

function get_date_event_info(inst){
  var year = inst.selectedYear;
  var month = inst.selectedMonth+1;
  var date = inst.selectedDay;
  
  $.ajax({
		type : "GET",
		async : false,
		cache : false,
		url : "/api/event/get_info_date",
		data : "&year="+year+"&month="+month+"&date="+date,
		dataType : "JSON",
		success : function(json) {
		  console.log(json.events);
		  
		  $("#side_event_list").find("li").remove();
		  for(var k=0; k<json.events.length; k++){
		      $("#side_event_list").append("<li><p>- <a href='/event/detail/"+json.events[k].id+"'>"+json.events[k].title+"</a></p></li>");
		  }
		  if(json.events.length == 0){
		      $("#side_event_list").append("<li><p>- There is no event on this day.</p></li>");
		  }
		  
		},
		error : function(data){
		  console.log(data);
		}
  });
}