(function($) {
    var ANSWER_ANOTHER_DELAY = 12000;
    var MAX_ATTEMPTS = 3;
    var MAX_TIME = 10000;

    var lat = NaN;
    var lon = NaN;
    var requiresGeo = false;
    var lastCommand = null;
    var currentQuestion = null;
    var makerProbability = 0.5;
    var attempts = 0;
    var questionTimeout;

    var templates = {
        "Human": ["ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","5c5c5c","2e2e2e","2e2e2e","5c5c5c","ffffff","2e2e2e","5c5c5c","2e2e2e","5c5c5c","2e2e2e","2e2e2e","2e2e2e","000000","000000","2e2e2e","2e2e2e","5c5c5c","000000","000000","000000","5c5c5c","2e2e2e","2e2e2e","000000","000000","2e2e2e","2e2e2e","2e2e2e","5c5c5c","2e2e2e","5c5c5c","2e2e2e","ffffff","5c5c5c","2e2e2e","2e2e2e","5c5c5c","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff"],
        "Cat": ["ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","5c5c5c","5c5c5c","5c5c5c","5c5c5c","ffffff","5c5c5c","2e2e2e","5c5c5c","2e2e2e","5c5c5c","2e2e2e","2e2e2e","2e2e2e","2e2e2e","2e2e2e","2e2e2e","000000","000000","000000","000000","000000","2e2e2e","2e2e2e","2e2e2e","2e2e2e","2e2e2e","2e2e2e","5c5c5c","2e2e2e","5c5c5c","2e2e2e","5c5c5c","ffffff","5c5c5c","5c5c5c","5c5c5c","5c5c5c","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff"],
        "Alien": ["ffffff","2e2e2e","ffffff","ffffff","5c5c5c","5c5c5c","ffffff","ffffff","ffffff","2e2e2e","ffffff","ffffff","ffffff","ffffff","5c5c5c","5c5c5c","ffffff","ffffff","ffffff","2e2e2e","2e2e2e","2e2e2e","ffffff","ffffff","5c5c5c","000000","030303","5c5c5c","ffffff","2e2e2e","000000","000000","000000","2e2e2e","ffffff","5c5c5c","000000","000000","5c5c5c","ffffff","ffffff","2e2e2e","2e2e2e","2e2e2e","ffffff","ffffff","ffffff","5c5c5c","5c5c5c","ffffff","ffffff","ffffff","ffffff","2e2e2e","ffffff","ffffff","ffffff","5c5c5c","5c5c5c","ffffff","ffffff","2e2e2e","ffffff"]
    };

    var colors = {
        "Brown": ["",""],
        "Blue": ["",""],
        "Green": ["",""],
        "Red": ["",""],
        "Yellow": ["",""],
        "Purple": ["",""],
        "Orange": ["",""],
        "Pink": ["",""],
        "Grey": ["",""],
    };

    var restlessness = {
        "Relaxed": 0.015,
        "Excited": 0.15
    };

    function onWebsocketOpen(evt) {

    }

    function onWebsocketClose(evt) {
        if (attempts < MAX_ATTEMPTS) {
            showConnecting();
            connect();
        } else {
            showUnavailable();
        }
        ++attempts;
    }

    function onWebsocketError(evt) {
        websocket.close();
        showAsleep();
    }

    function selectResponse(evt) {
        var target = $(evt.target);
        var creatureId = parseInt(target.attr("data-creature"));
        var responseId = parseInt(target.attr("data-response"));

        $("#stage").empty();
        $("#stage").append('<img src="' + currentQuestion.image + '" class="eye">');
        $("#stage").append('<h3 class="center-text">Now watch ' + currentQuestion.creature + ' react to your answer!</h3><p class="center-text"><strong>Tip:</strong> Look for the eyes that are rapidly blinking.</p>');

        websocket.send(prepareMessage({"type":"respond", "creature_id":creatureId, "response_id":responseId}));
        setTimeout(answerAnother, ANSWER_ANOTHER_DELAY, creatureId, responseId);
    }

    function answerAnother(creatureId, responseId){
        $("#stage").empty();
        $("#stage").append('<h3 class="center-text">The Eyes thank you!</h3>');
        var talkButton = $('<p class="center-text"><a href="#" class="button button-blue">Answer another question</a></p>');
        talkButton.click(getQuestion);
        $("#stage").append(talkButton);
    }

    function onWebsocketMessage(evt) {
        var data = JSON.parse(evt.data);

        if (data.type == "status") {
            if (data.has_brainstem === true) {
                $("#stage").empty();
                $("#stage").append('<h3 class="center-text">The Eyes are asking questions!</h3><p class="center-text">Would you like to talk to them?</p>');
                if (data.geolocation_required === true) {
                    requiresGeo = true;
                    $("#stage").append('<p class="center-text">When you click the button we\'ll ask for you location to make sure you\'re close enough.</p>');
                }

                var talkButton = $('<p class="center-text"><a href="#" class="button button-blue">Talk to the Eyes</a></p>');
                talkButton.click(getQuestion);
                $("#stage").append(talkButton);
            } else {
                showAsleep();
            }
        } else if (data.type == "question") {
            currentQuestion = data;

            clearTimeout(questionTimeout);

            $("#stage").empty();
            $("#stage").append('<img src="' + data.image + '" class="eye">');
            $("#stage").append('<h3 class="center-text">' + data.creature + '</h3>');
            $("#stage").append('<p class="center-text"><strong>' + data.question + '</strong></p>');

            var buttons = $('<p class="center-text"></p>');

            for (var i=0; i<data.responses.length; ++i) {
                var r = data.responses[i];
                var response = $('<a href="#" class="button-3d button-green green-3d response" data-creature="'+data.creature_id+'" data-response="'+r.id+'">' + r.response + '</a></p>');
                response.click(selectResponse);
                buttons.append(response);
            }
            $("#stage").append(buttons);

        } else if (data.type == "not_allowed") {
            $("#stage").empty();
            $("#stage").append('<h3 class="center-text">Sorry.</h3><p class="center-text">You\'re not close enough to the Eyes to talk to them.</p>');

        } else if (data.type == "none_awake") {
            $("#stage").empty();
            $("#stage").append('<h3 class="center-text">Sorry.</h3><p class="center-text">Your creature fell asleep before you responded.</p>');

            var talkButton = $('<p class="center-text"><a href="#" class="button button-blue">Try again</a></p>');
            talkButton.click(getQuestion);
            $("#stage").append(talkButton);
        }
    }

    function requestLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(onLocationSuccess, onLocationError);
        } else{
            $("#stage").empty();
            $("#stage").append('<h3 class="center-text">Sorry.</h3><p class="center-text">Either your device doesn\'t support geolocation or it\'s disabled so we can\'t location you.</p>');
        }
    }

    function onLocationSuccess(location) {
        lat = location.coords.latitude;
        lon = location.coords.longitude;

        if (lastCommand !== null) {
            lastCommand();
            lastCommand = null;
        }

    }

    function onLocationError() {
        $("#stage").empty();
        $("#stage").append('<h3 class="center-text">Sorry.</h3><p class="center-text">We weren\'t able to retrieve your location.</p>');
        $("#stage").append('<p>You may not have location services enabled. See the directions below to enable location services and then reload this page.</p>');
        $("#stage").append('<p><a href="http://support.apple.com/kb/HT6338">Enable location services for Safari on iOS</a></p><p><a href="https://support.google.com/chrome/answer/2710173?hl=en">Enable location services for Chrome on Android</a></p>');
    }

    function prepareMessage(message) {
        if (requiresGeo) {
            message.lat = lat;
            message.lon = lon;
        }

        return JSON.stringify(message);
    }

    function getQuestion() {
        $("#stage").empty();
        if (requiresGeo && (isNaN(lat) || isNaN(lon))) {
            lastCommand = getQuestion;
            requestLocation();
            $("#stage").append('<h3 class="center-text">Just a second.</h3><p class="center-text">We\'re looking up your location.</p>');
        } else{
            questionTimeout = setTimeout(resetConnection, MAX_TIME);
            $("#stage").append('<h3 class="center-text">Please wait.</h3><p class="center-text">The Eyes are deciding who wants to talk to you.</p>');
            var message = {"type": "get_question"};
            websocket.send(prepareMessage(message));
        }
    }

    function resetConnection() {
        clearTimeout(questionTimeout);
        websocket.close();
        showConnecting();
        connect();
    }

    function showUnsupported() {
        $("#stage").empty();
        $("#stage").append('<h3 class="center-text">Sorry.</h3><p class="center-text">Your web browser is not modern enough to support talking to the Eyes.</p>');
        $("#stage").append('<p class="center-text">Your browser needs to support WebSockets and the Geolocation API. Most smartphones produced in the last two years will qualify.</p>');
    }

    function showConnecting() {
        $("#stage").empty();
        $("#stage").append('<h3 class="center-text">Please wait.</h3><p class="center-text">Trying to connect to the Eyes.</p>');
    }

    function showAsleep() {
        $("#stage").empty();
        $("#stage").append('<h3 class="center-text">The Eyes are nocturnal.</h3><p class="center-text">They are awake from dusk until 10pm.</p>');
    }

    function showUnavailable() {
        $("#stage").empty();
        $("#stage").append('<h3 class="center-text">Sorry.</h3><p class="center-text">The Eyes are unavailable right now. Please try again later.</p>');
    }

    function connect() {
        websocket = new WebSocket("ws://theey.es:8080/");
        websocket.onopen = onWebsocketOpen;
        websocket.onclose = onWebsocketClose;
        websocket.onerror = onWebsocketError;
        websocket.onmessage = onWebsocketMessage;
    }


    if (typeof(WebSocket) == "object" || typeof(WebSocket) == "function") {
        showConnecting();
        connect();
    } else {
        showUnsupported();
    }

})(jQuery);
