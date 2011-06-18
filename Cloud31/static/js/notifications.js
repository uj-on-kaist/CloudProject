function get_notis_count(){
    $.ajax({
		type : "GET",
		url : "/api/noti/get/",
		dataType : "JSON",
		success : function(json) {
		  if(json.success){
		      if(json.notifications.length == 0){
		          $(".noti_count").text("");
		          $('#noti_selector').attr('status','nor');
		          $('#noti_selector').removeClass("sel");
                  $('#noti_selector').addClass("nor");
		      }else{
		          $('#noti_selector').attr('status','high');
		          $('#noti_selector').removeClass("nor");
		          $('#noti_selector').addClass("high");
		          $(".noti_count").text(json.notifications.length);
		      }
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function load_notis(){
    if($('#noti_list').is(":visible")){
        hide_noti();
        return false;
    }

    $.ajax({
		type : "GET",
		url : "/api/noti/get/",
		dataType : "JSON",
		success : function(json) {
		  if(json.success){
		      console.log(json.notifications);
		      show_noti(json.notifications);
		      if(json.notifications.length != 0)
		          $(".noti_count").text(json.notifications.length);
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});

    return false;
}
function show_noti(notis){
    $('#noti_list').show();
    $('#noti_list li.header').click(function(){
        return false;
    });
    $('#noti_selector').removeClass("nor high");
    $('#noti_selector').addClass("sel");
    
    $('#noti_list li.noti_item').remove();
    for(var i=0; i<notis.length; i++){
        var noti=notis[i];
        var noti_layout= $("#noti_list li.noti_item_template").clone();
        noti_layout.removeClass("noti_item_template");
        noti_layout.addClass("noti_item");
        noti_layout.find(".user_picture").attr("src","/picture/"+noti.sender);
        noti_layout.find(".message").html(noti.contents);
        noti_layout.find(".noti_time abbr").text(humane_date(noti.reg_date));
        console.log(noti_layout);
        $('#noti_list a.see_more').before(noti_layout);
    }

}

function hide_noti(){
    $('#noti_list').hide();
    $('#noti_selector').removeClass("sel");
    $('#noti_selector').addClass($('#noti_selector').attr('status'));

}