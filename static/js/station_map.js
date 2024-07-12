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

const isMobileScreen = window.innerWidth <= 480;

function toggleStationWindow(windowId) {
  if (activeStationWindow === windowId) {
    $(`#${windowId}Window`).hide();
    $("#mainWindow").hide();
    activeStationWindow = null;
    return;
  }

  if (activeStationWindow) {
    $(`#${activeStationWindow}Window`).hide();
  }
  if (isMobileScreen) {
    $("#mainWindow").html($(`#${windowId}Window`).html() + 
        `<div class="close-station-info-window" onclick="$('#mainWindow').hide();activeStationWindow = null;"><i class="bi bi-x-lg"></i></div>`);
    $("#mainWindow").show();
  } else {
    $(`#${windowId}Window`).show();
  }
  activeStationWindow = windowId;
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

  const map = new YMap(document.getElementById("map"), {
    location: {
      center: [37.617698, 55.755864],
      zoom: 12,
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

  document.getElementsByClassName("ymaps3x0--control-button")[0].click();

  for (const station of stations) {
    const markerElement = document.createElement("div");
    markerElement.className = "station-marker";
    markerElement.innerHTML = `
      <div onclick="toggleStationWindow('${station.id}')">
        <div class="umbrellas-count">${station.can_take}</div>
        <img src="/static/img/umbrella.svg">
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


function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}


function checkAuth() {
  if (getCookie("authToken") === null) {
    $("#profile").hide()
    $("#headerLoginContainer").show()
  }
}


function takeUmbrella(stationId) {
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
    },
  });
}


let stations = []
let activeStationWindow = null;

loadStations().then((data) => {
  stations = data;
  console.log(stations);
  initMap();
});
// initMap();
checkAuth()

