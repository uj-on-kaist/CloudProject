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
		    show_noti(json.notifications);
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
        
    }

}

function hide_noti(){
    $('#noti_list').hide();
    $('#noti_selector').removeClass("sel");
    $('#noti_selector').addClass($('#noti_selector').attr('status'));

}