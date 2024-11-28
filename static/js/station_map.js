/* 
Как работают карточки с информацией о станциях:
1) На телефонах: 
    При нажатии на метку на карте открывается карточка поверх карты и не двигается с движением карты. 
    При нажатии на другую метку, контент заменяется.
2) На других устройствах:
    При нажатии на метку на карте открывается карточка внутри карты. Карточка прикреплена к метке, с движением карты двигается карточка.
    При нажатии на другую метку, старая закрывается, а новая открывается.

При повторном нажатии на метку, карточка закрывается.
*/


function getUrlCurrentStation() {
  const urlParams = new URLSearchParams(window.location.search);
  const stationId = urlParams.get('station_id');
  return stationId;
}

function clearUrlCurrentStation() {
  const url = new URL(window.location);
  url.searchParams.delete('station_id');
  window.history.replaceState({}, '', url);
}


const isMobileScreen = window.innerWidth <= 480;

function toggleStationWindow(windowId) {
  if (activeStationWindow === windowId) {
    $(`#${windowId}Window`).hide();
    $("#mainWindow").hide();
    $("#QRScannerButton").show();
    activeStationWindow = null;
    return;
  }

  if (activeStationWindow) {
    $(`#${activeStationWindow}Window`).hide();
  }

  if (hasActiveOrder) {
    $(".take-umbrella-btn").hide()
    $(".put-umbrella-btn").show()
  } else {
    $(".take-umbrella-btn").show()
    $(".put-umbrella-btn").hide()
  }

  if (isMobileScreen) {
    $("#mainWindow").html($(`#${windowId}Window`).html() + 
        `<div class="close-station-info-window" onclick="$('#mainWindow').hide();activeStationWindow = null;$('#QRScannerButton').show();$('.ymaps3x0--control.ymaps3x0--control__background').show();"><i class="bi bi-x-lg"></i></div>`);
    $("#mainWindow").show();
    $(".ymaps3x0--control.ymaps3x0--control__background").hide();
  } else {
    $(`#${windowId}Window`).show();
  }

  activeStationWindow = windowId;
  $("#QRScannerButton").hide();
}


function showRoute(station_coords) {
  ymaps3.geolocation.getPosition().then((pos) => {
    pos = pos.coords;
    $("#navigator").attr(
      "src",
      `https://yandex.ru/map-widget/v1/?mode=routes&rtext=${pos[1]}%2C${pos[0]}~${station_coords[0]}%2C${station_coords[1]}&rtt=pd&ruri=~`
    );
    $("#routeWindow").show()
  });
}

function generateNumberCells(number, containerId) {
  const numberContainer = document.getElementById(containerId);
  if (!numberContainer) return; // проверка на наличие элемента
  numberContainer.innerHTML = ''; // Очищаем старые ячейки
  
  const digits = String(number).split('');
  digits.forEach(digit => {
    const span = document.createElement('span');
    span.classList.add('number');
    span.textContent = digit;
    numberContainer.appendChild(span);
  });
}


