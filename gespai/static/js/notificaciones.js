function generar_lista_notificaciones(data) {
    var menu = document.getElementById(notify_menu_id);
    if (menu) {
        menu.innerHTML = "";
        for (var i = 0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];
            console.log(item)
            var message = ""
            if (typeof item.actor !== 'undefined') {
                message = message + item.actor;
            }
            if (typeof item.verb !== 'undefined') {
                message = message + " " + item.verb;
            }
            if (typeof item.timestamp !== 'undefined') {
                var m = item.timestamp.match(/(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2})/)
                date = '(' + m[3] + '/' + m[2] + '/' + m[1] + ' - ' + m[4] + ')'
                message = message + " " + date;
            }

            menu.innerHTML = menu.innerHTML + "<li><a href='/inbox/notifications'>" + message + "</a></li>";
        }
    }
}
