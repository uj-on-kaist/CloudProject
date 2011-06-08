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
          if(json.success){
            clear_feed_input();
            var feed_type=$("#feed_list").attr('type');
            load_feed(feed_type);
          }
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



function load_feed(type){
    $.ajax({
		type : "GET",
		url : "/feed/"+type,
		dataType : "JSON",
		success : function(json) {
		  if(json.success)
		      display_feeds(json.feeds, type);
		      
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function display_feeds(feeds, type){
    $("div.stream.feed_item").remove();
    for(var i=0; i<feeds.length; i++){
        var feed=feeds[i];
        
        var feed_layout= $("div.stream.template").clone();
        feed_layout.removeClass("template");
        feed_layout.addClass("feed_item");
        feed_layout.attr('id','feed_'+feed.id)
        feed_layout.find('.user_link').attr('href','/user/'+feed.author);
        feed_layout.find('.from a').text(feed.author);
        feed_layout.find('.feed_content').html(feed.contents);
        feed_layout.find('abbr').text(humane_date(feed.reg_date));
        if(type == 'me'){
            feed_layout.find('.stream_element_delete').show();
            feed_layout.find('.stream_element_delete').attr('feed_id',feed.id);
            feed_layout.find('.stream_element_delete').click(function(){
                delete_feed($(this));
            });
        }
        
        $("#feed_list").append(feed_layout);
    }
}


function delete_feed(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var feed_id=item.attr('feed_id');
    
    tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/feed/delete/"+feed_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
          if(json.success){
            $("#feed_"+feed_id).remove();
            
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}