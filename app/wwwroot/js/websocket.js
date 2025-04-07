const connection = new signalR.HubConnectionBuilder()
  .withUrl("/NotificationHub")
  .withAutomaticReconnect()
  .build();

connection.on("mesaj", function (message) {
  if (
    window.location.href !== "http://localhost:5029/get_date/Webhook/grafice"
  ) {
    showPopupNotification(
      "Datele tale sunt gata!",
      "Apasa aici pentru a vedea graficele generate.",
      "/get_date/Webhook/grafice"
    );
  }
  console.log(message);
});

//functie pentru a salva connection id ul in sesiune (con_idul signalr)

export async function start() {
  try {
    await connection.start();
    console.log("Conexiunea SignalR este stabilită!");

    const connectionId = connection.connectionId;
    const response = await fetch("/get_date/Webhook/SaveConnectionId", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ idd: connectionId }),
    });
    if (response.ok) {
      console.log("ok signal r salvat in sesh");
    } else {
      console.error("Eroare la salvarea ConnectionId:", await response.text());
    }
  } catch (err) {
    console.error("Eroare la conectarea SignalR:", err);
    setTimeout(startSignalRConnection, 5000);
  }
}
start();
function showPopupNotification(title, message, link) {
  const notification = document.createElement("div");
  notification.className = "popup-notification";
  notification.innerHTML = `
        <h3>${title}</h3>
        <p>${message}</p>
        <button id="view-details">Vezi detalii</button>
    `;

  // Stiluri pentru notificare
  const styles = `
        .popup-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        }
        .popup-notification h3 {
            margin: 0 0 10px;
        }
        .popup-notification p {
            margin: 0 0 10px;
        }
        .popup-notification button {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
        }
        .popup-notification button:hover {
            background: #0056b3;
        }
    `;
  const styleSheet = document.createElement("style");
  styleSheet.type = "text/css";
  styleSheet.innerText = styles;
  document.head.appendChild(styleSheet);

  // Adauga notif
  document.body.appendChild(notification);

  // Eveniment pentru buton
  document.getElementById("view-details").onclick = () => {
    window.location.href = link;
  };

  setTimeout(() => {
    notification.remove();
  }, 20000);
}

document.getElementById("csvv").onclick = async () => {
  try {
    const response = await fetch("/get_date/Webhook/DownloadCSV");
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "CSVfiles.zip";
      a.click();
      window.URL.revokeObjectURL(url);
    } else {
      const error = await response.json();
      document.getElementById("csv_e").innerText = error.error;
    }
  } catch (error) {
    document.getElementById("csv_e").innerText = error;
  }
};

document.getElementById("graficee").onclick = async () => {
  try {
    const response = await fetch("/get_date/Webhook/DownloadGrafice");
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "GRAFICEfiles.zip";
      a.click();
      window.URL.revokeObjectURL(url);
    } else {
      const error = await response.json();
      document.getElementById("grafice_e").innerText = error.error;
    }
  } catch (error) {
    document.getElementById("grafice_e").innerText = error;
  }
};
