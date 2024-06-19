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
    new YMapControls({ position: "bottom left" })
      // Add the geolocation control to the map
      .addChild(new YMapGeolocationControl({}))
  );

  document.getElementsByClassName("ymaps3x0--control-button")[0].click();

  const stations = [
    {
      station_id: 1,
      title: "Певческая капелла",
      address: "г. Санкт-Петербург, Набережная реки Мойки, 20",
      coords: [59.939936, 30.320801],
      image: "/static/img/pass.jpg",
      umbrellas_count: 5,
    },
    {
      station_id: 2,
      title: "Дом Таля",
      address: "г. Санкт-Петербург, Невский проспект, 6",
      coords: [59.936997, 30.314489],
      image: "/static/img/pass.jpg",
      umbrellas_count: 3,
    },
  ];

  for (const station of stations) {
    const markerElement = document.createElement("div");
    markerElement.className = "station-marker";
    markerElement.innerHTML = `
      <div onclick="toggleStationWindow('${station.station_id}')">
        <div class="umbrellas-count">${station.umbrellas_count}</div>
        <img src="/static/img/umbrella.svg">
      </div>
      <div class="station-info-window" id="${station.station_id}Window">
        <div class="windowContent">
          <div class="left" style="background-image: url('${station.image}');"></div>
          <div class="right">
            <div class="titleContainer">
              <span class="title">${station.title}</span>
              <span class="address">${station.address}</span>
            </div>
            <div class="btnContainer">
              <button class="markerBtn route" onclick="showRoute([${station.coords[0]}, ${station.coords[1]}])"><i class="bi bi-geo-alt-fill"></i> Маршрут</button>
              <button class="markerBtn take-umbrella"><i class="bi bi-umbrella-fill"></i> Взять зонт</button>
            </div>
          </div>
        </div>
      </div>
      `;

    const marker = new YMapMarker(
      {
        coordinates: station.coords.reverse(),
      },
      markerElement
    );

    map.addChild(marker);
  }
}

let activeStationWindow = null;

initMap();
