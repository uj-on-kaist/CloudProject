function upload_feed(){
    
    var attach_list='';
    var count=$(".qq-upload-list").find('li').length;
    $(".qq-upload-list").find('li').each(function(i, val){
        var file_id = $(this).attr('id').split('#');
        if(file_id.length != 2)
            return false;
        if (i == count-1)
            attach_list+=file_id[1];
        else
            attach_list+=file_id[1]+'.';
    });
    console.log("Attach: " + attach_list);
    
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


function load_feed(type, load_more, base_id){
    if(type == '') return false;
    console.log("load_type: "+type);
    
    var url='';
    if(type == 'me'){
        url="/api/timeline/"+type;
    }else if(type.indexOf("user#") != -1){ 
        var user_name=type.split("#")[1];
        url="/api/feed/user/"+user_name;
    }else if(type.indexOf("at#") != -1){ 
        var user_name=type.split("#")[1];
        url="/api/feed/user_at/"+user_name;
        console.log("123");
    }else if(type.indexOf("topic#") != -1){
        var topic_name=type.split("#")[1];
        url="/api/feed/topic/"+topic_name;
    }else if(type.indexOf("favorite#") != -1){
        var user_name=type.split("#")[1];
        url="/api/feed/favorite/"+user_name;
    }else if(type.indexOf("company") != -1 || type.indexOf("notice") != -1){
        url="/api/feed/"+type;
    }else{
        return false;
    }
    
    if(load_more){
        url+="?base_id="+base_id;
    }

    $.ajax({
		type : "GET",
		url : url,
		dataType : "JSON",
		success : function(json) {
		  $("#loading_box").hide();
		  if(json.success){
		      $("#feed_list").attr('type',type);
		      if(!load_more)
		          $("div.stream.feed_item").remove();
		      display_feeds(json.feeds, type);
		      
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


function load_more(){
    var base_id = $("#feed_list").find(".stream.feed_item").last().attr("base_id");
    if (base_id == undefined || base_id == ''){
        return false;
    }
    var type = $("#feed_list").attr('type');
    console.log(base_id, type);
    
    $("#load_more_box").hide();
    $("#loading_box").show();
    load_feed(type, true, base_id);

}


function display_feeds(feeds, type){
    for(var i=0; i<feeds.length; i++){
        
        var feed=feeds[i];
        console.log(feed);
        
        var feed_layout= $("div.stream.template").clone();
        feed_layout.removeClass("template");
        feed_layout.addClass("feed_item");
        feed_layout.attr('id','feed_'+feed.id);
        feed_layout.attr('base_id',feed.base_id);
        feed_layout.find('.user_link').attr('href','/user/'+feed.author);
        feed_layout.find('.from a').text(feed.author);
        feed_layout.find('.from span.author_name').text(feed.author_name);
        feed_layout.find('.feed_content').html(nl2br(feed.contents));
        
        if(feed.favorite){
            feed_layout.find('.like_action a span.favor').hide();
            feed_layout.find('.like_action a span.unfavor').show();
            feed_layout.find('.like_action a').attr('feed_id',feed.id);
            
            feed_layout.find('.like_action a').click(function(){
                feed_like($(this), false);
                return false;
            });
        }else{
            feed_layout.find('.like_action a span.favor').show();
            feed_layout.find('.like_action a span.unfavor').hide();
            feed_layout.find('.like_action a').attr('feed_id',feed.id);
            feed_layout.find('.like_action a').click(function(){
                feed_like($(this), true);
                return false;
            });
        }
        
        feed_layout.find('abbr.feed_time').text(humane_date(feed.reg_date));
        feed_layout.find('img.avatar.author').attr('src','/picture/'+feed.author);

        display_files(feed.file_list, feed_layout);
        feed_layout.find("a.fancy_image").fancybox();
        
        
        if(feed.author == $("#user_name_info").text()){
            feed_layout.find('.stream_element_delete.feed').show();
            feed_layout.find('.stream_element_delete.feed').attr('feed_id',feed.id);
            feed_layout.find('.stream_element_delete.feed').click(function(){
                delete_feed($(this));
            });
        }
        
        
        
        
        feed_layout.find('.comment_action a').attr("feed_id",feed.id);
        feed_layout.find('.comment_action a').click(function(){
            $("#feed_"+$(this).attr("feed_id")+" ul.comments").show();
        });
        
        feed_layout.find('span.comment_count_text').text(feed.comments.length);
        if(feed.comments.length == 0){
            
            feed_layout.find('ul.comments.comment_count li span').text('댓글이 없습니다.');
            feed_layout.find('ul.comments.comment_list').hide();
            feed_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+feed.id);
            feed_layout.find("ul.comments.comment_count a.show_all").hide();
        }else{
            if (feed.comments.length == 1){
                feed_layout.find("ul.comments.comment_count a.show_all").hide();
            }
            feed_layout.find('ul.comments.comment_count span span').text(feed.comments.length);
            feed_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+feed.id);
        }
        feed_layout.find("ul.comments.comment_count a.show_all").click(function(){
                if($(this).text().indexOf('보기') != -1){
                    $(this).text('숨기기');
                    var id=$(this).attr('id').split('_')[2];
                    $('#feed_'+id+' ul.comments.comment_list li').show();
                }else{
                    $(this).text('모두 보기');
                    var id=$(this).attr('id').split('_')[2];
                    var total=$('#feed_'+id+' ul.comments.comment_list li').length;
                    $('#feed_'+id+' ul.comments.comment_list li').each(function(i){
                        $(this).hide();
                    });
                }
                return false;
        });
        
        
        
        
        
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


function display_files(file_list, feed_layout){
    for(var i=0; i<file_list.length; i++){
        var file = file_list[i];
        if(file.type == "img"){
            var image_layout = '<a class="fancy_image" href="'+file.url+'" onfocus="this.blur()">'+
                '<img  src="'+file.url+'">' +
                '</a>';
        
            feed_layout.find('.feed_attach_image').append(image_layout);
        }else{
            var file_layout = '<a class="attach_file" href="'+file.url+'" target=_blank onfocus="this.blur()">' +
                '<span class="ui_icon ui_icon_file_'+file.type+'" ></span>' +
                '<span class="">'+file.name+'</span>' +
            '</a>';
        
            feed_layout.find('.feed_attach').append(file_layout);
        }
    }
    
    if(feed_layout.find('.feed_attach a').length == 0){
        feed_layout.find('.feed_attach').remove();
    }
    if(feed_layout.find('.feed_attach_image a').length == 0){
        feed_layout.find('.feed_attach_image').remove();
    }        
    
}

function feed_like(item, action){
    var feed_id = item.attr('feed_id');
    //console.log("feed: "+feed_id+" / action: "+action);
    var url="/api/feed/favor/"+feed_id;
    if(!action){
        url="/api/feed/unfavor/"+feed_id;
    }
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : url,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		success : function(json) {
		  if(!action){
		    item.find('span.unfavor').hide();
            item.find('span.favor').show();
		  }else{
		    item.find('span.favor').hide();
            item.find('span.unfavor').show();
		  }
		  item.unbind('click');
		  item.click(function(){
                feed_like($(this), !action);
                return false;
          });
		},
		error : function(data){
		  console.log(data);
		}
	});
	
	return false;
}

function add_comment(feed_layout, comment, index, total){
    var comment_layout= feed_layout.find("li.comment.posted.template").clone();
    comment_layout.removeClass("template");
    comment_layout.find('p.comment_text').html(nl2br(comment.contents));
    comment_layout.find('abbr.comment_time').text(humane_date(comment.reg_date));
    comment_layout.find('.user_link').attr('href','/user/'+comment.author);
    comment_layout.find('img.avatar').attr('src','/picture/'+comment.author);
    
    var current_user = $("#user_name_info").text();
    comment_layout.find('img.current_user.avatar').attr('src','/picture/'+current_user);
    
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
            delete_comment($(this));
            return false;
        });
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
            $("#feed_"+feed_id).slideToggle("",function(){
		      $(this).remove();
		    });
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function delete_comment(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var comment_id=item.attr('comment_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/feed/comment/delete/"+comment_id,
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


function change_comment_count(item, increase){
    var count = item.parent().parent().find(".comment_count li span span");
    
    var new_count = parseInt(count.text())-1;
    if(increase){
        new_count = parseInt(count.text()) + 1;
    }
    if(new_count <= 1){
        if(new_count == 0){
            item.parent().parent().find(".comment_count li").text("댓글이 없습니다.");
        }else{
            count.text(new_count);
        }
        item.parent().parent().find(".comment_count li a").hide();
    }else{
        count.text(new_count);
        item.parent().parent().find(".comment_count li a").show();
        console.log(item.parent().parent().find(".comment_count li a"));
    }
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
		      
		      change_comment_count(comment_layout, true);
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



function delete_detail_feed(item){
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
            location.href="/feed/";
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function delete_detail_comment(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var comment_id=item.attr('comment_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/feed/comment/delete/"+comment_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
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


