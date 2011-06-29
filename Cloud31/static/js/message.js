function send_message(){
    var receivers_text = $('#facebox #input_users').val();
    var message = $('#facebox #input_message').val();
    /*

    receivers_text = receivers_text.replace(/[^a-zA-Z 0-9]+/g,'');
    var receivers = receivers_text.split(' ');
    
    var receivers_list='';
    for(var i=0; i<receivers.length; i++){
        receivers_list+=receivers[i]+',';
    }

    
    console.log(receivers_list);
    */
    console.log(message);
    
    
    
    var tokenValue = $("#csrf_token").text();
    
    data= "message=" + message + "&receivers=" + receivers_text;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/api/message/update/",
		data : data,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
          if(json.success){
            clear_message_input();
            load_message($("#message_list").attr('type'));
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function clear_message_input(){
    $('#input_users').val('');
    $('#input_users').trigger('success');
    $('#input_message').val('');
    $('#input_message').trigger('success');
}


function load_message(type, load_more, base_id){
    console.log(type);
    
    var url="/api/message/get/"+type+"/";
    
    if (load_more){
        url+="?base_id="+base_id;
    }
    
    $.ajax({
		type : "GET",
		url : url,
		dataType : "JSON",
		success : function(json) {
		  $("#loading_box").hide();
          if(json.success){
            $("#message_list").attr('type',type);
            if(!load_more)
                $("div.stream.message_item").remove();
            display_messages(json.messages);
            
            
            if(json.load_more){
		          $("#load_more_box").show();
		    }else{
		          $("#load_more_box").hide();
		    }
		      
          }else{console.log(json);}
		},
		error : function(data){
		  $("#loading_box").hide();
		  console.log(data);
		}
	});
	
}

function load_more_message(){
    var base_id = $("#message_list").find(".stream.message_item").last().attr("base_id");
    if (base_id == undefined || base_id == ''){
        return false;
    }
    var type = $("#message_list").attr('type');
    
    
    $("#load_more_box").hide();
    $("#loading_box").show();
    load_message(type, true, base_id);

}



function display_messages(messages){
    for(var i=0; i<messages.length; i++){
        
        var message=messages[i];
        console.log(message);
        
        var message_layout= $("div.stream.template").clone();
        message_layout.removeClass("template");
        message_layout.addClass("message_item");
        message_layout.attr('id','message_'+message.id);
        message_layout.attr('base_id',+message.base_id);
        message_layout.find('.user_link').attr('href','/user/'+message.author);
        message_layout.find('.from a').text(message.author);
        message_layout.find('.from span').text(message.receivers);
        message_layout.find('abbr.message_time').text(humane_date(message.reg_date));
        message_layout.find('img.avatar').attr('src','/picture/'+message.author);
        message_layout.find('.message_content').html(nl2br(message.contents));
        
        message_layout.find('.content').attr('message_id',message.id);
        message_layout.find('.content').click(function(){
            location.href="/message/detail/"+$(this).attr('message_id')+"?type="+$("#message_list").attr('type');
        });
        
        if(message.author == $("#user_name_info").text()){
            message_layout.find('.stream_element_delete.message').show();
            message_layout.find('.stream_element_delete.message').attr('message_id',message.id);
            message_layout.find('.stream_element_delete.message').click(function(){
                delete_message($(this));
            });
        }
        
        
        $("#message_list").append(message_layout);
    }
}

function delete_message(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var message_id=item.attr('message_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/message/delete/"+message_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
          if(json.success){
            $("#message_"+message_id).slideToggle("",function(){
		      $(this).remove();
		    });
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}


function send_reply(message_id){
    var message = $('#reply_area_'+message_id).val();

    var tokenValue = $("#csrf_token").text();
    data= "message=" + message +"&message_id="+message_id;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/api/message/reply/update/",
		data : data,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
          if(json.success){
          
            var reply_layout = add_reply(json.reply);
            reply_layout.hide();
            reply_layout.slideToggle();
            
            $('#reply_area_'+message_id).val('');
            $('#reply_area_'+message_id).height(40);
          }
		},
		error : function(data){
		  console.log(data);
		}
	});

}

function add_reply(reply){
    var reply_layout= $("div.stream.template").clone();
    reply_layout.removeClass("template");
    reply_layout.attr('id','reply_'+reply.id);
    reply_layout.find('p.reply_contents').html(nl2br(reply.contents));
    reply_layout.find('abbr.reply_time').text(humane_date(reply.reg_date));
    reply_layout.find('.user_link').attr('href','/user/'+reply.author);
    reply_layout.find('img.avatar').attr('src','/picture/'+reply.author);
    reply_layout.find('.from a').text(reply.author);
    
    if(reply.author == $("#user_name_info").text()){
        //reply_layout.css("border-left","3px solid #95BDED");
        reply_layout.find('.stream_element_delete').show();
        reply_layout.find('.stream_element_delete').attr('reply_id',reply.id);
        reply_layout.find('.stream_element_delete').click(function(){
            delete_reply($(this));
        });
    }else{
        //reply_layout.css("border-left","3px solid #F0F4F5");
        reply_layout.find('.stream_element_delete').remove();
    }
    
    $("#message_reply_list").append(reply_layout);
    
    return reply_layout;
}


function delete_reply(item){
    
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var reply_id=item.attr('reply_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/message/reply/delete/"+reply_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
          if(json.success){
            $("#reply_"+reply_id).slideToggle("",function(){
		      $(this).remove();
		    });
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
	
}