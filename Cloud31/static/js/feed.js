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
    
    var tokenValue = $("#csrf_token").text();
    
    data= "message=" + message + "&attach_list=" + attach_list + "&location_info="+location_info;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/api/feed/update/",
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
    $('textarea#feed_message_input').trigger('success');
    
    $("#attach_list").find('li').each(function(i, val){
        $(this).remove();
    });
    
    $(".qq-upload-list").find('li').each(function(){
        $(this).remove();
    })
}



function load_feed(type){
    if(type == '') return false;
    

    var url='';
    if(type == 'me'){
        url="/api/timeline/"+type;
    }else if(type.indexOf("user#") != -1){ 
        var user_name=type.split("#")[1];
        url="/api/feed/user/"+user_name;
    }else if(type.indexOf("topic#") != -1){
        var topic_name=type.split("#")[1];
        url="/api/feed/topic/"+topic_name;
    }else{
        return false;
    }
    console.log(url);  
    $.ajax({
		type : "GET",
		url : url,
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
        feed_layout.find('.feed_content').html(nl2br(feed.contents));
        console.log(feed);
        
        feed_layout.find('abbr.feed_time').text(humane_date(feed.reg_date));
        feed_layout.find('img.avatar').attr('src','/picture/'+feed.author);
        
        var attach_count=feed.attach_files.split(',').length;
        if(feed.attach_files == ""){
            feed_layout.find('#attach_file_count').hide();
        }else{
            feed_layout.find('#attach_file_count span').text(attach_count);
        }
        if(type == 'me'){
            feed_layout.find('.stream_element_delete').show();
            feed_layout.find('.stream_element_delete').attr('feed_id',feed.id);
            feed_layout.find('.stream_element_delete').click(function(){
                delete_feed($(this));
            });
        }
        
        
        
        if(feed.comments.length == 0){
            feed_layout.find('ul.comments.comment_count li').text('댓글이 없습니다.');
            feed_layout.find('ul.comments.comment_list').hide();
            feed_layout.find("ul.comments.comment_count a.show_all").hide();
        }else{
            feed_layout.find('ul.comments.comment_count span').text(feed.comments.length);
            feed_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+feed.id);
            feed_layout.find("ul.comments.comment_count a.show_all").click(function(){
                if($(this).text().indexOf('보기') != -1){
                    $(this).text('숨기기');
                    var id=$(this).attr('id').split('_')[2];
                    $('#feed_'+id+' ul.comments.comment_list li').removeClass('hidden');
                }else{
                    $(this).text('모두 보기');
                    var id=$(this).attr('id').split('_')[2];
                    var total=$('#feed_'+id+' ul.comments.comment_list li').length;
                    $('#feed_'+id+' ul.comments.comment_list li').each(function(i){
                        $(this).attr('class',$(this).attr('class')+' hidden');
                    });
                    
                }
                
            });
        }
        for(var j=0; j<feed.comments.length; j++){
            add_comment(feed_layout, feed.comments[j], j, feed.comments.length);
        }

        $("#feed_list").append(feed_layout);
        feed_layout.find(".comment_area").attr('id','comment_area_'+feed.id);
        feed_layout.find(".comment_submit").attr('id','comment_submit_'+feed.id);
        feed_layout.find(".comment_submit").click(function(){
                var id=$(this).attr('id').split('_')[2];
                update_comment(id);
        });
        feed_layout.find("textarea").click(function(){
                var reply_btn = $(this).parent().parent().find('.submit_button');
                reply_btn.show();
        });    
        feed_layout.find('textarea').elastic();
    }
}

function add_comment(feed_layout, comment, index, total){
    var comment_layout= feed_layout.find("li.comment.posted.template").clone();
    comment_layout.removeClass("template");
    comment_layout.find('p.comment_text').html(nl2br(comment.contents));
    comment_layout.find('abbr.comment_time').text(humane_date(comment.reg_date));
    comment_layout.find('.user_link').attr('href','/user/'+comment.author);
    comment_layout.find('img.avatar').attr('src','/picture/'+comment.author);
    comment_layout.find('.from a').text(comment.author);
    
    if(index <= total-3){
        comment_layout.addClass('hidden');
    } 
    if(comment.author == $("#user_name_info").text()){
        comment_layout.css("border-left","3px solid #95BDED");
    }else{
        comment_layout.css("border-left","3px solid #F0F4F5");
        comment_layout.find('.stream_element_delete').remove();
    }
    feed_layout.find('ul.comments.comment_list').append(comment_layout);
    return comment_layout;
}

function delete_feed(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var feed_id=item.attr('feed_id');
    
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/feed/delete/"+feed_id,
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


function setLocationInfo(){
    $.facebox.close();
    $('#foo').bind('click', function() {
        $('#facebox #map_canvas').attr('id','target_map_canvas');
        initialize();
    });
}


function update_comment(feed_id){
    var tokenValue = $("#csrf_token").text();
    
    
    var message = $("#comment_area_"+feed_id).val();
    
    data= "message=" + message + "&feed_id=" + feed_id;
    data +="&csrfmiddlewaretoken="+tokenValue;
    
    $.ajax({
		type : "POST",
		url : "/api/feed/update/comment/",
		data : data,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
		  $("#comment_area_"+feed_id).val("");
		  $('textarea#comment_area_'+feed_id).trigger('success');
		  if(json.comment){
		      var feed_layout=$("#feed_"+feed_id);
		      
		      feed_layout.find('ul.comments.comment_list').show();
		      var this_index=$('ul.comment_list').find('li.comment.posted').length;
		      var comment_layout=add_comment(feed_layout, json.comment, this_index,this_index+1);
		      comment_layout.hide();
		      comment_layout.slideToggle();
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});

    
}

function show_all_comments(feed_id){
    $('#feed_'+feed_id+' ul.comment_list').find('li.comment.posted').removeClass('hidden');
}