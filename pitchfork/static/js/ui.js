
$('.scrollup').click(function(){
    $('html, body').animate({ scrollTop: 0 }, 600);
    return false;
});

$('.toc').click(function(e) {
    e.preventDefault();
    var target = $(this).attr('href');
    if (user != 'None') {
        $('html, body').animate({ scrollTop: $(target).offset().top - 200}, 600);
    } else {
        $('html, body').animate({ scrollTop: $(target).offset().top - 160}, 600);
    }
});

$('.testing-button').on('click', function() {
    var pathname = window.location.pathname;
    pathname += 'testing';
    window.location = pathname;
});

$('.active-button').on('click', function() {
    var pathname = window.location.pathname;
    var temp_path = pathname.split('/');
    window.location = '/' + temp_path[1] + '/';
});

function toggle_results() {
    $('.code-blocks-wrapper #toggle_results').click(function(e){
        var loop = $(this).data('loop');
        var title = $(this).data('title');
        var results = $(this).data('results');
        $('#api_results_wrapper_' + title).toggle('slow', function() {});
        e.stopPropagation();
    });
}

$('#region').on('change', function () {
    $(this).removeClass('error');
    if ($(this).val() == 'none') {
        $(this).addClass('empty');
    }
    else {
        $(this).removeClass("empty");
    }
    $('.code-block').text('None');
    $('.code-blocks-wrapper').hide();
    if (global_count > 1) {
        show_product_message('Responses have been cleared as the data does not apply to the new region', 'info');
    }
    else {
        global_count += 1;
    }
    if (require_region === 'true') {
        if ( $('#region').val() == 'us' ) {
            $('.api-call-endpoint').text(endpoints.us_api);
        } else if ( $('#region').val() == 'uk' ) {
            $('.api-call-endpoint').text(endpoints.uk_api);
        }
    }
});

function scroll_if_anchor(href, add_to) {
    href = typeof(href) === 'string' ? href : $(this).attr('href');
    if(!href) return;
    var fromTop = 160 + add_to;
    if(href.charAt(0) === '#') {
        var $target = $(href);
        if($target.length) {
            $('html, body').animate({ scrollTop: $target.offset().top - fromTop });
        }
    }
}

function display_message(message, alert_class) {
    $('#generated_messages').html(
        '<div class="alert alert-' + alert_class + '">' +
        '<button type="button" class="close" data-dismiss="alert">' +
        '&times;</button><p>' + message + '</p></div>');
}

function show_product_message(message, alert_class) {
    $('#generated_messages_product').html(
        '<div class="alert alert-' + alert_class + '">' +
        '<button type="button" class="close" data-dismiss="alert">' +
        '&times;</button><p>' + message + '</p></div>');
}

function validate_field(field_name) {
    if ( $.trim($('#' + field_name).val()) !== '' & $('#' + field_name).val().length !== 0 & $.trim($('#' + field_name).val()) !== 'none' ) {
        return true;
    }
    else {
        $('#' + field_name).addClass('error');
        return false;
    }
}

function setup_toggle_details() {
    $('.row #toggle_details').click(function(e) {
        var loop = $(this).data('loop');
        var title = $(this).data('title');
        var button = $(this);
        var parent = $(this).closest('.call-wrapper');
        parent.toggleClass('call-visible');
        $('.' + title).toggle('slow', function() {
            if ( $('.' + title).is(':hidden') ) {
                button.text('Details');
            } else {
                button.text('Hide');
            }
        });
        e.stopPropagation();
    });
}

function setup_toggle_details_verb() {
    $('.row #toggle_details_verb').click(function(e) {
        var loop = $(this).data('loop');
        var title = $(this).data('title');
        var button = $(this).parent().parent().find('.details-btn');
        var parent = $(this).closest('.call-wrapper');
        parent.toggleClass('call-visible');
        $('.' + title).toggle('slow', function() {
            if ( $('.' + title).is(':hidden') ) {
                button.text('Details');
            } else {
                button.text('Hide');
            }
        });
        e.stopPropagation();
    });
}

$('.toggle-favorite').click(function(e) {
    e.preventDefault();
    var action = $(this).attr('data-action');
    var product = $(this).data('product');
    var data = {
        'call_id': $(this).data('id')
    };
    var url = $(this).data('url');
    var favorite = $(this);
    $.ajax({
        url: '/' + url + '/favorites/' + action,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json"
    }).done(function(result) {
        if (action === 'add') {
            favorite.find('span').addClass('chosen');
            favorite.attr('data-action', 'remove');
        } else {
            favorite.find('span').removeClass('chosen');
            favorite.attr('data-action', 'add');
        }
    }).fail(function(error) {
        show_product_message('There was an error processing the request', 'error');
    });
});

function send_api_call(send_to, data) {
    return $.ajax({
        url: send_to,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json"
    });
}

function process_display_api_call(send_to, data, form_submit, form_value) {
    send_api_call(send_to, data).done(success_process).fail(error_process);

    function success_process(result) {
        $('#loading_div_' + form_submit).hide();
        if (!$('#api_results_wrapper_' + form_submit).is(':visible')) {
            $('#api_results_wrapper_' + form_submit).toggle('slow');
        }
        $('#api_url_' + form_submit).html(result.api_url);
        $('#api_headers_' + form_submit).html(result.request_headers);
        if (result.data_package) {
            if ( $('#api_body_wrapper_' + form_submit).is(':hidden') ) {
                $('#api_body_wrapper_' + form_submit).toggle();
            }
            $('#api_body_' + form_submit).html(result.data_package);
        }
        if (form_value != 'Mock API Call') {
            $('.response-headers-' + form_submit).show();
            $('.response-body-' + form_submit).show();
            $('#api_response_headers_' + form_submit).html(result.response_headers);
            $('#api_content_' + form_submit).html(result.response_body);
        } else {
            $('.response-headers-' + form_submit).hide();
            $('.response-body-' + form_submit).hide();
        }
    }

    function error_process(result) {
        $('#loading_div_' + form_submit).hide();
    }
}

