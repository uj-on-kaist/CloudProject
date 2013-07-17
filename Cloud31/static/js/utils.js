/** ******* 1. Pretty Date *************** */
/*
 * JavaScript Pretty Date Copyright (c) 2008 John Resig (jquery.com) Licensed
 * under the MIT license.
 */

// Takes an ISO time and returns a string representing how
// long ago the date represents.

function humane_date(time){
	var d = new Date((time || "").replace(/-/g,"/").replace(/[TZ]/g," "));
	return d.getFullYear() + "년 " + (d.getMonth() + 1) + "월 " + d.getDate() + "일 " + d.getHours() + "시 " + d.getMinutes() + "분";
}
/*
function humane_date(time){
	
	var date = new Date((time || "").replace(/-/g,"/").replace(/[TZ]/g," ")),
		diff = (((new Date()).getTime() - date.getTime()) / 1000),
		day_diff = Math.floor(diff / 86400);
	if ( isNaN(day_diff) || day_diff < 0 || day_diff >= 31 )
		return;

	return day_diff == 0 && (
			diff < 60 && "just now" ||
			diff < 120 && "1 minute ago" ||
			diff < 3600 && Math.floor( diff / 60 ) + " minutes ago" ||
			diff < 7200 && "1 hour ago" ||
			diff < 86400 && Math.floor( diff / 3600 ) + " hours ago") ||
		day_diff == 1 && "Yesterday" ||
		day_diff < 7 && day_diff + " days ago" ||
		day_diff < 31 && Math.ceil( day_diff / 7 ) + " weeks ago";
}*/


function start_loading(item){
    item.parent().find('.loading').show();
    item.hide();
}

function finish_loading(item){
    item.removeAttr('disabled');
    item.parent().find('.loading').hide();
    item.show();
}


function nl2br (str, is_xhtml) {   
    var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';    
    return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ breakTag +'$2');
}

function remove_special(input){
    var result=input;
    var re = /[\{\}\[\]\/?.,;:|\)*~`!^\+┼<>@\#$%&\'\"\\\(\=]/gi;
    return result.replace(re, "");
}


function setSelectionRange(input, selectionStart, selectionEnd) {
  if (input.setSelectionRange) {
    input.focus();
    input.setSelectionRange(selectionStart, selectionEnd);
  }
  else if (input.createTextRange) {
    var range = input.createTextRange();
    range.collapse(true);
    range.moveEnd('character', selectionEnd);
    range.moveStart('character', selectionStart);
    range.select();
  }
}

function setCaretToPos (input, pos) {
  setSelectionRange(input, pos, pos);
}

function cursor_postion_text(item){
    var result = new Object();
    
    var position = item.getCursorPosition();
    var str = item.val();
    
    //var currentChar = str.charAt(position);
    
    var left=position-1;
    var right=position;
 
    while(str.charAt(right) != ' ' && str.charAt(right) != '\n' && right < str.length){
        right++;
    }
    while(str.charAt(left) != ' ' && str.charAt(left) != '\n' && left >= 0){
        left--;
    }
    
    
    result.text=str.substring(left+1,right);
    result.left=left+1;
    result.right=right;
    return result;
}


function detect_auto_complete(textarea){
    var result = cursor_postion_text(textarea);
    
    var text=result.text;
    
    if(text.length <= 1){
        
        if(text.charAt(0) == '@' || text.charAt(0) == '#'){
            if(text.charAt(0) == '@'){
                $("#auto_complete_list .type_msg").text("Type search keyword for User...");
                $('#auto_complete_list li.add').hide();
            }else{
                $("#auto_complete_list .type_msg").text("Type search keyword for Topic...");
            }
            $("#auto_complete_list .type_msg").show();
            $("#auto_complete_list .search_msg").hide();
            $("#auto_complete_list li.list_item").remove();
            
            if($("#location_selector").length != 0){
                if($("#location_selector").is(":visible")){
                    $("#auto_complete_list").css("top","-286px");
                }else{
                    $("#auto_complete_list").css("top","-41px");
                }
            }
            
            
            $("#auto_complete_list").show();
        }else{
            $("#auto_complete_list li.list_item").remove();
            $("#auto_complete_list").hide();
        }
        
        return false;
    }
    
    var keyword = '';
    var type='';
    if(text.charAt(0) == '@'){
        //console.log("@ user detect:"+text.substring(1));
        keyword = text.substring(1);
        type = 'user';
    }else if(text.charAt(0) == '#'){
        //console.log("# topic detect:"+text.substring(1));
        keyword = text.substring(1);
        type = 'topic';
    }else{
        return false;
    }
    
    var url='/api/search/'+type+'?q='+encodeURI(keyword);
    $.ajax({
		type : "GET",
		url : url,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  if(json.success){
		      //console.log(json.items);
		      display_auto_complete(type,json.items, result.left, result.right, keyword, textarea);
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});
    
}

function display_auto_complete(type,items, left, right, keyword, textarea){
    $("#auto_complete_list .type_msg").hide();
    $("#auto_complete_list .search_msg").show();
    if(!$("#auto_complete_list").is(":visible")){
        $("#auto_complete_list").show();
    }
    $("#auto_complete_list li.list_item").remove();
    
    if(type == 'topic'){
        $('#auto_complete_list li.add .topic_name').text("#"+keyword);
        $('#auto_complete_list li.add').attr('left',left);
        $('#auto_complete_list li.add').attr('right',right);
        $('#auto_complete_list li.add').show();
    }
    if(type == 'user' && items.length == 0){
         $("#auto_complete_list .search_msg").text("User Not found for \""+keyword+"\"");
    }else if(type == 'topic' && items.length == 0){
         $("#auto_complete_list .search_msg").text("Topic Not found for \""+keyword+"\"");
    }else{
        $("#auto_complete_list .search_msg").text("Search Result");
    }
    for(var i=0; i<items.length; i++){
        var item=items[i];
        
        if(type == 'user'){
            $('#auto_complete_list li.add').hide();
            
            var layout= $("#auto_complete_list li.user_item.template").clone();
            
            layout.removeClass("template");
            layout.addClass("list_item");
            layout.attr('left',left);
            layout.attr('right',right);
            layout.find(".user_picture img").attr("src",item.picture);
            layout.find(".user_picture img").attr("title","@"+item.username);
            layout.find(".user_name").text("@"+item.username);
            layout.find(".user_real_name").text(item.name);
            
            layout.click(function(){
                var left=$(this).attr('left');
                var right=$(this).attr('right');
                replace_input_text(textarea, $(this).find('.user_name').text(),left, right);
            });
            $('#auto_complete_list li.add').before(layout);
            
        }else{
            
            
            var layout= $("#auto_complete_list li.topic_item.template").clone();
            
            layout.removeClass("template");
            layout.addClass("list_item");
            layout.attr('left',left);
            layout.attr('right',right);
            layout.find(".topic_name").text("#"+item.topic_name);
            
            layout.click(function(){
                var left=$(this).attr('left');
                var right=$(this).attr('right');
                replace_input_text(textarea, $(this).find('.topic_name').text(),left, right);
            });

            $('#auto_complete_list li.add').before(layout);
        }
    }
    $("#auto_complete_list li.list_item").highlight(keyword);
}

function replace_input_text(item, text, left, right){
    //console.log("["+left+"/"+right+"]hi "+text);
    var str = item.val();
    
    var new_str = str.substring(0,left);
    new_str+=text;
    new_str+=str.substring(right,str.length);
    new_str+=' ';
    item.val(new_str);
    setCaretToPos(item[0], left+text.length+1);
}
