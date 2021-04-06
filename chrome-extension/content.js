var blocked_html = ' <div> <h2 style="font-family: sans-serif;">Domain is blocked - workaholic</h2> <iframe src="https://giphy.com/embed/4U6FaR1YSLlUCfSrV6" width="480" height="270" frameBorder="0" class="giphy-embed" allowFullScreen></iframe> </div> <style> body { text-align: center; background-color: #06d6a0; } div { background-color: #f1faee; display: inline-block; margin-top: 100px; padding: 30px; padding-top: none; border-radius: 10px; } h2 { margin-top: 0px; font-size: 30px; } </style>'
var host = window.location.host;
chrome.runtime.sendMessage({ method: "getBlocked" }, function (response) {
  if ('blocked_domains' in response) {
    var block = response.blocked_domains;
    if (block.includes(host.replace("www.", ""))) {
      document.documentElement.innerHTML = '';
      document.documentElement.innerHTML = blocked_html;
      document.documentElement.scrollTop = 0;
      fetch('http://' + response.host + ':' + response.port + '/bad-tab');
    }
  }
});