function upload_feed(){
    $("#update_btn").hide();
    $("div.item.update div.loading").show();
    
    var attach_list='';
    var count=$("#attach_list").find('li').length;
    $("#attach_list").find('li').each(function(i, val){
        if (i == count-1)
            attach_list+=$(this).text();
        else
            attach_list+=$(this).text()+'.';
    });
    console.log(attach_list);
    
    var message=$('textarea#feed_message_input').val();
    var location_info='';
    
    tokenValue = $("#csrf_token").text();
    
    data= "message=" + message + "&attach_list=" + attach_list + "&location_info="+location_info;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/feed/update/",
		data : data,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
		  $("#update_btn").show();
          $("div.item.update div.loading").hide();
          
          clear_feed_input();
		},
		error : function(data){
		  console.log(data);
		}
	});
    
}

function clear_feed_input(){
    $('textarea#feed_message_input').val("");
    
    $("#attach_list").find('li').each(function(i, val){
        $(this).remove();
    });
    
    $(".qq-upload-list").find('li').each(function(){
        $(this).remove();
    })
}