async function drawStations() {
  await ymaps3.ready;

  const {
    YMapMarker,
  } = ymaps3;

  $(".station-marker").remove();

  for (const station of stations) {
    const markerElement = document.createElement("div");
    markerElement.className = "station-marker";
    markerElement.innerHTML = `

    <div onclick="toggleStationWindow('${station.id}')">
        <div class="umbrellas-count">${station.can_take}</div>
        <img src="/static/img/logos/umbrella-mini.svg">
    </div>
    <div class="station-info-window" id="${station.id}Window">
      <div class="windowContent">
        <div class="container">
            <div class="header">
                № <span id="number-container-${station.id}"></span>
        </div>
            
            
            <div class="location-row">
                <div>
                    <div class="location"><a>${station.title}</a></div>
                    <div class="location-text"><a>${station.address}</a></div>
                </div>
                
                <div class="map-button" onclick="showRoute([${station.latitude}, ${station.longitude}])">
                    <!-- SVG-иконка для карты -->
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-map-pin">
                        <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 1 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    Маршрут
                </div>
            </div>
            
           
            ${station.information ? ` <div>
                <div class="location"><a>Как найти:</a></div>
                <div class="location-text"><a>${station.information}</a></div>
            </div>` :""}

            
            <div>
                <div class="location"><a>График работы:</a></div>
                <div class="location-text"><a> пн - пт: 06:00 - 23:00 <span style="color: green;">открыто</span></a></div>
                <div class="location-text"><a> cб - вс: <span style="color: rgb(128, 0, 0);">закрыто</span></a></div>
            </div>
            
            <!-- Блок залога и доступности сбоку -->
            <div class="deposit-availability-container">
                <!-- Шкала с метками и крестиком -->
                <div class="timeline">
                    <div class="timeline-line"></div>
                    <div class="timeline-marker"></div> <!-- Первые сутки -->
                    <div class="timeline-marker"></div> <!-- Вторые сутки -->
                </div>

                <!-- Блок залога -->
                <div class="deposit-box">
                    <div class="deposit-header">цена старта:</div>
                    <div class="deposit-item">
                    <div class="deposit-item">
                        <span class="deposit-label">старт с подпиской</span>
                        <span class="deposit-price">0 рублей</span>
                    </div>
                    <div class="deposit-item">
                        <span class="deposit-label">старт без подписки</span>
                        <span class="deposit-price">149 рублей</span>
                    </div>
                </div>      
                <!-- Информация о зонтах -->
                <div class="umbrella-info-new">
                    <div class="umbrella-block">
                        <div class="umbrella-row">
                            <img src="/static/img/logos/umbrella-rounded-green.png" alt="Зонт" class="umbrella-icon green">
                            <span class="umbrella-number">${station.can_take}</span>
                        </div>
                        <span class="umbrella-label">можно взять</span>
                    </div>
                    <div class="umbrella-block">
                        <div class="umbrella-row">
                            <img src="/static/img/logos/umbrella-rounded.png" alt="Зонт" class="umbrella-icon blue">
                            <span class="umbrella-number">${station.can_put}</span>
                        </div>
                        <span class="umbrella-label">можно сдать</span>
                    </div>
                </div>  
            </div>
        

            
            <button class="take-umbrella-btn" onclick="takeUmbrella('${station.id}')"><i class="bi bi-umbrella-fill"></i> Взять зонт</button>
            <button class="put-umbrella-btn" onclick="putUmbrella('${station.id}')" style="display: none;"><i class="bi bi-arrow-down"></i> Вернуть зонт</button>
            
            </div>
    </div>


      `;
    
      const marker = new YMapMarker(
        {
          coordinates: [station.longitude, station.latitude],
        },
        markerElement
      );
  
      map.addChild(marker);
  
      // Вызываем функцию для генерации номера станции сразу после создания маркера
      generateNumberCells(station.id, `number-container-${station.id}`);
    }
  }


async function initMap() {
  await ymaps3.ready;

  const {
    YMap,
    YMapDefaultSchemeLayer,
    YMapDefaultFeaturesLayer,
    YMapControls,
  } = ymaps3;

  const { YMapDefaultMarker } = await ymaps3.import(
    "@yandex/ymaps3-markers@0.0.1"
  );

  const { YMapGeolocationControl } = await ymaps3.import(
    "@yandex/ymaps3-controls@0.0.1"
  );

  const urlCurrentStationId = getUrlCurrentStation();

  let mapCenter = [37.617698, 55.755864] // Moscow
  let zoom = 12;
  if (urlCurrentStationId) {
    const station = stations.find(station => station.id == urlCurrentStationId);
    mapCenter = [station.longitude, station.latitude];
    zoom = 16;
  }

  map = new YMap(document.getElementById("map"), {
    location: {
      center: mapCenter,
      zoom: zoom,
    },
    controls: ["routeButtonControl"],
  });

  map.addChild(new YMapDefaultSchemeLayer());
  map.addChild(new YMapDefaultFeaturesLayer());

  /*ymaps3.geolocation.getPosition().then((pos) => {
          console.log(pos);
        });*/

  /*const markerElement = document.createElement("div");
        markerElement.className = "icon-marker";
        markerElement.innerText = "I'm marker!";
  
        const marker = new YMapMarker(
          {
            coordinates: [25.229762, 55.289311]
          },
          markerElement
        );
  
        map.addChild(marker);*/

  /*map.addChild(
          new YMapDefaultMarker({
            coordinates: [25.229762, 55.289311],
            title: "Hello World!",
            subtitle: "kind and bright",
            color: "blue",
          })
        );*/

  map.addChild(
    // Using YMapControls you can change the position of the control
    new YMapControls({ position: "left" }) // bottom left
      // Add the geolocation control to the map
      .addChild(new YMapGeolocationControl({}))
  );

  if (!urlCurrentStationId) {
    document.getElementsByClassName("ymaps3x0--control-button")[0].click();
  }

  await drawStations()

  if (urlCurrentStationId) {
    toggleStationWindow(urlCurrentStationId);
    clearUrlCurrentStation();
  }
}


