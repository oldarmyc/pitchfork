$('.scrollup').click(function(){
    $('html, body').animate({ scrollTop: 0 }, 600);
    return false;
});

$('.toc').click(function(e) {
    e.preventDefault();
    var target = $(this).attr('href');
    $('html, body').animate({ scrollTop: $(target).offset().top - 60}, 600);
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

$('.panel-title #toggle_details').click(function(e) {
    var loop = $(this).data('loop');
    var title = $(this).data('title');
    var button = $(this);
    $('.' + title).toggle('slow', function() {
        if ( $('.' + title).is(':hidden') ) {
            button.text('Call Details');
        } else {
            button.text('Hide Details');
        }
    });
    e.stopPropagation();
});

$('.code-blocks-wrapper #toggle_results').click(function(e){
    var loop = $(this).data('loop');
    var title = $(this).data('title');
    var results = $(this).data('results');
    $('#api_results_wrapper_' + title).toggle('slow', function() {
        if ( $('#api_results_wrapper_' + title).is(':visible') === false) {
            // $('html, body').animate({ scrollTop: $('#' + title).offset().top - 60}, 10);
        }
    });
    e.stopPropagation();
});

$('#data_center').on('change', function () {
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
        display_message('Responses have been cleared as the data does not apply to the new data center', 'info');
    }
    else {
        global_count += 1;
    }
    if (require_dc === 'true') {
        if ( $('#data_center').val() == 'us' ) {
            $('span.api-call-endpoint').text("{{ api_settings.us_api }}")
        } else if ( $('#data_center').val() == 'uk' ) {
            $('span.api-call-endpoint').text("{{ api_settings.uk_api }}")
        } else {
            $('span.api-call-endpoint').text("{{ api_settings.us_api }}")
        }
    }
});

function display_message(response_message, alert_class) {
    var message = '<div class="alert alert-' + alert_class +'"><button type="button" class="close" data-dismiss="alert">&times;</button><p>' + response_message + '</p></div>';
    $('#generated_messages').html(message);
}

function validate_field(field_name) {
    if ( $.trim($('#' + field_name).val()) != '' & $('#' + field_name).val().length != 0 & $.trim($('#' + field_name).val()) != 'none' ) {
        return true;
    }
    else {
        $('#' + field_name).addClass('error');
        return false;
    }
}

function escapeHTML(data) {
    return data.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g, '<br />').replace(/\s\s/g, '&nbsp;&nbsp;');
}

function formatXml(xml) {
    var formatted = '';
    var reg = /(>)(<)(\/*)/g;
    xml = xml.toString().replace(reg, '$1\r\n$2$3');
    var pad = 0;
    $.each(xml.split('\r\n'), function(index, node) {
        var indent = 0;
        if (node.match( /.+<\/\w[^>]*>$/ )) {
            indent = 0;
        } else if (node.match( /^<\/\w/ )) {
            if (pad != 0) {
                pad -= 2;
            }
        } else if (node.match( /^<\w[^>]*[^\/]>.*$/ )) {
            indent = 2;
        } else {
            indent = 0;
        }
        var padding = '';
        for (var i = 0; i < pad; i++) {
            padding += ' ';
        }
        formatted += padding + node + '\r\n';
        pad += indent;
    });
    return escapeHTML(formatted);
}

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
        $('#api_url_' + form_submit).text(result.api_url);
        $('#api_headers_' + form_submit).html(
            '<pre>' +
            JSON.stringify(result.request_headers, null, 4) +
            '</pre>'
        );
        if (result.data_package) {
            if ( $('#api_body_wrapper_' + form_submit).is(':hidden') ) {
                $('#api_body_wrapper_' + form_submit).toggle();
            }
            $('#api_body_' + form_submit).html(
                '<pre>' +
                JSON.stringify(result.data_package, null, 4) +
                '</pre>'
            );
        }
        if (form_value != 'Mock API Call') {
            $('.response-headers-' + form_submit).show();
            $('.response-body-' + form_submit).show();
            $('#api_response_headers_' + form_submit).html(
                '<pre>' +
                JSON.stringify(result.response_headers, null, 4) +
                '</pre>'
            );
            var content_type = [];
            if (result.response_headers['content-type']) {
                content_type = result.response_headers['content-type'].split(';');
            }
            if ( result.response_code >= 400 ) {
                if (
                    $.inArray('application/xml', content_type) >= 0 ||
                    $.inArray('application/atom+xml', content_type) >= 0
                ) {
                    $('#api_content_' + form_submit).html(
                        formatXml(result.response_body)
                    );
                } else {
                    $('#api_content_' + form_submit).html(
                        '<pre>' +
                        JSON.stringify(result.response_body, null, 4) +
                        '</pre>'
                    );
                }
            } else {
                if (
                    $.inArray('application/xml', content_type) >= 0 ||
                    $.inArray('application/atom+xml', content_type) >= 0
                ) {
                    $('#api_content_' + form_submit).html(
                        formatXml(result.response_body)
                    );
                } else {
                    $('#api_content_' + form_submit).html(
                        '<pre>' +
                        JSON.stringify(result.response_body, null, 4) +
                        '</pre>'
                    );
                }
            }
        } else {
            $('.response-headers-' + form_submit).hide();
            $('.response-body-' + form_submit).hide();
        }
    }

    function error_process(result) {
        $('#loading_div_' + form_submit).hide();
    }
}

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
            sending[vals[0].replace(/\+/g, ' ')] = unescape(vals[1].replace(/\+/g, ' '));
        });
        var message = "You must provide the following data before the request can be sent:<br /><br />";
        var dc_check = false;
        if ( require_dc && form_value != 'Mock API Call' ) {
            if ( validate_field('data_center') ) {
                sending['data_center'] = $('#data_center').val();
                sending['ddi'] = $('#ddi').val().trim();
                dc_check = true;
            } else {
                $('#data_center').addClass('error');
                if (restrict_dcs === 'true') {
                    message += "<span class='text-danger'>Region</span>";
                } else {
                    message += "<span class='text-danger'>Data Center</span>";
                }
            }
        } else if (require_dc === 'true') {
            if ( $('#data_center').val() != 'none' ) {
                sending['data_center'] = $('#data_center').val();
                sending['ddi'] = $('#ddi').val().trim();
            }
        } else {
            dc_check = true;
            sending['ddi'] = $('#ddi').val().trim();
        }
        if (dc_check) {
            sending['testing'] = testing;
            validated = true;
        }
        if (form_value == 'Mock API Call') {
            validated = true;
            sending['mock'] = true;
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
