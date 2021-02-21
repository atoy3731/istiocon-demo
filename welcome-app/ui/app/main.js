$(function() {
    $.ajax({url: "api/user", 
        success: function(result) {
            if (result.random) {
                $("#welcome").html("Hello, Stranger! I still don't know who you are!");
            }
            else {
                $("#welcome").html('Hello, ' + result.firstName + ' ' + result.lastName + '! Welcome to IstioCon 2021!');
                $("#location").html('I hope all is well in ' + result.city + ', ' + result.state + ', ' + result.country + '!');
            }
        },
    }).fail(function(jqXHR, textStatus, error) {
        $("#welcome").html('Hello, Stranger! Welcome to IstioCon 2021!');
        alert('Uh oh! Something broke! Error Code: ' + jqXHR.status);
    });
});