function loadStations() {
  return $.ajax({
    type: "GET",
    url: "/station-map/get-stations",
    success: function (data) {
      return data;
    },
  });
}



function loadActiveOrder() {
  $.ajax({
    type: "GET",
    url: "/profile/get-active-order",
    success: function (data) {
      hasActiveOrder = data.order !== null

      if (hasActiveOrder) {
        $(".take-umbrella-btn").hide()
        $(".put-umbrella-btn").show()
      } else {
        $(".take-umbrella-btn").show()
        $(".put-umbrella-btn").hide()
      }
    },
  });
}


function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}


function checkAuth() {
  const authToken = getCookie("authToken");
  if (authToken === null || authToken === '') {
    hasAuth = false
    $("#profile").hide()
    $("#headerLoginContainer").show()
  } else {
    hasAuth = true
  }
}


function takeUmbrella(stationId) {
  if (!hasAuth) {
    // $("#auth-suggestion-modal").addClass("show")
    return window.location.href = `/auth?station_id=${stationId}`
  }

  showStationInteractionModal(`
    <div class="modal-body">
    <div class="modal-content">
      Подключение к банку...
    </div>
  </div>
  `)

  $.ajax({
    type: "POST",
    url: `/station-map/take-umbrella`,
    data: {
      station_id: stationId
    },
    success: function (data) {
      if (data.status === "ok") {
        // alert(`Заказ №${data.order_id}\nВы можете забрать зонт из ячейки ${data.slot}`)
        if (data.payment_mode === "auto") {
          setIsInteractingWithStation(true);
        } else {
          $('#stationInteractionModal').removeClass('show')
          showPayment(data.user_id, data.station_id)
        }
      }
      toggleStationWindow(stationId)
      setTimeout(() => {
        loadActiveOrder()
      }, 1000)
    },
  });
}


function putUmbrella(stationId) {
  $.ajax({
    type: "POST",
    url: `/station-map/put-umbrella`,
    data: {
      station_id: stationId
    },
    success: function (data) {
      if (data.status === "ok") {
        // alert(`Заказ №${data.order_id} закрыт\nСпасибо за то, что пользуетесь нашим сервисом!`)
        setIsInteractingWithStation(true);
      }
      toggleStationWindow(stationId)
      setTimeout(() => {
        loadActiveOrder()
      }, 1000)
    },
  });
}


function showStationInfo(stationId) {
  const station = stations.find(station => station.id == stationId);
  map.update({location: {center: [station.longitude, station.latitude], zoom: 16, duration: 2000}});
  toggleStationWindow(stationId)
}


function showStationInfoFromSearch(stationId) {
  hideSearch()
  showStationInfo(stationId)
}


