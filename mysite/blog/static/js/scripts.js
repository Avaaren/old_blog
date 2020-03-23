$(document).ready(function () {
    $('#search-box').on('input', function (e) {
        $.ajax({
            url: '/blog/ajax_search/',
            data: {
                'value': $(this).val(),
            },
            dataType: 'json',
            success: function (data) {
                // $('#result').text($(this).val());
                console.log(data.search_result);
                $('#result').empty();
                if (data.search_result.length == 0) {
                    $('#result').append($('<p>').text('empty'));
                }
                else {
                    data.search_result.forEach(function (item) {
                        var p = $('<p>', { 'class': 'lol' }).text(item);
                        $('#result').append(p);
                    })
                }
            }
        })
        // $('#result').text($(this).val());

    });
});

