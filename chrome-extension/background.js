chrome.runtime.onStartup.addListener(() => {
  console.log('onStartup...');
  var xhr = new XMLHttpRequest();
  xhr.onload = function () {
    let res = JSON.parse(this.response);
    chrome.storage.sync.set(res);
  };
  xhr.open('GET', chrome.extension.getURL('config.json'), true);
  xhr.send();
  setInterval(getData, 5 * 1000);
});


chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.method == "getBlocked"){
    chrome.storage.sync.get(["blocked_domains", "status", "connection", "host", "port"], ({ blocked_domains, status, connection, host, port }) => {
      if (status == "work" && connection=="ping") {
        sendResponse({ blocked_domains: blocked_domains, host: host, port: port });
      } else {
        sendResponse({});
      }
    });
  }
  else
    sendResponse({});
  return true;
});


function getData() {
  chrome.storage.sync.get(["host", "port"], ({ host, port }) => {
    fetch('http://' + host + ':' + port+'/')
      .then(r => r.json())
      .then(result => {
        chrome.storage.sync.set(result);
      }
      ).catch(err => {
        chrome.storage.sync.set({ connection: "offline" });
      });
  });

}