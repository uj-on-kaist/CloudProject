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
