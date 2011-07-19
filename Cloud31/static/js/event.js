function register_event(item){
    item.attr('disabled','disabled');
    start_loading(item);
    var title=$("#input_title").val();
    if(title == ""){
        finish_loading(item);
        return false;
    }
    
    
    var start_date=$("#start_time input").val();
    var start_time_text=$("#start_time select option[value='"+$("#start_time select").val()+"']").text();
    var start_time = start_date + ' ' + start_time_text;
    
    var end_date=$("#end_time input").val();
    var end_time_text=$("#end_time select option[value='"+$("#end_time select").val()+"']").text();
    if(end_date == ''){
        end_time_text = '';
    }
    var end_time = end_date + ' ' + end_time_text;
    
    var location=$("#input_location").val();
    var invited_text=$("#input_invites").val();
    var message=$("#input_message").val();
    var public=$("#input_public").is(':checked');
    
    
    var tokenValue = $("#csrf_token").text();
    
    var data = "title=" + title + "&start_time=" + start_time;
    if(end_time != ''){
        data += "&end_time="+end_time;
    }
    data += "&location=" + location + "&invited_text=" + invited_text + "&message="+message;
    data += "&public="+public;
    data +="&csrfmiddlewaretoken="+tokenValue;
    
    clear_event_input();

	$.ajax({
		type : "POST",
		url : "/api/event/register/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            document.location.href='/event/'
          }else{
            finish_loading(item);
          }
		},
		error : function(data){
		  console.log(data);
		}
	});

    return false;
}

function reset_start_time(){
    var d = new Date();
    d.setMinutes(d.getMinutes() + 60);
    var curr_date = d.getDate();
    var curr_month = d.getMonth()+1;
    var curr_year = d.getFullYear();
    $('#start_time .datepicker').val(curr_year+"-"+curr_month+"-"+curr_date);
    
    var curr_hour = d.getHours();
    var curr_min = d.getMinutes();
    var curr_time = curr_hour * 60 + curr_min;
    curr_time = parseInt(curr_time/30);
    curr_time*=30;
    $('#start_time .time_min').val(curr_time);
    
    $("#end_time input").val('');
    $('#end_time .time_min').val(curr_time);
}
function clear_event_input(){
    $('#input_title').val('');
    $('#input_location').val('');
    $('#input_invites').val('');
    reset_start_time();
    
    $("#end_time input").val('');
    $('#input_message').val('');
    $("#input_public").attr("checked", false);
    $('#input_message').trigger('success');
    
    //$("#event_form tr.canHide").addClass("hidden");
}

function load_event(type, load_more, base_id){
    $("#load_more_box").hide();
    $("#loading_box").show();
    
    if(type == '') return false;
    console.log("load_type: "+type);
    
    var url='/api/event/get/'+type;
    if(load_more)
        url +="?base_id="+base_id;
        
    if(!load_more)
        $("div.stream.event_item").remove();
    
    var tokenValue = $("#csrf_token").text();
    var data ="&csrfmiddlewaretoken="+tokenValue;
    $.ajax({
		type : "POST",
		url : url,
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  $("#loading_box").hide();
		  if(json.success){
		      $("#event_list").attr('type',type);
		      
		      display_event(json.events);
		      
              if(json.load_more){
		          $("#load_more_box").show();
		      }else{
		          $("#load_more_box").hide();
		      }
		  }
		},
		error : function(data){
		  $("#loading_box").hide();
		  console.log(data);
		}
	});
}

function load_more_event(){
    var base_id = $("#event_list").find(".stream.event_item").last().attr("base_id");
    if (base_id == undefined || base_id == ''){
        return false;
    }
    var type = $("#event_list").attr('type');
    
    load_event(type, true, base_id);

}


