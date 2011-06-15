function send_message(){
    var receivers_text = $('#input_users').val();
    var message = $('#input_message').val();
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


function load_message(type){
    console.log(type);
    
    $("#message_list").attr('type',type);
    
    $.ajax({
		type : "GET",
		url : "/api/message/get/"+type+"/",
		dataType : "JSON",
		success : function(json) {
		  
          if(json.success){
            $("div.stream.message_item").remove();
            display_messages(json.messages);
          }else{console.log(json);}
		},
		error : function(data){
		  console.log(data);
		}
	});
	
}



function display_messages(messages){
    for(var i=0; i<messages.length; i++){
        
        var message=messages[i];
        console.log(message);
        
        var message_layout= $("div.stream.template").clone();
        message_layout.removeClass("template");
        message_layout.addClass("message_item");
        message_layout.attr('id','message_'+message.id)
        message_layout.find('.user_link').attr('href','/user/'+message.author);
        message_layout.find('.from a').text(message.author);
        message_layout.find('.from span').text(message.receivers);
        message_layout.find('abbr.message_time').text(humane_date(message.reg_date));
        message_layout.find('img.avatar').attr('src','/picture/'+message.author);
        message_layout.find('.message_content').html(nl2br(message.contents));
        
        message_layout.find('.content').attr('message_id',message.id);
        message_layout.find('.content').click(function(){
            location.href="/message/"+$(this).attr('message_id')+"?type="+$("#message_list").attr('type');
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
