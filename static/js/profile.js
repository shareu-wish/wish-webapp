function formatNumber(phone) {
    return phone.slice(2, 12).replace(/(\d{3})(\d{3})(\d{2})(\d{2})/, `${phone.slice(0, -10)} ($1) $2 $3-$4`)
}


function loadUserInfo() {
    $.ajax({
        url: '/profile/get-user-info',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            document.getElementById('name').innerText = data.name ? data.name : "Не указано";
            switch (data.gender) {
                case 1:
                    document.getElementById('gender').innerText = 'Мужской';
                    break;
                case 2:
                    document.getElementById('gender').innerText = 'Женский';
                    break;
                default:
                    document.getElementById('gender').innerText = 'Не указано';
            }
            document.getElementById('age').innerText = data.age ? data.age : "Не указано";
            document.getElementById('phone').innerText = formatNumber(data.phone);
        },
        error: function (error) {
            console.error('Error fetching user info:', error);
        }
    });
}


function loadCurrentOrder() {
    // Пример активного заказа
    const activeOrder = true; // Здесь можно подгрузить состояние с сервера
    const currentOrderDiv = document.getElementById('current-order');
    
    if (activeOrder) {
        currentOrderDiv.innerHTML = `
            <p>Зонт у вас уже: <span id="umbrella-time">2 часа</span></p>
            <p>За сданный зонт вам вернётся: 700 рублей</p>
            <button class="lost-btn" onclick="openLostModal()">Зонт потерян</button>
        `;
    } else {
        currentOrderDiv.innerHTML = '<p>Нет активных заказов</p>';
    }
}

function loadOrderHistory() {
    // Пример истории заказов
    const orderHistory = [
        {
            startTime: '2023-01-01 10:00',
            startStation: 'Станция А',
            endTime: '2023-01-01 12:00',
            endStation: 'Станция Б',
            duration: '2 часа'
        },
        // Добавьте больше заказов по мере необходимости
    ];
    
    const orderHistoryDiv = document.getElementById('order-history');
    orderHistory.forEach(order => {
        const orderCard = document.createElement('div');
        orderCard.className = 'order-card';
        orderCard.innerHTML = `
            <p>Время начала: ${order.startTime}</p>
            <p>Адрес станции, откуда зонт был взят: ${order.startStation}</p>
            <p>Время конца: ${order.endTime}</p>
            <p>Адрес станции, куда зонт вернули: ${order.endStation}</p>
            <p>Продолжительность заказа: ${order.duration}</p>
        `;
        orderHistoryDiv.appendChild(orderCard);
    });
}

function openEditModal() {
    const name = document.getElementById('name').innerText;
    const gender = document.getElementById('gender').innerText;
    const age = document.getElementById('age').innerText;
    
    document.getElementById('edit-name').value = name !== 'Не указано' ? name : '';
    $(`input[name="edit-gender"]`).val([gender]);
    document.getElementById('edit-age').value = age !== 'Не указано' ? age : '';

    const modal = document.getElementById('edit-modal');
    modal.classList.add('show');
}

function closeEditModal() {
    const modal = document.getElementById('edit-modal');
    modal.classList.remove('show');
}

function saveChanges() {
    const name = document.getElementById('edit-name').value;
    const gender =  $(`input[name="edit-gender"]:checked`).val();
    const age = document.getElementById('edit-age').value;

    document.getElementById('name').innerText = name ? name : 'Не указано';
    document.getElementById('gender').innerText = gender ? gender : 'Не указано';
    document.getElementById('age').innerText = age ? age : 'Не указано';

    let genderCode = 0;
    if (gender === 'Мужской') {
        genderCode = 1;
    } else if (gender === 'Женский') {
        genderCode = 2;
    }

    // Отправка данных на сервер о изменениях пользователя
    $.ajax({
        url: '/profile/update-user-info',
        type: 'POST',
        data: JSON.stringify({
            name: name,
            gender: genderCode,
            age: age ? Number(age) : null
        }),
        success: function (response) {
            console.log('User info updated successfully');
        },
        error: function (error) {
            console.error('Error updating user info:', error);
        }
    });

    // Отправка данных на сервер о изменениях пользователя
    
    closeEditModal();
}

function openLostModal() {
    document.getElementById('lost-modal').style.display = 'block';
}

function closeLostModal() {
    document.getElementById('lost-modal').style.display = 'none';
}

function confirmLoss() {
    // Отправка данных на сервер о потере зонта
    alert('Данные о пропаже зонта отправлены на сервер.');
    closeLostModal();
}


$(document).ready(() => {
    loadUserInfo();
    loadCurrentOrder();
    loadOrderHistory();
});