function initSearch(stations) {
  const searchItemsContainer = document.getElementById("searchItemsContainer");
  searchItemsContainer.innerHTML = ''
  for (const station of stations) {
    const searchItem = document.createElement("div");
    searchItem.className = "search-item";
    searchItem.innerHTML = `
      <div class="search-station-info">
        <div class="windowContent">

          <div class="left-right-container">
            <div class="left" style="background-image: url('${station.picture}');"></div>
            <div class="right">
              <div class="titleContainer">
                <span class="number">№${station.id}</span>
                <span class="title">${station.title}</span>
                <span class="address">${station.address}</span>
              </div>
              <div class="btnContainer">
                <button class="putTakeBtn"><i class="bi bi-arrow-up-circle"></i> ${station.can_take}</button>
                <button class="putTakeBtn"><i class="bi bi-arrow-down-circle"></i> ${station.can_put}</button>
                <button class="markerBtn" onclick="showStationInfoFromSearch('${station.id}')">Показать</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      `;

      searchItemsContainer.appendChild(searchItem);
  }

  $("#search").on("input", function() {
    const searchText = $(this).val().toLowerCase();
    $(".search-item").each(function() {
      const stationTitle = $(this).find(".titleContainer").text().toLowerCase();
      if (stationTitle.includes(searchText)) {
        $(this).show();
      } else {
        $(this).hide();
      }
    });
  });
}


function showSearch() {
  $("#searchOffcanvas").addClass("show");
}

function hideSearch() {
  $("#searchOffcanvas").removeClass("show");
}


/* Получение статуса заказа во время взаимодействия со станцией */
async function getOrderStatus() {
  return await new Promise((resolve, reject) => {
    $.ajax({
      type: "GET",
      url: `/station-map/get-order-status`,
      success: function (data) {
        if (data.status === "ok") {
          console.log(data.order_status)
          resolve(data)
        }
      },
      error: function (e) {
        reject(e)
      }
    });
  });
}


function setIsInteractingWithStation(val) {
  if (val) {
    checkOrderStatusForUpdates();
  }
  oldStationInteractionOrderStatus = null;
  localStorage.setItem("isInteractingWithStation", val);
  reInitStations();
}


function showStationInteractionModal(content) {
  $("#stationInteractionModal").removeClass("show")

  setTimeout(() => {
    $("#stationInteractionModal").html(content)
    $("#stationInteractionModal").addClass("show")
  }, 300)
}


async function checkOrderStatusForUpdates() {
  if (localStorage.getItem("isInteractingWithStation") === "true") {
    const data = await getOrderStatus();
    console.log(data);

    if (oldStationInteractionOrderStatus === data.order_status) {
      return;
    }
    
    switch (data.order_status) {
      case "station_opened_to_take":
        showStationInteractionModal(`
          <div class="modal-body">
            <div class="modal-content">
              Возьмите зонт из ячейки №${data.slot}
            </div>
          </div>
        `)
        break;
      case "in_the_hands":
        if (oldStationInteractionOrderStatus === 'station_opened_to_take') {
          showStationInteractionModal(`
            <div class="modal-body">
              <div class="modal-header station-interaction-modal-header">
                <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
              </div>
              <div class="modal-content">
                Приятного пользования и хорошей погоды!
              </div>
            </div>
          `)
        } else if (oldStationInteractionOrderStatus === 'station_opened_to_put') {
          if (timesBeforePutUmbrellaTimeout < 2) {
            timesBeforePutUmbrellaTimeout += 1
            return
          }
          showStationInteractionModal(`
            <div class="modal-body">
              <div class="modal-header station-interaction-modal-header">
                <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
              </div>
              <div class="modal-content">
                Время для возврата зонта в станцию истекло.<br>
                Попробуйте еще раз.
              </div>
            </div>
          `)
        } else if (oldStationInteractionOrderStatus === null) {
          showStationInteractionModal(`
            <div class="modal-body">
            <div class="modal-content">
              Взаимодействие с банком...
            </div>
          </div>
          `)
        }
        if (oldStationInteractionOrderStatus !== null) {
          setIsInteractingWithStation(false);
        }
        break;
      case "timeout_exceeded":
        showStationInteractionModal(`
          <div class="modal-body">
            <div class="modal-header station-interaction-modal-header">
              <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
            </div>
            <div class="modal-content">
              Время на взятие зонта истекло. Ваш депозит скоро Вам вернется.<br>
              Мы можете попробовать взять зонт еще раз.
            </div>
          </div>
        `)
        setIsInteractingWithStation(false);
        break;
      case "bank_error":
          showStationInteractionModal(`
            <div class="modal-body">
              <div class="modal-header station-interaction-modal-header">
                <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
              </div>
              <div class="modal-content">
                Произошла ошибка с созданием депозита.<br>
                Попробуйте еще раз.
              </div>
            </div>
          `)
          setIsInteractingWithStation(false);
          break;
      case "station_opened_to_put":
        showStationInteractionModal(`
          <div class="modal-body">
            <div class="modal-content">
              Пожалуйста, положите зонт в ячейку №${data.slot}
            </div>
          </div>
        `)
        break;
      case "closed_successfully":
        // showStationInteractionModal(`
        //   <div class="modal-body">
        //     <div class="modal-header station-interaction-modal-header">
        //       <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
        //     </div>
        //     <div class="modal-content">
        //       Спасибо за пользование нашим сервисом!
        //     </div>
        //   </div>
        // `)
        setIsInteractingWithStation(false);
        // Feedback form
        showFeedbackForm()
        break;
      default:
        showStationInteractionModal(`
          <div class="modal-body">
            <div class="modal-header station-interaction-modal-header">
              <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
            </div>
            <div class="modal-content">
              Произошла непредвиденная ошибка(
            </div>
          </div>
        `)
        setIsInteractingWithStation(false);
        break;
    }


    oldStationInteractionOrderStatus = data.order_status;
    timesBeforePutUmbrellaTimeout = 0
  }
}

