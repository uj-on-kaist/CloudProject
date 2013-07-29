function upload_tab_feed(tab_id,item){
    item.attr('disabled','disabled');
    
    start_loading(item);
    
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
    if($("#location_info_box").attr("attached") == "true"){
        var lat = $("#lat_value").text().substring(0,14);
        var lng = $("#lng_value").text().substring(0,14);
        location_info = lat+"|"+lng;
    }
    
    var tokenValue = $("#csrf_token").text();
    
    if(message == ""){
        finish_loading(item);
        return false;
    }
    
    data= "tab=" + tab_id +"&message=" + encodeURIComponent(message) + "&attach_list=" + attach_list + "&location_info="+location_info;
    data +="&csrfmiddlewaretoken="+tokenValue;
    console.log(data);
	$.ajax({
		type : "POST",
		url : "/api/tab/feed/update/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  item.removeAttr('disabled');
          if(json.success){
            clear_feed_input();
            var type = $("#tab_id").attr('tab');
            load_tab_feed(type);
          }
          
          finish_loading(item);
		},
		error : function(data){
		  console.log(data);
		  alert('Error Occured');
		}
	});
    
}

function load_tab_feed(type, load_more, base_id){
    $("#load_more_box").hide();
    $("#loading_box").show();
    
    if(type == '') return false;
    console.log("load_type: "+type);
    
    var url="/api/tab/feed/load?tab="+type;
    
    if(load_more){
        url+="&base_id="+base_id;
        if($("#feed_sort_method").length != 0){
            url+="&sort="+$("#feed_sort_method").val();
        }
    }else if($("#feed_sort_method").length != 0){
        url+="&sort="+$("#feed_sort_method").val();
    }
    
    if(!load_more)
        $("div.stream.feed_item").remove();

    $.ajax({
		type : "GET",
		url : url,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  $("#loading_box").hide();
		  if(json.success){
		      $("#feed_list").attr('type',type);
		      
		      display_feeds(json.feeds, 'tab');
		      
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


function load_tab_more(){
    var base_id = $("#feed_list").find(".stream.feed_item").last().attr("base_id");
    if (base_id == undefined || base_id == ''){
        return false;
    }
    var type = $("#tab_id").attr('tab');
    console.log(base_id, type);
    
    load_tab_feed(type, true, base_id);

}

function update_tab_comment(feed_id){
    var tokenValue = $("#csrf_token").text();
    
    
    var message = $("#comment_area_"+feed_id).val();
    
    data= "message=" + encodeURIComponent(message) + "&feed_id=" + feed_id;
    data +="&csrfmiddlewaretoken="+tokenValue;
    
    $.ajax({
		type : "POST",
		url : "/api/tab/feed/update/comment/",
		data : data,
		dataType : "JSON",
		cache : false,
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

function delete_tab_feed(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var feed_id=item.attr('feed_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/tab/feed/delete/"+feed_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
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

function delete_tab_comment(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var comment_id=item.attr('comment_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/tab/feed/comment/delete/"+comment_id,
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


function change_tab_sort_method(item){
    var val=item.val();    
    var type = $("#tab_id").attr('tab');
    load_tab_feed(type);
}