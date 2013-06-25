
function update_poll_comment(poll_id){
    var tokenValue = $("#csrf_token").text();

    var message = $("#comment_area_"+poll_id).val();
    
    data= "message=" + message + "&poll_id=" + poll_id;
    data +="&csrfmiddlewaretoken="+tokenValue;
    
    $.ajax({
		type : "POST",
		url : "/api/poll/update/comment/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  $("#comment_area_"+poll_id).val("");
		  $('textarea#comment_area_'+poll_id).trigger('success');
		  if(json.comment){
		      var event_layout=$("#poll_"+poll_id);
		      
		      event_layout.find('ul.comments.comment_list').show();
		      var this_index=$('ul.comment_list').find('li.comment.posted').length;
		      var comment_layout=add_comment(event_layout, json.comment, this_index,this_index+1);
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


function delete_detail_poll(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var poll_id=item.attr('poll_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/poll/delete/"+poll_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            location.href="/poll/";
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function delete_detail_poll_comment(item){
    var answer = confirm ("Really Delete?");
    if (!answer)
        return false;

    var comment_id=item.attr('comment_id');
    var tokenValue = $("#csrf_token").text();
    $.ajax({
		type : "POST",
		url : "/api/poll/comment/delete/"+comment_id,
		data : "&csrfmiddlewaretoken="+tokenValue,
		dataType : "JSON",
		cache : false,
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




function register_poll(item){
    item.attr('disabled','disabled');
    start_loading(item);
    
    var title=$("#input_title").val();
    if(title == ""){
        finish_loading(item);
        return false;
    }
    
    var detail=$("#input_detail").val();

    var options = "";
    var option_count = 0;
    $(".option_item").each(function(i){
        var option_text = $(this).find(".option_text").val();
        if(option_text == "" || option_text == undefined){
            ;
        }else{
            options+="&option"+i+"="+option_text;
            option_count++;
        }
    });
    
    if(options.length == 0){
        finish_loading(item);
        return false;
    }
    
    console.log(title);
    console.log(detail);
    console.log(options);
    
    var tokenValue = $("#csrf_token").text();
    
    var data = "title=" + title + "&detail=" + detail;
    data += "&option_count=" + option_count + options;
    data +="&csrfmiddlewaretoken="+tokenValue;
    
	$.ajax({
		type : "POST",
		url : "/api/poll/register/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            document.location.href='/poll/'
          }else{
            finish_loading(item);
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
    
    finish_loading(item);
    
}
function add_poll_item(item){
    var poll_item_layout = $("#option_template").clone();
    poll_item_layout.addClass("option_item");
    poll_item_layout.attr("id","");
    item.before(poll_item_layout);
}


function calculate_poll_options(){
    var total_answers = 0;
    
    $(".option_item").each(function(){
        total_answers += parseInt($(this).attr("option_value"));
    });
    
    $(".option_total_text").text("Total 100% ("+total_answers+"/"+total_answers+")");
    
    $(".option_item").each(function(){
        var total_answers_value = total_answers;
        if(total_answers == 0){
            total_answers_value=1;
        }
        var this_value = parseInt($(this).attr("option_value"));
        var percent = this_value / total_answers_value;
        percent = (percent*100).toFixed(2);
        $(this).find(".option_percent").animate({"width":percent+"px"},"fast");
        $(this).find(".option_percent_text").text(percent+"% ("+this_value+"/"+total_answers+")");
    });
    
    
    
}

function option_selected(item){
    var option_id = item.attr("option_id");
    var checked = item.find("input").attr("checked");
    if(checked){
        checked = "1";
    }else{
        checked = "0";
    }
    console.log(checked);
    $.ajax({
		type : "GET",
		url : "/api/poll/option/"+option_id+"/"+checked,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
          if(json.success){
            var option_value = 0;
            if(json.checked == "1"){
                option_value = parseInt(item.attr("option_value")) + 1;
            }else{
                option_value = parseInt(item.attr("option_value")) - 1;
            }
            item.attr("option_value", option_value+"")
            calculate_poll_options();
          }else{
          }
		},
		error : function(data){
		  console.log(data);
		}
	});


    return true;
}