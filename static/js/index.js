function loadWeather() {
  $.getJSON("https://api.ipify.org?format=json", function (data) {
    $.getJSON(
      `http://www.geoplugin.net/json.gp?ip=${data.ip}&lang=ru`,
      function (data2) {
        let city = data2.geoplugin_city;
        if (!city) {
          city = data2.geoplugin_region;
        }
        $.getJSON(
          `https://api.open-meteo.com/v1/forecast?latitude=${data2.geoplugin_latitude}&longitude=${data2.geoplugin_longitude}&current=temperature_2m,is_day,weathercode`,
          function (data3) {
            $.getJSON("/static/weatherCodes.json", function (weatherCodes) {
              const weatherCode = data3.current.weathercode;
              const timeOfDay = data3.current.is_day ? "day" : "night";
              const weather =
                weatherCodes[weatherCode][timeOfDay]["description"];

              if (city && weather) {
                $("#current-weather").show();
                $("#current-weather-city").text(city);
                $("#current-weather-description").text(weather);
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


loadWeather();

$(document).ready(function () {
  const faqs = document.querySelectorAll(".accordion .question-container");

  faqs.forEach(function (faq) {
    faq.addEventListener("click", function () {
      this.parentNode.classList.toggle("active");
    });
  });
});


