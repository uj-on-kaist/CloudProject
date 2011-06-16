function register_event(){
    var title=$("#input_title").val();
    
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
		success : function(json) {
		  console.log(json);
          if(json.success){
            clear_event_input();
            load_event($("#event_list").attr('type'));
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

function load_event(type){
    if(type == '') return false;
    console.log("load_type: "+type);
    
    var url='/api/event/get/'+type;
    var tokenValue = $("#csrf_token").text();
    var data ="&csrfmiddlewaretoken="+tokenValue;
    $.ajax({
		type : "POST",
		url : url,
		data : data,
		dataType : "JSON",
		success : function(json) {
		  if(json.success){
		      $("#event_list").attr('type',type);
		      $("div.stream.event_item").remove();
		      display_event(json.events);
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});
}


function display_event(events){
    for(var i=0; i<events.length; i++){
        
        var event=events[i];
        console.log(event);
        
        
        var event_layout= $("div.stream.template").clone();
        event_layout.removeClass("template");
        event_layout.addClass("event_item");
        event_layout.attr('id','event_'+event.id);
        event_layout.attr('id','event_'+event.id);
        event_layout.find('.user_link').attr('href','/user/'+event.host);
        event_layout.find('.from a').text(event.host);
        event_layout.find('.from span.author_name').text(event.host_name);

        event_layout.find('.event_title').html(nl2br(event.title));
        event_layout.find('.event_content').html(nl2br(event.contents));
        event_layout.find('.event_location').html("<b>Where? </b> "+event.location);
        event_layout.find('.start_time').html("<b>From</b> "+event.start_time);
        if(event.end_time != undefined){
            event_layout.find('.end_time').html(" - <b>To</b> "+event.end_time);
        }
        
        if(event.public){
            event_layout.find('.public_info').text("공개된 이벤트 입니다.");
        }
        
        event_layout.find('abbr.event_time').text(humane_date(event.reg_date));
        event_layout.find('img.avatar.author').attr('src','/picture/'+event.host);
        
        if(event.host == $("#user_name_info").text()){
            event_layout.find('.stream_element_delete.event').show();
            event_layout.find('.stream_element_delete.event').attr('event_id',event.id);
            event_layout.find('.stream_element_delete.event').click(function(){
                delete_event($(this));
            });
        }
        
        
        event_layout.find('.comment_action a').attr("event_id",event.id);
        event_layout.find('.comment_action a').click(function(){
            $("#event_"+$(this).attr("event_id")+" ul.comments").show();
        });
        
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
        event_layout.find("ul.comments.comment_count a.show_all").click(function(){
                if($(this).text().indexOf('보기') != -1){
                    $(this).text('숨기기');
                    var id=$(this).attr('id').split('_')[2];
                    $('#event_'+id+' ul.comments.comment_list li').show();
                }else{
                    $(this).text('모두 보기');
                    var id=$(this).attr('id').split('_')[2];
                    var total=$('#event_'+id+' ul.comments.comment_list li').length;
                    $('#event_'+id+' ul.comments.comment_list li').each(function(i){
                        $(this).hide();
                    });
                }
                return false;
        });
        
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
        
        
    }
}

function add_event_comment(event_layout, comment, index, total){
    var comment_layout= event_layout.find("li.comment.posted.template").clone();
    comment_layout.removeClass("template");
    comment_layout.find('p.comment_text').html(nl2br(comment.contents));
    comment_layout.find('abbr.comment_time').text(humane_date(comment.reg_date));
    comment_layout.find('.user_link').attr('href','/user/'+comment.author);
    comment_layout.find('img.avatar.author').attr('src','/picture/'+comment.author);
    
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