function display_event(events){
    for(var i=0; i<events.length; i++){
        
        var event=events[i];
        //console.log(event);
        
        
        var event_layout= $("div.stream.template").clone();
        event_layout.removeClass("template");
        event_layout.addClass("event_item");
        event_layout.attr('id','event_'+event.id);
        event_layout.attr('base_id',+event.base_id);
        event_layout.find('.user_link').attr('href','/user/'+event.host);
        event_layout.find('.from a').text(event.host);
        event_layout.find('.from span.author_name').text(event.host_name);

        event_layout.find('.event_title').html(nl2br(event.title));
        event_layout.find('.event_content').html(nl2br(event.contents));
        if(event.contents == ""){
            event_layout.find('.event_content').remove();
        }
        event_layout.find('.event_location').html("<b>Where? </b> "+event.location);
        event_layout.find('.start_time').html("<b>From</b> "+event.start_time);
        if(event.end_time != undefined && event.end_time != 'None'){
            event_layout.find('.end_time').html(" - <b>To</b> "+event.end_time);
        }
        
        if(event.public){
            event_layout.find('.public_info').text("공개된 이벤트 입니다.");
        }
        
        event_layout.find('abbr.event_time').text(humane_date(event.reg_date));
        event_layout.find('img.avatar.author').attr('src',event.host_picture);
        
        if(event.host == $("#user_name_info").text()){
            event_layout.find('.stream_element_delete.event').show();
            event_layout.find('.stream_element_delete.event').attr('event_id',event.id);
            event_layout.find('.stream_element_delete.event').click(function(){
                delete_event($(this));
            });
        }
        
        
        event_layout.find('span.comment_count_text').text(event.comments.length);
        if(event.comments.length == 0){
            event_layout.find('ul.comments.comment_count li span').text('댓글이 없습니다.');
            event_layout.find('ul.comments.comment_list').hide();
            event_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+event.id);
            event_layout.find("ul.comments.comment_count a.show_all").hide();
        }else{
            if (event.comments.length == 1){
                event_layout.find("ul.comments.comment_count a.show_all").hide();
            }
            event_layout.find('ul.comments.comment_count span span').text(event.comments.length);
            event_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+event.id);
        }

        
        for(var j=0; j<event.comments.length; j++){
            add_event_comment(event_layout, event.comments[j], j, event.comments.length);
        }
        
        $("#event_list").append(event_layout);
        event_layout.find(".comment_area").attr('id','comment_area_'+event.id);
        event_layout.find(".comment_submit").attr('id','comment_submit_'+event.id);

        event_layout.find(".comment_submit").click(function(){
                var id=$(this).attr('id').split('_')[2];
                update_event_comment(id);
        });
        event_layout.find("textarea").click(function(){
                var reply_btn = $(this).parent().parent().find('.submit_button');
                reply_btn.show();
        });    
        event_layout.find('textarea').elastic();
        
        event_layout.find('.content').attr('event_id',event.id);
        event_layout.find('.content').click(function(){
            location.href="/event/detail/"+$(this).attr('event_id');
        });
        
    }
}


function add_event_comment(event_layout, comment, index, total){
    var comment_layout= event_layout.find("li.comment.posted.template").clone();
    comment_layout.removeClass("template");
    comment_layout.find('p.comment_text').html(nl2br(comment.contents));
    comment_layout.find('abbr.comment_time').text(humane_date(comment.reg_date));
    comment_layout.find('.user_link').attr('href','/user/'+comment.author);
    comment_layout.find('img.avatar.author').attr('src',comment.author_picture);
    
    comment_layout.find('.from a').text(comment.author);
    comment_layout.find('.from span.author_name').text(comment.author_name);
    if(index <= total-3){
        comment_layout.hide();
    } 
    if(comment.author == $("#user_name_info").text()){
        comment_layout.css("border-left","3px solid #95BDED");
        comment_layout.find('.stream_element_delete').show();
        comment_layout.find('.stream_element_delete').attr('comment_id',comment.id);
        comment_layout.find('.stream_element_delete').click(function(){
            delete_event_comment($(this));
            return false;
        });
    }else{
        comment_layout.css("border-left","3px solid #F0F4F5");
        comment_layout.find('.stream_element_delete').remove();
    }
    event_layout.find('ul.comments.comment_list').append(comment_layout);
    return comment_layout;
}

function update_event_comment(event_id){
    var tokenValue = $("#csrf_token").text();

    var message = $("#comment_area_"+event_id).val();
    
    data= "message=" + message + "&event_id=" + event_id;
    data +="&csrfmiddlewaretoken="+tokenValue;
    
    $.ajax({
		type : "POST",
		url : "/api/event/update/comment/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  $("#comment_area_"+event_id).val("");
		  $('textarea#comment_area_'+event_id).trigger('success');
		  if(json.comment){
		      var event_layout=$("#event_"+event_id);
		      
		      event_layout.find('ul.comments.comment_list').show();
		      var this_index=$('ul.comment_list').find('li.comment.posted').length;
		      var comment_layout=add_comment(event_layout, json.comment, this_index,this_index+1);
		      comment_layout.hide();
		      comment_layout.slideToggle();
		      
		      change_comment_count(comment_layout, true);
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});
 
}

function delete_event(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var event_id=item.attr('event_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/event/delete/"+event_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            $("#event_"+event_id).slideToggle("",function(){
		      $(this).remove();
		    });
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function delete_event_comment(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var comment_id=item.attr('comment_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/event/comment/delete/"+comment_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  item.parent().parent().slideToggle("",function(){
		      change_comment_count($(this), false);
		      $(this).remove();
		  });
		},
		error : function(data){
		  console.log(data);
		}
	});
}




