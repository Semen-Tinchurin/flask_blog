// Создаем новый объект Date
var date = new Date();

// Получаем смещение часового пояса в минутах относительно UTC
var offset = date.getTimezoneOffset();

// Вычисляем смещение в часах и минутах
var hours = Math.abs(Math.floor(offset / 60));
var minutes = Math.abs(offset % 60);

// Формируем строку с тайм зоной
var timezone = 'UTC';
if (offset < 0) {
    timezone += '+';
} else {
    timezone += '-';
}
timezone += hours.toString().padStart(2, '0') + ':' + minutes.toString().padStart(2, '0');

// Отправляем данные на сервер с помощью AJAX-запроса
var xhr = new XMLHttpRequest();
xhr.open('POST', '/timezone', true);
xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
xhr.send(JSON.stringify({'timezone': timezone}));
