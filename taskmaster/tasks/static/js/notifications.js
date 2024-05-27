function toggleNotifications() {
    document.getElementById("notificationDropdown").classList.toggle("show");
}

function toggleNotificationSettings() {
    document.getElementById("notificationSettingsPopup").classList.toggle("show");

}

function closeNotificationSettings() {
    document.getElementById("notificationSettingsPopup").classList.remove("show");
}

function saveNotificationSettings() {
    var form = document.getElementById("notificationSettingsForm");
    var formData = new FormData(form);
    var formDataObject = {};
    formData.forEach((value, key) => {
        if (!formDataObject[key]) {
            formDataObject[key] = [];
        }
        formDataObject[key].push(value);
    });

    fetch('/save-notification-settings/', {
        method: 'POST',
        body: JSON.stringify(formDataObject),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeNotificationSettings();
        } else {
            alert("Ошибка при сохранении настроек: " + data.error);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function closeNotificationSettings() {
    document.getElementById("notificationSettingsPopup").classList.remove("show");
}


function markNotificationAsRead(notificationId) {
    fetch(`/mark-notification-as-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
}

function markAllNotificationsAsRead() {
    fetch('/mark-all-notifications-as-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            document.getElementById("notificationDropdown").classList.remove("show");
            document.querySelector('.notification-btn .badge').innerText = "0";
        } else {
            alert("Ошибка при пометке всех уведомлений как прочитанных");
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Проверяем, соответствует ли этот cookie нужному имени
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