function show_event_detail(event_id){
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/event/detail/"+event_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            var detail_box = $('#event_detail_box');
            var event = json.event;
            detail_box.find('a.attend_btn').attr('event_id',event.id);
            detail_box.find('.event_title').text(event.title);
            detail_box.find('img.host_avatar').attr('src',event.host_picture);
            detail_box.find('.event_content').html(nl2br(event.contents));
            detail_box.find('.event_location').html("<b>Where? </b> "+event.location);
            detail_box.find('.start_time').html("<b>From</b> "+event.start_time);
            if(event.end_time != undefined && event.end_time != 'None'){
                detail_box.find('.end_time').html(" - <b>To</b> "+event.end_time);
            }
            
            if(!event.attend_open){
                $(".attend_action").remove();
            }else{
                var description=detail_box.find(".attending_status");
                $(".attend_action .attend_btn").show();
                if(event.attending == 'yes'){
                    description.text("회원님은 참석 중입니다.");
                    $(".attend_action .yes_btn").hide();
                }else if(event.attending == 'no'){
                    description.text("회원님은 참석 중이 아닙니다.");
                    $(".attend_action .no_btn").hide();
                }else if(event.attending == 'wait'){
                    description.text("회원님은 참석 여부를 보류 하셨습니다.");
                    $(".attend_action .wait_btn").hide();
                }else{
                    description.text("회원님은 아직 응답하지 않으셨습니다.");
                }
            }
            
            for(var a=0; a<event.attendees.length; a++){
                var layout = '<li class="attendee" username="'+event.attendees[a].username+'"><img src="'+event.attendees[a].picture+'" /></li>';
                detail_box.find(".attendees_list ul").append(layout);
            }
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function attend_event(item, type){
    var event_id = item.attr('event_id');
    
    
    
    var url='/api/event/attend/'+event_id;
    var tokenValue = $("#csrf_token").text();
    var data ="attend_type="+type+"&csrfmiddlewaretoken="+tokenValue;
    $.ajax({
		type : "POST",
		url : url,
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  if(json.success){
		    var attendee_list=$("#attendees_list");
		    
		    var description=$("#attend_info .attending_status");
		    $("#attend_info .attend_action .attend_btn").show();
		    if(type == 'yes'){
		        var user_name = $("#user_name_info").text();
		        var user_picture = $("#user_picture_info").text();
		        attendee_list.append('<li class="attendee" username="'+user_name+'"><img src="'+user_picture+'" /></li>').hide().fadeIn();
                description.text("참가 하셨습니다.");
                $(".attend_action .yes_btn").hide();
            }else if(type == 'no'){
                var user_name = $("#user_name_info").text();
                attendee_list.find("li[username='"+user_name+"']").fadeOut(1000,function(){
                    $(this).remove();
                });
                description.text("참가 하지 않으시고 계십니다.");
                $(".attend_action .no_btn").hide();
            }else if(type == 'wait'){
                var user_name = $("#user_name_info").text();
                attendee_list.find("li[username='"+user_name+"']").fadeOut(1000,function(){
                    $(this).remove();
                });
                description.text("참가 보류 하셨습니다.");
                $(".attend_action .wait_btn").hide();
            }else{
                description.text("회원님은 아직 응답하지 않으셨습니다.");
            }
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});   
    
    
}


function delete_detail_event(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var event_id=item.attr('event_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/event/delete/"+event_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            location.href="/event/";
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function delete_detail_event_comment(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var comment_id=item.attr('comment_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/event/comment/delete/"+comment_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  item.parent().parent().slideToggle("",function(){
		      $(this).remove();
		      $(".comment_count_text").text($(".comment_list").find("li.comment.posted").length - 1);
		  });
		},
		error : function(data){
		  console.log(data);
		}
	});
}