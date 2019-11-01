// $(document).ready(function () {
//     // warning();
//     console.log('Hello');
//     let msg_container = $('#message-container');
//     msg_container.append(
//         $('<div/>')
//             .addClass("alert alert-dismissible message-box1")
//             .attr('id', 'message-box1')
//             .attr("role", "alert")
//             .append($("<button/>")
//                 .attr('type', 'button')
//                 .addClass('close')
//                 .attr('aria-label', 'Close')
//                 .attr('onclick', '$("#message-box1").remove()')
//                 .append($('<span/>')
//                     .attr('aria-hidden', 'true')
//                     .text("×")
//                 )
//             )
//
//             .append($("<div/>")
//                 .attr('id', 'warning1')
//                 .text('Warning Message')
//             )
//
//         // .append("<span/>")
//         // .attr('aria-hidden', 'true').text("&times;")
//
//     );
//     console.log('Hello humndas!')
//
// });
//
//
//
// function warning() {
//     console.log('warning - ----');
//
//     $.ajax({
//         url: '/check-for-updates',
//         type: 'get',
//         processData: false,
//         contentType: false,
//         dataType: "JSON",
//         success: function (data) {
//             // Perform operation on return value
//             var tag = data['error_message']['tag'];
//             var message = data['error_message']['message'];
//
//             $('#warning').text(message);
//             $('#message-box').addClass(tag);
//             $('#message-box').css('visibility', '');
//             $('#message-box').css('display', 'block');
//             warning();
//         },
//     });
// }
//

