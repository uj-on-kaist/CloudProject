function validate_userid(item){
    var userid = item.val();
    var input_desc = item.parent().find(".input_desc");
    console.log(userid);
    
    if(userid){
    
    }
    if(userid.length > 10){
        input_desc.text("10자 이하의 아이디를 입력해 주세요.");
        input_desc.show(); 
    }else{
        input_desc.hide();
    }
    
}
function validate_username(item){
    var username = item.val();
    var input_desc = item.parent().find(".input_desc");
    
    
    if(username.length > 10) { 
        input_desc.text("10자 이하의 이름을 사용해 주세오.");
        input_desc.show();
    } else{
        input_desc.hide();
    }
}

function validate_email(item) {
    var email = item.val();
    var input_desc = item.parent().find(".input_desc");
    var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    
    if (!filter.test(email)) {
        input_desc.text("올바른 이메일 주소를 입력해 주세요.");
        input_desc.show();
    }else{
        input_desc.hide();
    }
}


function validate_password(item){
    var password = item.val();
    var input_desc = item.parent().find(".input_desc");
    
    
    if(password.length > 12 || password.length < 6) { 
        input_desc.text("6자 이상 12자 이하의 비밀번호를 사용해 주세오.");
        input_desc.show();
    } else{
        input_desc.hide();
    }
}

function validate_password_equal(item){
    var password2 = item.val();
    var password1 = $("#id_password1").val();
    
    var input_desc = item.parent().find(".input_desc");
    
    
    if(password1 != password2) { 
        input_desc.text("비밀번호가 일치하지 않습니다.");
        input_desc.show();
    } else{
        input_desc.hide();
    }
}


function check_form(item){
    var all_valid=true;
    item.find("input").each(function(){
        if(all_valid && $(this).val() == ""){
            all_valid = false;
            var label = $(this).parent().find("label").text();
            var input_desc = $(this).parent().find(".input_desc");
            input_desc.text(label+"을 입력해 주세요.");
            input_desc.show();
        }
    });
    item.find(".input_desc").each(function(){
        if(all_valid && $(this).is(':visible')){
            all_valid = false;
        }
    });
    
    return all_valid;
}