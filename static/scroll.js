// code adapted from w3schools for slide up on scroll

$(window).scroll(function() {
    $(".slideanim").each(function(){
        var pos = $(this).offset().top;

        var winTop = $(window).scrollTop();
        if (pos > winTop) {
            $(this).addClass("slide");
        }
    });
}); 

$(window).scroll(function() {
    $(".slideanim_right").each(function(){
        var pos = $(this).offset().top;

        var winTop = $(window).scrollTop();
        if (pos > winTop) {
            $(this).addClass("slide_right");
        }
    });
}); 
 