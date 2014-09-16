$('.scrollup').click(function(){
    $('html, body').animate({ scrollTop: 0 }, 600);
    return false;
});

$('.toc').click(function(e) {
    e.preventDefault();
    $('html, body').animate( { scrollTop: ( $( $(this).attr('href') ).offset().top - 60 ) }, 600);
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
    if ( global_count > 1 ) {
        display_message('Responses have been cleared as the data does not apply to the new data center', 'info');
    }
    else {
        global_count += 1;
    }
    if (require_dc) {
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
