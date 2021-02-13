$(function() {
    $.ajax({url: "api/user", 
        success: function(result) {
            $("#welcome").html('Hello, ' + result.firstName + ' ' + result.lastName + '! Welcome to IstioCon 2021!');
        },

    }).fail(function(jqXHR, textStatus, error) {
        $("#welcome").html('Hello, Stranger! Welcome to IstioCon 2021!');
        alert('Uh oh! Something broke! Error Code: ' + jqXHR.status);
    });
});