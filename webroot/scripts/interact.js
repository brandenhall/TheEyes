(function() {
    websocket = new WebSocket("ws://theey.es:8080/");
    websocket.onopen = function(evt) {

    };
    websocket.onclose = function(evt) {

    };
    websocket.onmessage = function(evt) {
        var data = JSON.parse(evt.data);

        if (data.type == "status") {
            if (data.has_brainstem == true) {
                var red = $("<button>Red</button>");
                red.click(function() {
                    websocket.send('{"type":"set_color", "color":[255,0,0]}');
                });
                var green = $("<button>Red</button>");
                green.click(function() {
                    websocket.send('{"type":"set_color", "color":[0,255,0]}');
                });
                var blue = $("<button>Red</button>");
                blue.click(function() {
                    websocket.send('{"type":"set_color", "color":[0,0,255]}');
                });
                $("#message").empty();
                $("#message").append(red);
                $("#message").append(green);
                $("#message").append(blue);
            } else {
                $("#message").empty();
                $("#message").append('<h3 class="center-text">The Eyes are resting right now.</h3><p class="center-text">Sorry.</p>');
            }
        }
    };
    websocket.onerror = function(evt) {

    };
})();
