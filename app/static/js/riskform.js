$(document).ready(function() {

    // $('#residential_status_cbs').attr("disabled", true);

    setHiddenValue();

    //var selected_text = $('#cus_business').val();
    let cus_business_text = $('#cus_business option:selected').text();
    //if (selected)

    if (cus_business_text == 'Others (please mention in details)') {
        let cus_business_others_score = parseInt($('#cus_business_others').val()) || 0;
        //let cus_business_text = $('#cus_business option:selected').text();
        $('#cus_business option:selected').val(cus_business_others_score);
    }

    var selected = $('#residential_status_cbs').val();

    if (selected > 1) {
        $('#foreign_div').show();
    } else {
        $('#foreign_div').hide();
    }

    /*$(document).on('change', '#cus_business', function() {
        // Does some stuff and logs the event to the console
        alert('test...')
    });

    $("body").on('change', '#cus_business', function() { // 2nd (B)
        // do your code here
        // It will filter the element "Input_Id" from the "body" and apply "onChange effect" on it
        alert('test...')
    });*/

    $('#cus_business').change(function() {
        //alert ('buisness change')
        var selected = $(this).val();
        //alert(selected);
        if (selected == 0) {
            //alert('log in...')
            $('#others_risk').show();
            let cus_business_others_score = parseInt($('#cus_business_others').val()) || 0;
            let cus_business_text = $('#cus_business option:selected').text();
            $('#cus_business option:selected').val(cus_business_others_score);
        } else {
            $('#others_risk').hide();
        }
    });




    $('body').on('change', '#cus_business_others', function() {

        let cus_business_others_score = parseInt($('#cus_business_others').val()) || 0;
        let cus_business_text = $('#cus_business option:selected').text();
        $('#cus_business option:selected').val(cus_business_others_score);


    });

    //cus_occupation_others

    $('body').on('change', '#cus_occupation_others', function() {

        let cus_occupation_others_score = parseInt($('#cus_occupation_others').val()) || 0;
        let cus_occupation_text = $('#cus_occupation_others option:selected').text();
        $('#cus_occupation option:selected').val(cus_occupation_others_score);


    });




    $('#residential_status_cbs').change(function() {

        var selected = $(this).val();
        //alert(selected);
        if (selected > 1) {
            //alert('log in...')
            $('#foreign_div').show();
        } else {
            $('#foreign_div').hide();
        }
    });




    $(document).on("click", "#addRisk", function(e) {
        e.preventDefault();

        $('#alertModal').on('shown.bs.modal', function () {
            $('#alertModal').trigger('focus')
        })

       

        $('#type_product_service').attr("disabled", false);
        
        $('#subjective_risk_type_val').attr("disabled", false);
        let btn_value = $(this).val();
        //alert(btn_value);
        if (btn_value == 'Approve') {
            btn_value = 'approved';
        } else {
            btn_value = 'pending';
        }
       
        $('#submit_button').val(btn_value);

        $('#confirm-button').on("click", function (){
            // do something
            $("#riskform").submit();
            
        });
        //alert('test');
        //$("#riskform").submit();

    });

    $(document).on("click", "#rejected", function(e) {
        e.preventDefault();
        $('#type_product_service').attr("disabled", false);
        let btn_value = $(this).val();

        $('#submit_button').val(btn_value);

        $("#riskform").submit();


    });




    //cancel_risk_link

    $(document).on("click", "#cancel_risk_link", function(event) {
        $('#subjective_risk_type_val').val('');

    });

    $(document).on("click", "#change_risk_link", function(event) {

        sub_transparency_risk =  $('#subjective_risk_type_val').val();
        
        //alert (sub_transparency_risk);
        if (sub_transparency_risk != 'High Risk'){
            //alert ('Empty');
            sub_transparency_risk = 'High Risk';
            $('#subjective_risk_div').show();
        }else {
            sub_transparency_risk = "";
            $('#subjective_risk_div').hide();
        }
        
        $('#subjective_risk_type_val').val(sub_transparency_risk);

        return false;

    });

    $(document).on("click", "#change_risk_btn", function(event) {

        var sub_transparency_risk = $('#sub_transparency_risk').val();
        var comments = $('#comments').val();
        $('#assesment_notes').val(comments);
        $('#subjective_risk_type_val').val(sub_transparency_risk);
        $('#exampleModal').modal('toggle');
        $("#exampleModal").modal('hide');
        return false;
        //$("#exampleModal").modal('hide');
    });


    $('#type_product_service').change(function() {
        let type_product_service_score = parseInt($('#type_product_service').val()) || 0;
        var type_product_service_text = $('#type_product_service option:selected').text();
        if (type_product_service_text == 'Choose option...') {
            type_product_service_text = ''
        }
        $('#producttype').val(type_product_service_text)

    });

    $('#on_boarding_channel').change(function() {
        let on_boarding_channel_score = parseInt($('#on_boarding_channel').val()) || 0;
        var on_boarding_channel_text = $('#on_boarding_channel option:selected').text();
        if (on_boarding_channel_text == 'Choose option...') {
            on_boarding_channel_text = ''
        }
        $('#onboardingchannel').val(on_boarding_channel_text)

    });

    $('#residential_status_cbs').change(function() {
        let residential_status_cbs_score = parseInt($('#residential_status_cbs').val()) || 0;
        var residential_status_cbs_text = $('#residential_status_cbs option:selected').text();
        if (residential_status_cbs_text == 'Choose option...') {
            residential_status_cbs_text = ''
        }
        $('#residentialstatus').val(residential_status_cbs_text)

    });


    $('#foreigncitizenshipscore').change(function() {
        //set foreigncitizenshipscore
        let foreigncitizenshipscore_score = parseInt($('#foreigncitizenshipscore').val()) || 0;
        var foreigncitizenshipscore_text = $('#foreigncitizenshipscore option:selected').text();
        if (foreigncitizenshipscore_text == 'Choose option...') {
            foreigncitizenshipscore_text = ''
        }

        if (foreigncitizenshipscore_text == 'Choose option...') {
            $('#foreignercountryinblacklist').val('')
        } else {
            $('#foreignercountryinblacklist').val(foreigncitizenshipscore_text)
        }

    });


    $('#relationship_risk_pepscore').change(function() {
        let relationship_risk_pepscore_score = parseInt($('#relationship_risk_pepscore').val()) || 0;
        var relationship_risk_pepscore_text = $('#relationship_risk_pepscore option:selected').text();
        if (relationship_risk_pepscore_text == 'Choose option...') {
            relationship_risk_pepscore_text = ''
        }

        $('#customerpep').val(relationship_risk_pepscore_text)


    });

    $('#relationship_risk_rpepscore').change(function() {
        let relationship_risk_rpepscore_score = parseInt($('#relationship_risk_rpepscore').val()) || 0;
        var relationship_risk_rpepscore_text = $('#relationship_risk_rpepscore option:selected').text();

        if (relationship_risk_rpepscore_text == 'Choose option...') {
            relationship_risk_rpepscore_text = ''
        }
        $('#customerrelatedtopep').val(relationship_risk_rpepscore_text)



    });

    $('#relationship_risk_cusipscore').change(function() {

        let relationship_risk_cusipscore_score = parseInt($('#relationship_risk_cusipscore').val()) || 0;
        var relationship_risk_cusipscore_text = $('#relationship_risk_cusipscore option:selected').text();
        if (relationship_risk_cusipscore_text == 'Choose option...') {
            relationship_risk_cusipscore_text = ''
        }

        $('#customerip').val(relationship_risk_cusipscore_text)


    });


    $('#cus_business').change(function() {
        //cus_business
        let cus_business_score = parseInt($('#cus_business').val()) || 0;
        var cus_business_text = $('#cus_business option:selected').text();
        if (cus_business_text == 'Choose option...') {
            cus_business_text = ''
        }
        $('#customerbusiness').val(cus_business_text);

    });





    $('#cus_occupation').change(function() {
        //cus_occupation
        //alert ('cus_occupation');
        let cus_occupation_score = parseInt($('#cus_occupation').val()) || 0;
        var cus_occupation_text = $('#cus_occupation option:selected').text();
        if (cus_occupation_text == 'Choose option...') {
            cus_occupation_text = ''
        }
        if (cus_occupation_text == 'Others'){
            $('#others_risk_occupation').show();
        }else {
            $('#others_risk_occupation').hide();
        }
        $('#customeroccupation').val(cus_occupation_text);


    });

    $('#transactional_risk').change(function() {
        //transactional_risk
        let transactional_risk_score = parseInt($('#transactional_risk').val()) || 0;
        var transactional_risk_text = $('#transactional_risk option:selected').text();
        if (transactional_risk_text == 'Choose option...') {
            transactional_risk_text = ''
        }
        $('#averageyearlytransaction').val(transactional_risk_text)


    });


    $('#transparency_risk').change(function() {

        let transparency_risk_score = parseInt($('#transparency_risk').val()) || 0;
        var transparency_risk_text = $('#transparency_risk option:selected').text();
        if (transparency_risk_text == 'Choose option...') {
            transparency_risk_text = ''
        }
        $('#crediblesourceoffund').val(transparency_risk_text);


    });

    //cus_business_others




    function setHiddenValue() {


        let type_product_service_score = parseInt($('#type_product_service').val()) || 0;
        var type_product_service_text = $('#type_product_service option:selected').text();
        if (type_product_service_text == 'Choose option...') {
            type_product_service_text = ''
        }
        $('#producttype').val(type_product_service_text)

        // set onboarding channel 
        let on_boarding_channel_score = parseInt($('#on_boarding_channel').val()) || 0;
        var on_boarding_channel_text = $('#on_boarding_channel option:selected').text();
        if (on_boarding_channel_text == 'Choose option...') {
            on_boarding_channel_text = ''
        }
        $('#onboardingchannel').val(on_boarding_channel_text)

        //set residential_status_cbs
        let residential_status_cbs_score = parseInt($('#residential_status_cbs').val()) || 0;
        var residential_status_cbs_text = $('#residential_status_cbs option:selected').text();
        if (residential_status_cbs_text == 'Choose option...') {
            residential_status_cbs_text = ''
        }
        $('#residentialstatus').val(residential_status_cbs_text)

        //set foreigncitizenshipscore
        let foreigncitizenshipscore_score = parseInt($('#foreigncitizenshipscore').val()) || 0;
        var foreigncitizenshipscore_text = $('#foreigncitizenshipscore option:selected').text();
        if (foreigncitizenshipscore_text == 'Choose option...') {
            foreigncitizenshipscore_text = ''
        }

        if (foreigncitizenshipscore_text == 'Choose option...') {
            $('#foreignercountryinblacklist').val('')
        } else {
            $('#foreignercountryinblacklist').val(foreigncitizenshipscore_text)
        }

        //relationship_risk
        let relationship_risk_pepscore_score = parseInt($('#relationship_risk_pepscore').val()) || 0;
        var relationship_risk_pepscore_text = $('#relationship_risk_pepscore option:selected').text();
        if (relationship_risk_pepscore_text == 'Choose option...') {
            relationship_risk_pepscore_text = ''
        }

        $('#customerpep').val(relationship_risk_pepscore_text)

        //relationship_risk_rpepscore
        let relationship_risk_rpepscore_score = parseInt($('#relationship_risk_rpepscore').val()) || 0;
        var relationship_risk_rpepscore_text = $('#relationship_risk_rpepscore option:selected').text();

        if (relationship_risk_rpepscore_text == 'Choose option...') {
            relationship_risk_rpepscore_text = ''
        }
        $('#customerrelatedtopep').val(relationship_risk_rpepscore_text)


        let relationship_risk_cusipscore_score = parseInt($('#relationship_risk_cusipscore').val()) || 0;
        var relationship_risk_cusipscore_text = $('#relationship_risk_cusipscore option:selected').text();
        if (relationship_risk_cusipscore_text == 'Choose option...') {
            relationship_risk_cusipscore_text = ''
        }

        $('#customerip').val(relationship_risk_cusipscore_text)

        //cus_business
        let cus_business_score = parseInt($('#cus_business').val()) || 0;
        var cus_business_text = $('#cus_business option:selected').text();
        if (cus_business_text == 'Choose option...') {
            cus_business_text = ''
        }
        $('#customerbusiness').val(cus_business_text)

        //cus_occupation

        let cus_occupation_score = parseInt($('#cus_occupation').val()) || 0;
        var cus_occupation_text = $('#cus_occupation option:selected').text();
        if (cus_occupation_text == 'Choose option...') {
            cus_occupation_text = ''
        }
        if (cus_occupation_text == 'Others'){
            $('#others_risk_occupation').show();
        }else {
            $('#others_risk_occupation').hide();
        }
        $('#customeroccupation').val(cus_occupation_text)

        //transactional_risk
        let transactional_risk_score = parseInt($('#transactional_risk').val()) || 0;
        var transactional_risk_text = $('#transactional_risk option:selected').text();
        if (transactional_risk_text == 'Choose option...') {
            transactional_risk_text = ''
        }
        $('#averageyearlytransaction').val(transactional_risk_text)



        //transparency_risk

        let transparency_risk_score = parseInt($('#transparency_risk').val()) || 0;
        var transparency_risk_text = $('#transparency_risk option:selected').text();
        if (transparency_risk_text == 'Choose option...') {
            transparency_risk_text = ''
        }
        //alert(transparency_risk_text)
        $('#crediblesourceoffund').val(transparency_risk_text);


    }

    $(document).on("click", "#calculate", function() {

        //setHiddenValue();


        let type_product_service_score = parseInt($('#type_product_service').val()) || 0;
        var type_product_service_text = $('#type_product_service option:selected').text();
        if (type_product_service_text == 'Choose option...') {
            type_product_service_text = ''
        }
        $('#producttype').val(type_product_service_text)


        let on_boarding_channel_score = parseInt($('#on_boarding_channel').val()) || 0;
        var on_boarding_channel_text = $('#on_boarding_channel option:selected').text();

        if (on_boarding_channel_text == 'Choose option...') {
            on_boarding_channel_text = ''
        }
        $('#onboardingchannel').val(on_boarding_channel_text)
            //residential_status_cbs

        let residential_status_cbs_score = parseInt($('#residential_status_cbs').val()) || 0;
        var residential_status_cbs_text = $('#residential_status_cbs option:selected').text();
        if (residential_status_cbs_text == 'Choose option...') {
            residential_status_cbs_text = ''
        }
        $('#residentialstatus').val(residential_status_cbs_text)

        //foreigncitizenshipscore
        let foreigncitizenshipscore_score = parseInt($('#foreigncitizenshipscore').val()) || 0;
        var foreigncitizenshipscore_text = $('#foreigncitizenshipscore option:selected').text();

        if (foreigncitizenshipscore_text == 'Choose option...') {
            foreigncitizenshipscore_text = ''
        }

        $('#foreignercountryinblacklist').val(foreigncitizenshipscore_text)
            //relationship_risk

        let relationship_risk_pepscore_score = parseInt($('#relationship_risk_pepscore').val()) || 0;
        var relationship_risk_pepscore_text = $('#relationship_risk_pepscore option:selected').text();
        //alert(relationship_risk_pepscore_text);
        if (relationship_risk_pepscore_score == 'Choose option...') {
            relationship_risk_pepscore_score = ''
        }
        $('#customerpep').val(relationship_risk_pepscore_text)

        //relationship_risk_rpepscore

        let relationship_risk_rpepscore_score = parseInt($('#relationship_risk_rpepscore').val()) || 0;
        var relationship_risk_rpepscore_text = $('#relationship_risk_rpepscore option:selected').text();
        if (relationship_risk_rpepscore_text == 'Choose option...') {
            relationship_risk_rpepscore_text = ''
        }

        $('#customerrelatedtopep').val(relationship_risk_rpepscore_text)
            //relationship_risk_cusipscore

        let relationship_risk_cusipscore_score = parseInt($('#relationship_risk_cusipscore').val()) || 0;
        var relationship_risk_cusipscore_text = $('#relationship_risk_cusipscore option:selected').text();

        if (relationship_risk_cusipscore_text == 'Choose option...') {
            relationship_risk_cusipscore_text = ''
        }

        $('#customerip').val(relationship_risk_cusipscore_text)

        //cus_business
        let cus_business_score = parseInt($('#cus_business').val()) || 0;
        var cus_business_text = $('#cus_business option:selected').text();
        if (cus_business_text == 'Choose option...') {
            cus_business_text = ''
        }
        $('#customerbusiness').val(cus_business_text)

        //cus_occupation

        let cus_occupation_score = parseInt($('#cus_occupation').val()) || 0;
        var cus_occupation_text = $('#cus_occupation option:selected').text();
        if (cus_occupation_text == 'Choose option...') {
            cus_occupation_text = ''
        }
        $('#customeroccupation').val(cus_occupation_text)

        //transactional_risk
        let transactional_risk_score = parseInt($('#transactional_risk').val()) || 0;
        var transactional_risk_text = $('#transactional_risk option:selected').text();
        if (transactional_risk_text == 'Choose option...') {
            transactional_risk_text = ''
        }
        $('#averageyearlytransaction').val(transactional_risk_text)

        //transparency_risk

        let transparency_risk_score = parseInt($('#transparency_risk').val()) || 0;
        var transparency_risk_text = $('#transparency_risk option:selected').text();

        if (transparency_risk_text == 'Choose option...') {
            transparency_risk_text = ''
        }

        $('#crediblesourceoffund').val(transparency_risk_text);


        let total_risk = 0;
        //total_risk = 0

        //alert('initial' + parseInt(total_risk))

        if (type_product_service_score != '') {
            //total_risk = parseInt(total_risk) + parseInt(type_product_service_score);
            total_risk = parseInt(total_risk) + parseInt(type_product_service_score);
        }
        console.log ('type_product_service');
        console.log (total_risk);
        //alert ('type_product_service');
        //alert (total_risk);

        //alert('type_product_service_score' + parseInt(total_risk))
        //on_boarding_channel_score

        if (on_boarding_channel_score != '') {
            //alert ('onboarding');
            console.log (parseInt(on_boarding_channel_score));

            total_risk = parseInt(total_risk) + parseInt(on_boarding_channel_score);
            //total_risk = parseInt(total_risk) + on_boarding_channel_score;
        }
        //alert('on_boarding_channel_score' + parseInt(total_risk))
        console.log ('on_boarding_channel_score');
        console.log (total_risk);    
        //residential_status_cbs_score
        //alert('residential_status_cbs_score' + parseInt(total_risk))
        if (residential_status_cbs_score != '') {
            total_risk = parseInt(total_risk) + parseInt(residential_status_cbs_score);
            //total_risk = parseInt(total_risk) + residential_status_cbs_score;
            console.log ('residential_cbs_status');
            console.log (residential_status_cbs_score); 
        }
        console.log (total_risk);
        //alert('residential_status_cbs_score' + parseInt(total_risk))
        //alert(parseInt(total_risk))
        //foreigncitizenshipscore_score
        if (foreigncitizenshipscore_score != '') {
            total_risk = parseInt(total_risk) + parseInt(foreigncitizenshipscore_score);
            //total_risk = parseInt(total_risk) + foreigncitizenshipscore_score;
            console.log ('foreigncitizenshipscore_score');
            console.log (foreigncitizenshipscore_score); 
        }
        console.log (total_risk);
        //alert('foreigncitizenshipscore_score' + parseInt(total_risk))
        //alert(parseInt(total_risk))


        if (relationship_risk_pepscore_score != '') {
            total_risk = parseInt(total_risk) + parseInt(relationship_risk_pepscore_score);
            //total_risk = parseInt(total_risk) + relationship_risk_pepscore_score;
            console.log ('relationship_risk_pepscore_score');
            console.log ( parseInt(relationship_risk_pepscore_score)); 
        }
        console.log (total_risk);
        //alert('relationship_risk_pepscore_score' + parseInt(total_risk))
        if (relationship_risk_rpepscore_score != '') {

            total_risk = parseInt(total_risk) + parseInt(relationship_risk_rpepscore_score);
            //total_risk = parseInt(total_risk) + relationship_risk_rpepscore_score;
            console.log ('relationship_risk_rpepscore_score');
            console.log ( parseInt(relationship_risk_rpepscore_score)); 
        }
        console.log (total_risk);
        //alert(parseInt(total_risk))
        //alert('relationship_risk_rpepscore_score' + parseInt(total_risk))
        if (relationship_risk_cusipscore_score != '') {
            total_risk = parseInt(total_risk) + parseInt(relationship_risk_cusipscore_score);
            //total_risk = parseInt(total_risk) + relationship_risk_cusipscore_score;
            console.log ('relationship_risk_cusipscore_score');
            console.log (parseInt(relationship_risk_cusipscore_score)); 
        }
        console.log (total_risk);
        //alert('relationship_risk_cusipscore_score' + parseInt(total_risk))
        //alert(parseInt(total_risk))





        if (cus_business_score != '') {
            total_risk = parseInt(total_risk) + parseInt(cus_business_score);
            //total_risk = parseInt(total_risk) + cus_business_score;
            console.log ('cus_business_score');
            console.log (parseInt(cus_business_score)); 
        }
        console.log (total_risk);
        //alert('cus_business_score' + parseInt(total_risk))

        if (cus_occupation_score != '') {
            total_risk = parseInt(total_risk) + parseInt(cus_occupation_score);
            //total_risk = parseInt(total_risk) + cus_occupation_score;
            console.log ('cus_occupation_score');
            console.log (parseInt(cus_occupation_score));
        }
        console.log (total_risk);

        //alert('cus_occupation_score' + parseInt(total_risk))

        if (transactional_risk_score != '') {

            //total_risk = parseInt(total_risk) + transactional_risk_score;
           
            total_risk = parseInt(total_risk) + parseInt(transactional_risk_score);
            console.log ('transactional_risk_score');
            console.log (parseInt(transactional_risk_score));
        }
        console.log (total_risk);

        //alert('transactional_risk_score' + parseInt(total_risk))

        if (transparency_risk_score != '') {

            total_risk = parseInt(total_risk) + parseInt(transparency_risk_score);
            //total_risk = parseInt(total_risk) + transparency_risk_score;
            console.log ('transparency_risk_score');
            console.log (parseInt(transparency_risk_score));
        }
        console.log (total_risk);
        //alert('transparency_risk_score' + parseInt(total_risk))

        var risk_label = ''

        if (total_risk >= 15) {

            risk_label = 'High Risk';
        } else {
            risk_label = 'Low Risk';
        }

        total_risk = total_risk ; 
        $('#overall_risk_score').val(total_risk.toString());
        $('#overall_risk_score_hidden').val(total_risk.toString());

        $('#risk_type').val(risk_label);
        $('#risk_type_hidden').val(risk_label);

        //$('#exampleModal').hide('hide');
        // $('#exampleModal').modal().hide();

        //alert(total_risk)
        //alert(type_product_service_score)
        //console.log(type_product_service_text);

        //var label_for = $("#type_product_service_label").attr("for");
        //alert(label_for);
        // Can be simply:
        //var id = element.id;
        return false;

    });

    /*$('#exampleModal').on('shown.bs.modal', function() {
        alert('hellll.')
        $('#sub_transparency_risk').trigger('focus')
    })*/

    /*$("#riskform").on('click', '#calculate', function() {
        alert('hello click');
    });*/
});