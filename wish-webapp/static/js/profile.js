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


function loadActiveOrder() {
    $.ajax({
        url: '/profile/get-active-order',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            const currentOrderDiv = document.getElementById('current-order');
            if (data.order) {
                let datetimeTake = data.order.datetime_take

                // The time that the umbrella is in the user's hands (current-time - datetimeTake)
                // Should be displayed (ex.): `3 hours 42 minutes` or `52 hours 11 minures` or `38 minutes`
                datetimeTake = new Date(datetimeTake)
                // datetimeTake.setHours(datetimeTake.getHours() - 3)
                const timeOnHands = new Date() - datetimeTake;
                const hours = Math.floor(timeOnHands / (1000 * 60 * 60));
                const minutes = Math.floor((timeOnHands % (1000 * 60 * 60)) / (1000 * 60));
                let timeOnHandsFormatted = '';
                if (hours > 0) {
                    timeOnHandsFormatted = `${hours} часов ${minutes} минут`;
                } else if (minutes > 0) {
                    timeOnHandsFormatted = `${minutes} минут`;
                } else {
                    timeOnHandsFormatted = 'меньше минуты';
                }
            
                currentOrderDiv.innerHTML = `
                    <p>Зонт у вас уже: <span id="umbrella-time">${timeOnHandsFormatted}</span></p>
                    <p>За сданный зонт вам вернётся: 700 рублей</p>
                    <button class="lost-btn" onclick="openLostModal()">Зонт утерян</button>
                `;
            } else {
                currentOrderDiv.innerHTML = '<p>Нет активного заказа</p>';
            }
        },
        error: function (error) {
            console.error('Error fetching active order:', error);
        }
    });
}

function loadOrderHistory() {
    $.ajax({
        url: '/profile/get-processed-orders',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            const orderHistory = data.orders;
            orderHistory.reverse();
            const orderHistoryDiv = document.getElementById('order-history');
            orderHistoryDiv.innerHTML = '';
            
            orderHistory.forEach(order => {
                const timeOnHands = new Date(order.datetime_put) - new Date(order.datetime_take);
                const hours = Math.floor(timeOnHands / (1000 * 60 * 60));
                const minutes = Math.floor((timeOnHands % (1000 * 60 * 60)) / (1000 * 60));
                let timeOnHandsFormatted = '';
                if (hours > 0) {
                    timeOnHandsFormatted = `${hours} часов ${minutes} минут`;
                } else if (minutes > 0) {
                    timeOnHandsFormatted = `${minutes} минут`;
                } else {
                    timeOnHandsFormatted = 'меньше минуты';
                }
                const orderCard = document.createElement('div');
                orderCard.className = 'order-card';
                orderCard.innerHTML = `
                    <p>Время начала: <span>${new Date(order.datetime_take).toLocaleString()}</span></p>
                    <p>Адрес станции, откуда зонт был взят: <span>${order.station_take_address}</span></p>
                    <p>Время конца: <span>${new Date(order.datetime_put).toLocaleString()}</span></p>
                    <p>Адрес станции, куда зонт вернули: <span>${order.station_put_address}</span></p>
                    <p>Продолжительность заказа: <span>${timeOnHandsFormatted}</span></p>
                `;
                orderHistoryDiv.appendChild(orderCard);
            });
        },
        error: function (error) {
            console.error('Error fetching active order:', error);
        }
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
    loadActiveOrder();
    loadOrderHistory();
});
