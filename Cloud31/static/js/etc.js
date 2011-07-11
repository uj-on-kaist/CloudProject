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
    stopEvent(event);
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
		cache : false,
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

function stopEvent(event){
    agent = jQuery.browser;
	if(agent.msie) {
		event.cancelBubble = true;
	} else {
		event.stopPropagation();
	}
}



new function($) {
$.fn.getCursorPosition = function() {
    var pos = 0;
    var el = $(this).get(0);
    // IE Support
    if (document.selection) {
        el.focus();
        var Sel = document.selection.createRange();
        var SelLength = document.selection.createRange().text.length;
        Sel.moveStart('character', -el.value.length);
        pos = Sel.text.length - SelLength;
    }
    // Firefox support
    else if (el.selectionStart || el.selectionStart == '0')
        pos = el.selectionStart;

    return pos;
}
}(jQuery);


function reloadSWF(name, url) {
  swfobject.embedSWF(
    	  "/static/open-flash-chart2.swf", name, 
    	  "525", "200", "9.0.0", "/static/expressInstall.swf",
    	  {"data-file":url}, {"wmode":"transparent"} );
  return false;
}

function accuSet(item,name, url){
    if(item.attr("checked") == "checked"){
        reloadSWF(name, url+"?accu=1");
    }else{
        reloadSWF(name, url+"?accu=0");
    }
}


function reloadSWFRange(item, name, url){
    var start = item.parent().find(".startpicker").val();
    var end = item.parent().find(".endpicker").val();
    var accu = 0;
    if(item.parent().find("input[type=checkbox]").attr("checked") == "checked"){
        accu = 1;
    }
    var requestURL = url+"?start="+start+"&end="+end+"&accu="+accu;
    console.log(requestURL);
    reloadSWF(name, encodeURIComponent(requestURL));
    
}

