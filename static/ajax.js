$(function(){
    var val1 = $("#branch_select").val()
    //console.log(val1)
    if(val1 === '-1'){
        $(".brank_target ").prop('disabled', true);
    }

    $("#branch_select").change(function(){
        var val1 = $(this).val()
        //console.log(val1);
        if(val1 === '-1'){
            $(".brank_target ").prop('disabled', true);
        }
        else{
            $(".brank_target ").prop('disabled', false);
        
            $.ajax(
                '/ajax', 
                {
                    type: 'POST',
                    data: {'val': val1},
                    dataType: 'json'
                },

            ).done(function(data){
                if(data['result']){
                    console.log(data['result'])
                    $("#discuss").val('True')
                    $("#discuss").prop('disabled', true);
                }else{
                    $("#discuss").val('False')
                    $("#discuss").prop('disabled', false);
                }
            })
            .fail(function(){
                console.log("false")
            });
        }
    });
});

