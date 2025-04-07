// Write your JavaScript code.

//procesam fisierul incarcat prin butonul ,,incarca''
document
  .getElementById("fileInput")
  .addEventListener("change", handleFileSelect);

function handleFileSelect(event) {
  var file = event.target.files[0];
  if (file) {
    var formData = new FormData();
    formData.append("file", file);

    fetch("/get_date/Date/SendToApi", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("statusMessage").innerText = data.message;
      })
      .catch((error) => {
        document.getElementById("statusMessage").innerText =
          "Eroare la incarcarea fisierului " + error;
      });
  } else {
    document.getElementById("statusMessage").innerText = "Selectati un fisier.";
  }
}
///////

////update valorile sliderelor
function updateSpan(sliderId, valueId, min, max, step, value) {
  const slider = document.getElementById(sliderId);
  const sliderValue = document.getElementById(valueId);

  slider.min = min;
  slider.max = max;
  slider.step = step;
  slider.value = value;
  slider.addEventListener("input", function () {
    sliderValue.textContent = slider.value;
  });

  sliderValue.textContent = value;
}

updateSpan("slider", "sliderValue", 50, 90, 10, 80);
updateSpan("sliderK", "sliderValueK", 3, 21, 2, 3);
updateSpan("sliderF", "sliderValueF", 20, 100, 20, 20);

//functia aceasta este apelata dupa apasarea butonului start, pentru a reseta complet view-ul statistics
function clearCheckBox() {
  const checkboxes = document.querySelectorAll(
    "#div-alg input[type='checkbox']"
  );
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
    checkbox.disabled = false;
  });
}

///ne asiguram ca putem selecta un singur checkbox pentru algoritmi
function processCheckboxes() {
  const checkboxes = document.querySelectorAll(
    "#div-alg input[type='checkbox']"
  );

  const selected = Array.from(checkboxes).some((checkbox) => checkbox.checked);
  checkboxes.forEach((checkbox) => {
    if (!checkbox.checked) {
      checkbox.disabled = selected;
    } else {
      checkbox.disabled = false;
    }
  });
}

function processCheckboxes2() {
  const checkboxes = document.querySelectorAll(
    "#div-norme-interog input[type='checkbox']"
  );

  const selected = Array.from(checkboxes).some((checkbox) => checkbox.checked);
  checkboxes.forEach((checkbox) => {
    if (!checkbox.checked) {
      checkbox.disabled = selected;
    } else {
      checkbox.disabled = false;
    }
  });
}

//butonul de start, are nevoie de setari corespunzatoare+ fisier zip incarcat, asta va face metoda startProcessing din
//controller .
document.getElementById("start-b").addEventListener("click", async function () {
  const succes = await saveInSession("eRor");
  const verifyResponse = await fetch("/get_date/Date/verifyJsonn");
  const verifyData = await verifyResponse.json();
  console.log(verifyData);
  if (succes && verifyData.success) {
    fetch("/get_date/Date/startProcessing")
      .then((response) => response.json())
      .then((data) => {
        if (data.succes) {
          clearCheckBox();
          window.location.href = "/get_date/Webhook/grafice";
        } else {
          document.getElementById("eRor").innerText = data.message;
        }
      })
      .catch((err) => console.error("Eroare", err));
  }
});
///pentru a verifica setarile curente(se afiseaza setarile stocate in python api.)
document
  .getElementById("verif-session")
  .addEventListener("click", async function () {
    const succes = await saveInSession("eRRor");

    if (succes) {
      fetch("/get_date/Date/verifyJsonn")
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            document.getElementById("eRRor").innerText =
              "Setarile sunt " + JSON.parse(JSON.stringify(data.data));
          } else {
            document.getElementById("eRRor").innerText = "Date " + data.message;
          }
        })
        .catch((err) => console.error("Eroare", err));
    }
  });

//pt salvarea setarilor curente de pe pagina in sesiunea .net mvc
async function saveInSession(id) {
  var norme = Array.from(
    document.querySelectorAll("#div-norme input:checked")
  ).map((el) => el.name);
  if (norme.length == 0) {
    norme = ["1", "2", "infinit", "cos"];
  }
  const data = {
    alg: document.querySelector("#div-alg input:checked")?.name || null,
    norme: norme,
    training: document.getElementById("slider").value,
    k: document.getElementById("sliderK").value,
    fantome: document.getElementById("sliderF").value,

    optiuni: Array.from(
      document.querySelectorAll("#div-opt input:checked")
    ).map((el) => el.name),
  };
  try {
    const response = await fetch("/get_date/Date/SaveSessionData", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const responseData = await response.json();
    if (responseData.success) {
      console.log("lol?");
      return true;
    } else {
      document.getElementById(id).innerText =
        "Ai selectat setarile cum trebuie? " + responseData.message;
      return false;
    }
  } catch (err) {
    console.error("Eroare", err);
    return false;
  }
}