function setup_api_call_submit() {
    $('.api_call_submit').on('click', function() {
        var form_submit = $(this).attr('name');
        var form_value = $(this).attr('value');
        $("#" + form_submit + "_form").unbind('submit').bind('submit', function(e){
            e.preventDefault();
            $('#loading_div_' + form_submit).show();
            var sending = {};
            var send_to = 'api/call/process';
            var validated = false;
            var data = $("#" + form_submit + "_form").serialize();
            $.each(data.split('&'), function (index, elem) {
                var vals = elem.split('=');
                if (vals[0] === 'app_url_link' && vals[1] != 'None') {
                    send_to = unescape(vals[1].replace(/\+/g, ' ')) + '/api/call/process';
                }
                sending[vals[0].replace(/\+/g, ' ')] = unescape(vals[1]);
            });
            $("#" + form_submit + "_form").serializeArray().map(function(x){sending[x.name] = x.value;});
            var message = "You must provide the following data before the request can be sent:<br /><br />";
            var region_check = false;
            var ddi_check = false;
            var token_check = false;
            if (form_value === 'Mock API Call') {
                // Sending mock call
                validated = true;
                sending.mock = true;
                sending.region = '{region}';
                sending.ddi = '{ddi}';
                sending.token = '{api-token}';
            } else {
                // Sending Real Call
                if (sending.remove_token === 'True') {
                    token_check = true;
                } else {
                    if ( validate_field('token') ) {
                        sending.api_token = $('#token').val().trim();
                        token_check = true;
                    } else {
                        $('#token').addClass('error');
                        message += "<span class='text-danger'>API Token</span><br />";
                    }
                }
                if (sending.remove_ddi === 'True') {
                    ddi_check = true;
                } else {
                    if ( validate_field('ddi') ) {
                        sending.ddi = $('#ddi').val().trim();
                        ddi_check = true;
                    } else {
                        $('#ddi').addClass('error');
                        message += "<span class='text-danger'>DDI or Account Number</span><br />";
                    }
                }
                if (require_region === 'true') {
                    if ( validate_field('region') ) {
                        sending.region = $('#region').val();
                        region_check = true;
                    } else {
                        $('#region').addClass('error');
                        message += "<span class='text-danger'>Region</span><br />";
                    }
                } else {
                    region_check = true;
                }
                if (region_check && ddi_check && token_check) {
                    sending.testing = testing;
                    validated = true;
                }
            }
            if (validated) {
                process_display_api_call(
                    send_to,
                    sending,
                    form_submit,
                    form_value
                );
            }
            else {
                bootbox.alert(message);
                $('#loading_div_' + form_submit).hide();
            }
        });
    });
}

$('#get_hybrid_token_submit').on('click', function() {
    $("#generate_token_form").unbind('submit').bind('submit', function(e){
        e.preventDefault();
        var data = {};
        $.each($(this).serialize().split('&'), function (index, elem) {
            var vals = elem.split('=');
            data[vals[0].replace(/\+/g, ' ')] = unescape(vals[1].replace(/\+/g, ' '));
        });
        $.ajax({
            url: '/generate_hybrid_token',
            type: 'POST',
            data: JSON.stringify(data),
            contentType: "application/json",
            beforeSend: function() {
                $('#token_info').html('<p>Retrieving...<i class="fa fa-spin fa-spinner"></i></p>');
            }
        }).done(function(re) {
                if (re.code === 200) {
                    $('#token').val(re.token);
                    $('#ddi').val('hybrid:' + data.dedicated_account);
                    $('#token_info').html(
                        '<dl class="dl-horizontal"><dt>Token:</dt><dd>' + re.token +
                        '</dd><dt>DDI:</dt><dd>hybrid:' + data.dedicated_account + '</dd></dl>'
                    );
                    $('#get_hybrid_token_form').modal('hide');
                } else {
                    $('#token_info').html('<p><strong>Error:</strong> ' + re.message + ' </p>');
                }
        }).fail(function(result) {
            $('#token_info').html('<p class="text-danger"><strong>Error:</strong> There was an application error</p>');
        });
    });
});

$('#submit_feedback').on('show.bs.modal', function(event) {
    var link = $(event.relatedTarget);
    $(this).find('#call_id').val(
        link.data('call_id')
    );
    $(this).find('#product_db').val(
        link.data('product')
    );
});

$('#submit_feedback').on('hide.bs.modal', function(event) {
    $(this).find('#submit_feedback_form')[0].reset();
    $(this).find('#product_db').val('');
    $(this).find('#call_id').val('');
});

$('#submit_feedback_submit').on('click', function() {
    $('#submit_feedback_form').unbind('submit').bind('submit', function(e) {
        e.preventDefault();
        var data = $("#submit_feedback_form").serialize();
        var sending = {};
        $.each(data.split('&'), function (index, elem) {
            var vals = elem.split('=');
            if (vals[0] !== 'feedback') {
                sending[vals[0].replace(/\+/g, ' ')] = unescape(vals[1]);
            } else {
                sending[vals[0].replace(/\+/g, ' ')] = vals[1].replace(/\+/g, ' ');
            }
        });
        $.ajax({
            url: '/feedback/',
            type: 'POST',
            data: JSON.stringify(sending),
            contentType: "application/json",
        }).done(function(result) {
            show_product_message('Feedback has been sent successfully', 'success');
            $('#submit_feedback').modal('hide');
        }).fail(function(error) {
            show_product_message('Submit feeback encountered an error and could not be saved', 'error');
        });
    });
});
