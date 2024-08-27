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
        `<div class="close-station-info-window" onclick="$('#mainWindow').hide();activeStationWindow = null;$('#QRScannerButton').show();"><i class="bi bi-x-lg"></i></div>`);
    $("#mainWindow").show();
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


async function initMap() {
  await ymaps3.ready;

  const {
    YMap,
    YMapDefaultSchemeLayer,
    YMapDefaultFeaturesLayer,
    YMapControls,
    YMapMarker,
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
                <button class="markerBtn" onclick="showRoute([${station.latitude}, ${station.longitude}])"><i class="bi bi-geo-alt-fill"></i> Маршрут</button>
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
  }

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

  $.ajax({
    type: "POST",
    url: `/station-map/take-umbrella`,
    data: {
      station_id: stationId
    },
    success: function (data) {
      if (data.status === "ok") {
        alert(`Заказ №${data.order_id}\nВы можете забрать зонт из ячейки ${data.slot}`)
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
        alert(`Заказ №${data.order_id} закрыт\nСпасибо за то, что пользуетесь нашим сервисом!`)
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


function initQRScanner() {
  shouldStopQRScanning = false;

  const video = document.getElementById('qr-scanner-camera');
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  const mediaConfig = {
    video: {
        width: { ideal: window.innerHeight*2 },
        height: { ideal: window.innerWidth*2 },
        facingMode: "environment"
    }
};

  navigator.mediaDevices.getUserMedia(mediaConfig)
    .then(stream => {
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
  $("#qrScannerModal").removeClass("show");
}


function findByStationNumber() {
  hideQRScannerModal();
  showSearch();
}

function toggleFlashlight() {

}



let map = null;
let stations = []
let activeStationWindow = null;
let hasActiveOrder = false;
let hasAuth = false;

let shouldStopQRScanning = false;


loadStations().then((data) => {
  stations = data;
  initMap();
  initSearch(stations);
});
// initMap();
checkAuth()
loadActiveOrder()