setInterval(checkOrderStatusForUpdates, 1000);


/* Payments */
function showPayment(user_id, station_id) {
  let widget = new cp.CloudPayments();
  widget.pay('auth', {
    publicId: 'pk_dbf527223bbda31ff8805e8316148', //id из личного кабинета
    description: 'Депозит за зонт — WISH', //назначение
    amount: 300, //сумма
    currency: 'RUB', //валюта
    accountId: user_id, //идентификатор плательщика (необязательно)
    // invoiceId: order_id, //номер заказа  (необязательно)
    skin: "mini", //дизайн виджета (необязательно)
    autoClose: 3, //время в секундах до авто-закрытия виджета (необязательный)
    data: {
      paymentType: 'deposit',
      stationTake: station_id,
      paymentMode: 'manual'
    },
  },
  {
      onSuccess: function (options) { // success
        setIsInteractingWithStation(true);
      },
      onFail: function (reason, options) { // fail
        showStationInteractionModal(`
          <div class="modal-body">
            <div class="modal-header station-interaction-modal-header">
              <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
            </div>
            <div class="modal-content">
              Произошла ошибка с созданием депозита.<br>
              Попробуйте еще раз.
            </div>
          </div>
        `)
        setIsInteractingWithStation(false);
      },
      onComplete: function (paymentResult, options) { //Вызывается как только виджет получает от api.cloudpayments ответ с результатом транзакции.
        //например вызов вашей аналитики
      }
  }
  )
};


/* QR code scanner */
function initQRScanner() {
  shouldStopQRScanning = false;
  QRScanningTorch = false;

  const video = document.getElementById('qr-scanner-camera');
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  const mediaConfig = {
    video: {
        width: { ideal: window.innerHeight*2 },
        height: { ideal: window.innerWidth*2 },
        facingMode: "environment",
        // torch: true
    }
};

  navigator.mediaDevices.getUserMedia(mediaConfig)
    .then(stream => {
      QRScanningTrack = stream.getVideoTracks()[0];
      video.srcObject = stream;
      video.setAttribute("playsinline", true);
      requestAnimationFrame(tick);
  })
  .catch(err => {
    alert("Не удается получить доступ к камере")
  });

  function tick() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.height = video.videoHeight;
      canvas.width = video.videoWidth;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
      
      const qrCode = jsQR(imageData.data, canvas.width, canvas.height);

      if (qrCode) {
        try {
          const url = new URL(qrCode.data);
          const stationId = url.searchParams.get('station_id');
          if (stationId) {
            hideQRScannerModal();
            showStationInfo(stationId);
            shouldStopQRScanning = true;
          }
        } catch {}
      }
    }

    if (!shouldStopQRScanning) {
      requestAnimationFrame(tick);
    }
  }
}

