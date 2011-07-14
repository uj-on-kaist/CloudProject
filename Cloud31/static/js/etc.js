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







function detect_email_list(){
    var text = $("#email_list_input").val();
    var re = /[\{\}\[\]\/?,;:|\)*~`!^\+┼<>\#$%&\'\"\\\(\=\n\r\tㄱ-ㅎ가-힣]/gi;
    text = text.trim().replace(re, " ");
    
    var arr = text.replace(/\s{2,}/g, ' ').split(" ");
    var email_list = new Array();
    var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    for(var k=0; k < arr.length ; k++){
        var item = arr[k];
        if (filter.test(item)) {
            email_list.push(item);
            var email_layout = "<li class='ui-corner-all' onclick='$(this).remove();'>"+item+"</li>";
            $("#detect_list ul").append(email_layout);
        }
    }
}

function send_invites_admin(item){
    item.attr('disabled','disabled');
    var email_list="";
    $("#detect_list ul li").each(function(){
        var email = $(this).text();
        email_list+=email+"|";
    });
    console.log("Send Invites to : "+email_list);
    
    if(email_list == ""){
        alert('Error: Empty Email List');
        item.removeAttr('disabled');
        return false;
    }
    
    var tokenValue = $("#csrf_token").text();
    data= "email_list=" + email_list + "&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/admin/invite/send/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  item.removeAttr('disabled');
          if(json.success){
            alert("Invite Successful.");
            //$('#detect_list').hide(); $('#detect_list ul').remove(); $('#email_list_input').val('');
          }else{
            alert("Error: Invite Failed.");
          }
          item.removeAttr('disabled');
          
		},
		error : function(data){
		  console.log(data);
		  alert('Error Occured');
		}
	});
    
}