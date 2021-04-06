// set status
let status = document.getElementById("status");

chrome.storage.sync.get("connection", ({ connection }) => {
  if (connection=="ping") {
    status.innerHTML = "connected"
  }
});