function showQRScannerModal() {
  initQRScanner();
  $("#qrScannerModal").addClass("show");
}

function hideQRScannerModal() {
  shouldStopQRScanning = true;
  QRScanningTorch = false;
  if (QRScanningTrack) {
    QRScanningTrack.stop();
  }
  $("#qrScannerModal").removeClass("show");
}


function findByStationNumber() {
  hideQRScannerModal();
  showSearch();
}

async function toggleFlashlight() {
  const capabilities = QRScanningTrack.getCapabilities();

  if (!capabilities.torch) {
      alert('Фонарик не поддерживается на этом устройстве.');
      return;
  }

  QRScanningTorch = !QRScanningTorch;
  await QRScanningTrack.applyConstraints({ advanced: [{ torch: QRScanningTorch }] });
}


/* Feedback form */
function showFeedbackForm() {
  showStationInteractionModal(`
    <div class="modal-body">
      <div class="modal-header station-interaction-modal-header">
        <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
      </div>
      <div class="modal-content">
        <h3 class="feedback-header">Спасибо за пользование нашим сервисом!</h3>
        <p class="feedback-p">Пожалуйста, оцените качество обслуживания и оставьте нам свои пожелания.</p>
        <div class="feedback-rate-container">
          <div class="feedback-rate">
            <input type="radio" id="feedback-star5" name="feedback-rate" value="5" onclick="changedStarRating()" />
            <label for="feedback-star5" title="Отлично">5 stars</label>
            <input type="radio" id="feedback-star4" name="feedback-rate" value="4" onclick="changedStarRating()" />
            <label for="feedback-star4" title="Хорошо">4 stars</label>
            <input type="radio" id="feedback-star3" name="feedback-rate" value="3" onclick="changedStarRating()" />
            <label for="feedback-star3" title="Нормально">3 stars</label>
            <input type="radio" id="feedback-star2" name="feedback-rate" value="2" onclick="changedStarRating()" />
            <label for="feedback-star2" title="Плохо">2 stars</label>
            <input type="radio" id="feedback-star1" name="feedback-rate" value="1" onclick="changedStarRating()" />
            <label for="feedback-star1" title="Очень плохо">1 star</label>
          </div>
        </div>

        <div class="feedback-text-and-btn-container">
          <textarea class="feedback-textarea" id="feedback-textarea" placeholder="Пожелание или замечание" rows=5></textarea>
          <button class="feedback-submit" onclick="submitFeedback()" disabled>Отправить</button>
        </div>
      </div>
    </div>
  `)
}

function changedStarRating() {
  const rate = $('input[name="feedback-rate"]:checked').val();
  if (rate) {
    $(".feedback-submit").prop("disabled", false)
  } else {
    $(".feedback-submit").prop("disabled", true)
  }
}

function submitFeedback() {
  const rate = $('input[name="feedback-rate"]:checked').val();
  const text = $("#feedback-textarea").val();
  if (!rate) return
  
  $.ajax({
    url: "/station-map/order-feedback",
    type: "POST",
    data: JSON.stringify({
      rate: rate,
      text: text
    }),
    contentType: "application/json",
    success: function(data) {
      showStationInteractionModal(`
        <div class="modal-body">
          <div class="modal-header station-interaction-modal-header">
            <span class="modal-close" onclick="$('#stationInteractionModal').removeClass('show')"><i class="bi bi-x-lg"></i></span>
          </div>
          <div class="modal-content">
            Спасибо за ваш отзыв!
          </div>
        </div>
      `)
    }
  });
}


let map = null;
let stations = []
let activeStationWindow = null;
let hasActiveOrder = false;
let hasAuth = false;
let oldStationInteractionOrderStatus = null;
let timesBeforePutUmbrellaTimeout = 0;

let shouldStopQRScanning = false;
let QRScanningTrack = null;
let QRScanningTorch = false;


loadStations().then((data) => {
  stations = data;
  initMap();
  initSearch(stations);
});

function reInitStations() {
  loadStations().then((data) => {
    stations = data;
    drawStations();
    initSearch(stations);
  });
  loadActiveOrder();
}

// initMap();
checkAuth()
loadActiveOrder()

