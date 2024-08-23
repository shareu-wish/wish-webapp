function sendInstallStationRequest() {
  const organization = $("#installStationOrganization").val().trim();
  const city = $("#installStationCity").val().trim();
  const email = $("#installStationEmail").val().trim();
  const phone = $("#installStationPhone").val().trim();
  const text = $("#installStationText").val().trim();
  if (organization === "" || city === "" || text === "") {
    return alert("Заполните все обязательные поля!");
  }
  if (email === "" && phone === "") {
    return alert(
      "Укажите хотя бы один контактный способ (email или номер телефона)!"
    );
  }

  // TODO: Убрать, когда будет готов сервер
  return alert("К сожалению, эта форма сейчас не работает(");

  $.ajax({
    url: "/support",
    type: "POST",
    data: {
      organization: organization,
      city: city,
      email: email,
      phone: phone,
      text: text,
    },
    success: function (res) {
      alert("Ваш вопрос отправлен!");
      $("#installStationOrganization").val("");
      $("#installStationCity").val("");
      $("#installStationEmail").val("");
      $("#installStationPhone").val("");
      $("#installStationText").val("");
    },
  });
}


function waitImagesAndShowSite() {
  let loading = [];

  $("img").each(function () {
    loading.push(
      new Promise((resolve) => {
        let url = $(this).attr("src");
        let img = new Image();
        img.src = url;
        img.onload = () => {
          resolve();
        };
      })
    );
  });

  Promise.all(loading).then(() => {
    setTimeout(() => {
      $("#preloader").hide();
    }, 300);
  });
}


waitImagesAndShowSite();


$("#firstSection").mousemove(function (e) {
  const x = e.pageX - this.offsetLeft;
  const y = e.pageY - this.offsetTop;

  $(this).css({ "--mouse-x": `${x}px`, "--mouse-y": `${y}px` });
});


$('.install-station-card').hover(function() {
  // on mouse enter
  const src_anim = $(this).find('img').attr('data-anim');
  $(this).find('img').attr('src', src_anim);
}, function() {
  // on mouse leave
  const src_freeze = $(this).find('img').attr('data-freeze');
  $(this).find('img').attr('src', src_freeze);
})
