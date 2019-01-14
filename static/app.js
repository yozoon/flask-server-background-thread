// Latency calculation and Socket.IO setup is based on
// https://github.com/Chainfrog-dev/async_flask_2

$(document).ready(function() {
  /******************************* SocketIO *********************************/
  namespace = '/test';

  // Connect to the Socket.IO server.
  // The connection URL has the following format:
  //     http[s]://<domain>:<port>[/<namespace>]
  var socket = io.connect(location.protocol + '//' + document.domain 
    + ':' + location.port + namespace);

  socket.on('connect', function() {
    $('#status').text('Status: Connected');
  });

  socket.on('log', function(msg) {
     $('#log-view').prepend('<p>'+msg+'</p>').html();
  });

  var clear_message_timer;
  socket.on('message', function(msg) {
     $('#message').text(msg);
     if(clear_message_timer != null) {
       clearTimeout(clear_message_timer);
     }
     clear_message_timer = setTimeout(function() {
      $('#message').text("");
    }, 2000);
  });

  // Button handler
  $("#start-button").click(function() {
    console.log('start');
    socket.emit('action','start');
  });
  $("#stop-button").click(function() {
    console.log('start');
    socket.emit('action','stop');
  });

  // Interval function that tests message latency by sending a "ping"
  // message. The server then responds with a "pong" message and the
  // round trip time is measured.
  var ping_pong_times = [];
  var start_time;
  setInterval(function() {
    start_time = (new Date).getTime();
    socket.emit('measure');
  }, 1000);

  // Handler for the "pong" message. When the pong is received, the
  // time from the ping is stored, and the average of the last 30
  // samples is average and displayed.
  var latency_display_timer;
  socket.on('pong', function(msg) {
    var latency = (new Date).getTime() - start_time;
    ping_pong_times.push(latency);
    ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
    var sum = 0;
    for (var i = 0; i < ping_pong_times.length; i++)
      sum += ping_pong_times[i];

    $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10
        + " ");
    $('#status').text('Status: Connected');
    if(latency_display_timer != null) {
      clearTimeout(latency_display_timer);
    }
    latency_display_timer = setTimeout(display_latency_timeout, 1000);
  });

  function display_latency_timeout() {
    $('#ping-pong').text('-- ');
    $('#status').text('Status: Disconnected');
  }
});
