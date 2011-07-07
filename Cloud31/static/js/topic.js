function favor_topic(topic_name){
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/topic/favor/"+topic_name,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  if(json.success){
		      $(".tab .topic_favor_action").hide();
              $(".tab .topic_unfavor_action").show();
              
              
              var topic_favor_layout = '<li class="menu_item topic_favor_item last" topic="'+topic_name+'">'+
        '<a href="/topic/{{topic}}"><p style="margin:0; padding:0; float:left; width:130px; overflow:hidden;">#'+topic_name+'</p></a>'+
         '<a href="#" class="del_btn" style="float:right;margin-top:7px;" onclick="unfavor_topic(\''+topic_name+'\'); return false;"><img alt="Deletelabel" src="/static/image/deletelabel.png?1307079878"></a>'+
    '</li>';
              
              $("#topic_favor_list li").last().removeClass('last');
              
              console.log(topic_favor_layout);
              $("#topic_favor_list").append(topic_favor_layout);
              $("#topic_favor_list li.last").hide();
              $("#topic_favor_list li.last").fadeIn(500);
		  }
		},
		error : function(data){
		  console.log(data);
		}
   });
   
   
}

function unfavor_topic(topic_name){
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/topic/unfavor/"+topic_name,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  if(json.success){
		      $(".tab .topic_favor_action").show();
              $(".tab .topic_unfavor_action").hide();
              
              $(".topic_favor_item[topic='"+topic_name+"']").fadeOut(500,function(){
                $(this).remove();
              });
		  }
		},
		error : function(data){
		  console.log(data);
		}
   });
}