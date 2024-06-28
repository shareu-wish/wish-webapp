function openSection(name) {
  $(".inputPhoneContainer").hide();
  $(".preVerifyPhoneContainer").hide();
  $(".verifyPhoneContainer").hide();

  $(`.${name}Container`).css({ display: "flex" });
}

function goToPreVerification() {
  let phone = $("#phone").val();
  if (
    phone
      .replaceAll(" ", "")
      .replaceAll("(", "")
      .replaceAll(")", "")
      .replaceAll("+", "")
      .replaceAll("-", "").length !== 11
  )
    return alert("Введите номер телефона");
  sessionStorage.setItem("phone", phone);
  $("#yourPhone").text(phone);

  openSection("preVerifyPhone");
}

function startFlashCall() {
  if (
    new Date().getTime() -
      Number(sessionStorage.getItem("startFlashCallTime")) -
      60 * 1000 <
      0 &&
    sessionStorage.getItem("startFlashCallTime") != null
  ) {
    openSection("verifyPhone");
    return showRestartTimer();
  }

  openSection("verifyPhone");
  $.ajax({
    url: "/auth/start-flash-call",
    method: "post",
    data: {
      phone: sessionStorage.getItem("phone"),
    },
    success: function (data) {
      if (data.status !== "ok") alert("Произошла ошибка!");
    },
  });
  setRestartTimer();
}

function setRestartTimer() {
  sessionStorage.setItem("startFlashCallTime", new Date().getTime());
  showRestartTimer();
}

function showRestartTimer() {
  const timer = setInterval(() => {
    const timeLeft =
      new Date().getTime() -
      Number(sessionStorage.getItem("startFlashCallTime")) -
      60 * 1000;
    $("#restartTimer").text(
      `Позвонить еще раз: ${Math.floor(-timeLeft / 1000)}`
    );
    // $("#restartTimer").css({ color: "gray" });
    $("#restartTimer").addClass("restartTimerDisabled");
    if (timeLeft > 0) {
      $("#restartTimer").text(`Позвонить еще раз`);
      // $("#restartTimer").css({ color: "#004daf" });
      $("#restartTimer").removeClass("restartTimerDisabled");
      clearInterval(timer);
    }
  }, 100);
}

$("#phone").mask("+7 (999) 999 99-99");

// Обработка поля ввода кода
const ELS_pinEntry = document.querySelectorAll(".pinEntry");
ELS_pinEntry.forEach((el) => {
  //   el.addEventListener("focusin", (evt) => {
  //     const EL_input = evt.currentTarget;
  //     if (EL_input.value.length >= 4) EL_input.select();
  //   });
  el.addEventListener("input", (evt) => {
    const EL_input = evt.currentTarget;
    if (EL_input.value.length >= 4) {
      EL_input.value = EL_input.value.slice(0, 4);
      if (sessionStorage.getItem("startFlashCallTime") !== "0") {
        sessionStorage.setItem("startFlashCallTime", 0);
        $.ajax({
          url: "/auth/check-code",
          method: "post",
          data: {
            code: EL_input.value,
            phone: sessionStorage.getItem("phone"),
          },
          success: function (data) {
            if (data.status === "ok" && data.is_verified) {
              const urlParams = new URLSearchParams(window.location.search);
              const from_url = urlParams.get("from_url");
              if (from_url) {
                window.location.href = from_url;
              } else {
                window.location.href = "/station-map";
              }
            } else {
              if (data.attempts_exceeded) {
                alert("Превышено количество попыток ввода кода");
                location.reload();
              } else if (data.timeout_exceeded) {
                alert("Время действия кода истекло");
                location.reload();
              } else {
                alert("Неверный код");
                EL_input.value = "";
                sessionStorage.setItem("startFlashCallTime", 1);
              }
            }
          },
        });
      }
    }
  });
});

// Восстановить поле ввода кода, если минута не прошла, а страницу обновили
if (
  new Date().getTime() -
    Number(sessionStorage.getItem("startFlashCallTime")) -
    60 * 1000 <
    0 &&
  sessionStorage.getItem("startFlashCallTime") != null
) {
  openSection("verifyPhone");
  showRestartTimer();
}
