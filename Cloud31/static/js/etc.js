function show_user_menu(event){
    $("#menu_list").toggle();
    $("#menu_list").width($("#user_box").width()+24);
    if($("#menu_list").is(":visible")){
        $("#user_box").addClass("open");
        
        $("#user_box").find("span.ui_icon").removeClass("ui_icon_arrow_white");
        $("#user_box").find("span.ui_icon").addClass("ui_icon_arrow_black");
    }else{
        $("#user_box").removeClass("open");
        
        $("#user_box").find("span.ui_icon").removeClass("ui_icon_arrow_black");
        $("#user_box").find("span.ui_icon").addClass("ui_icon_arrow_white");
    }
    
    event.stopPropagation();
}

function hide_user_menu(){
    $("#menu_list").hide();
    $("#user_box").removeClass("open");
    
    $("#user_box").find("span.ui_icon").removeClass("ui_icon_arrow_black");
    $("#user_box").find("span.ui_icon").addClass("ui_icon_arrow_white");
}


function detail_feed_like(item, action){
    var feed_id = item.attr('feed_id');
    console.log("feed: "+feed_id+" / action: "+action);
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
		  if(action){
            $("span.favor").hide();
            $("span.unfavor").show();
          }else{
            $("span.favor").show();
            $("span.unfavor").hide();
          }
		},
		error : function(data){
		  console.log(data);
		}
	       });
	
            
}

function select_this_tab(item){
    item.parent().parent().find(".tab_item").removeClass("selected");
    item.addClass("selected");
    return false;
}
