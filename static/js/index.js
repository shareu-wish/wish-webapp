function loadWeather() {
  $.getJSON("https://api.ipify.org?format=json", function (data) {
    $.getJSON(
      `https://ipwho.is/${data.ip}?lang=ru`,
      function (data2) {
        let city = data2.city;
        $.getJSON(
          `https://api.open-meteo.com/v1/forecast?latitude=${data2.latitude}&longitude=${data2.longitude}&current=temperature_2m,is_day,weathercode`,
          function (data3) {
            $.getJSON("/static/weatherCodes.json", function (weatherCodes) {
              const weatherCode = data3.current.weathercode;
              const timeOfDay = data3.current.is_day ? "day" : "night";
              const weather =
                weatherCodes[weatherCode][timeOfDay]["description"];

              if (city && weather) {
                // $("#current-weather").show();
                $("#current-weather-city").text(city);
                $("#current-weather-description").text(weather);
              } else {
                $("#current-weather").hide();
              }
            });
          }
        );
      }
    );
  });
}


function sendQuestion() {
    const name = $("#supportName").val().trim();
    const city = $("#supportCity").val().trim();
    const email = $("#supportEmail").val().trim();
    const phone = $("#supportPhone").val().trim();
    const text = $("#supportText").val().trim();
    if (name === "" || city === "" || text === "") {
        return alert("Заполните все обязательные поля!");
    }
    if (email === "" && phone === "") {
        return alert("Укажите хотя бы один контактный способ (email или номер телефона)!");
    }

    // TODO: Убрать, когда будет готов сервер
    return alert("К сожалению, эта форма сейчас не работает(");

    $.ajax({
        url: "/support",
        type: "POST",
        data: {
            name: name,
            city: city,
            email: email,
            phone: phone,
            text: text
        },
        success: function (res) {
            alert("Ваш вопрос отправлен!");
            $("#supportName").val("");
            $("#supportCity").val("");
            $("#supportEmail").val("");
            $("#supportPhone").val("");
            $("#supportText").val("");
        }
    });
}


function createRain() {
  const coord = Math.random() * window.innerWidth
  const umbrella = document.getElementById("take-umbrella-img");
  const umbrellaRect = umbrella.getBoundingClientRect();
  let TTL = 1000;

  const drop = document.createElement("div");

  if (coord >= umbrellaRect.left && coord <= umbrellaRect.right) {
    drop.className = "drop on-umbrella";
    TTL = 450
  } else {
    drop.className = "drop";
  }

  drop.style.left = coord + "px";
  document.getElementById("take-umbrella-rain").appendChild(drop);
  setTimeout(function () {
    drop.remove();
  }, TTL);
  
  setTimeout(createRain, 5);
}


function waitImagesAndShowSite() {
  let loading = [];

  $("img").each(function() {
    loading.push(new Promise(resolve => {
      let url = $(this).attr('src');
      let img = new Image();
      img.src = url;
      img.onload = () => {
        resolve();
      }
    }));
  });

  Promise.all(loading).then(()=>{
    setTimeout(() => {
      $('#preloader').hide();
    }, 300);
  })
}


waitImagesAndShowSite()
loadWeather();

$(document).ready(function () {
  const faqs = document.querySelectorAll(".accordion .question-container");

  faqs.forEach(function (faq) {
    faq.addEventListener("click", function () {
      this.parentNode.classList.toggle("active");
    });
  });
});

createRain();


/* Пасхалка) */
let takeUmbrellaClicks = 0;
$("#take-umbrella-img").on("click", function () {
  takeUmbrellaClicks += 1;
  if (takeUmbrellaClicks === 5) {
    alert("Что ты делаешь?")
  } else if (takeUmbrellaClicks === 15) {
    alert("Прекрати!")
  } else if (takeUmbrellaClicks === 30) {
    alert("Я что тебе, хомяк что ли?")
  } else if (takeUmbrellaClicks === 40) {
    alert("Ладно, сам напросился!")
    window.open("https://rutube.ru/video/c6cc4d620b1d4338901770a44b3e82f4/?t=0", "_blank");
  }
});
