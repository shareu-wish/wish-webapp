function toggleStationWindow(windowId) {
  if (activeStationWindow === windowId) {
    $(`#${windowId}Window`).hide();
    activeStationWindow = null;
    return;
  }

  if (activeStationWindow) {
    $(`#${activeStationWindow}Window`).hide();
  }
  $(`#${windowId}Window`).show();
  activeStationWindow = windowId;
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
      <div class="window" id="${station.station_id}Window">
        <div class="windowContent">
          <div class="left" style="background-image: url('${station.image}');"></div>
          <div class="right">
            <div class="titleContainer">
              <span class="title">${station.title}</span>
              <span class="address">${station.address}</span>
            </div>
            <div class="btnContainer">
            <button class="markerBtn ">
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
