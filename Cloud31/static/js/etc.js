function show_user_menu(event){
    $("#menu_list").toggle();
    
    if($("#menu_list").is(":visible")){
        $("#user_box").addClass("open");
    }else{
        $("#user_box").removeClass("open");;
    }
    
    event.stopPropagation();
}

function hide_user_menu(){
    $("#menu_list").hide();
    $("#user_box").removeClass("open");;
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