let socket = new WebSocket('ws://127.0.0.1:8765');
let status1 = true
let intervalID
document.addEventListener('mouseup', async (event) => {
  let selectedText = window.getSelection().toString().trim();
  socket.send('init20230501')
  if (intervalID) {
    clearInterval(intervalID);
  }  
  // span
  new_span('init')
  if (selectedText) {
    intervalID = setInterval(function() {
      console.log(1);
      new_span('do')
      if (status1) {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send('do20230501')
        } else {
          alert('ws连接关闭,请重启浏览器并检查python后端是否报错')
        }
        status1 = false
      }
    }, 1000);
  }
})

socket.addEventListener('message', (event)=>{
  if (event.data == 'pass20230501'){
    document.querySelector('#next_translation').click()
    status1 = true
  }
  if (event.data == 'paste20230501') {
    // span
    new_span('next')
    document.querySelector("#suggest_translation").click();
    setTimeout(() => {
      document.querySelector('#next_translation').click()
      status1 = true
    }, 2000);
  }
  if (event.data == 'done20230501') {
    new_span('paste')
    var text_box = document.querySelector("#translation");
    text_box.focus();
    text_box.value = ''
    socket.send('paste20230501')
  }
})

function new_span(text){
  var newSpan = document.createElement('span');
  newSpan.className = 'newspan';
  newSpan.textContent =  text;
  newSpan.style.top = '200px';
  newSpan.style.left = '200px';
  document.body.appendChild(newSpan);
  setTimeout(() => {
    newSpan.remove();
  }, 1000);
}