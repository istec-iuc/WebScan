
$(document).ready(function() {

    var alreadyOpen = false;
    var hasBeenReading = false;
    var countdownInterval;

    function resetHasBeenReading(){
        hasBeenReading = false;
        setTimeout( function(){
            hasBeenReading = true;
        }, 10 * 1000);
    }
    resetHasBeenReading();

    function isPurchasing(){
        return $(".gumroad-loading-indicator").is(':visible') || $(".gumroad-overlay-iframe").is(':visible')
    }

    $("body").bind("mouseleave", function(e){
        // console.log("Mouse position is x: " + e.pageX + " y:" + e.pageY);
        if (e.pageY - $(window).scrollTop() <= 20){
            var countdownMinutes = parseInt($("#modal-countdown").attr('data-minutes'));
            var countdownSeconds = parseInt($("#modal-countdown").attr('data-seconds'));
            if (shouldShowModal(countdownMinutes, countdownSeconds)){
                $('#bounce-modal').modal('show');
                alreadyOpen = true;
                startCountdown();
            }
        }
    });

    // hide the modal if they click the buy button on it
    $(".modal .buy-now").click( function(){
        $('#bounce-modal').modal('hide');
        clearInterval(countdownInterval);
        alreadyOpen = false;
    });

    // whenever the modal is hidden, pause the countdown
    $("body").on("hide.bs.modal", function(){
        clearInterval(countdownInterval);
        alreadyOpen = false;
        resetHasBeenReading();
    });

    function shouldShowModal(mins, secs){
        if (
            !isPurchasing() &&              // they have the purchase screen open
            !alreadyOpen &&                 // the modal is already up
            hasBeenReading &&               // give them a few seconds to actually read
            !(mins === 0 && secs === 0)     // is there time left on the clock
        ){
            return true;
        }
        console.log("Not showing modal yet");
        console.log(" - Is Purchasing: " + isPurchasing());
        console.log(" - Already Open: " + alreadyOpen);
        console.log(" - Has Been Reading: " + hasBeenReading);
        return false;
    }

    // setup the countdown
    function startCountdown(){
        countdownInterval = setInterval( function(){
            var $cd = $("#modal-countdown");
            var m = $cd.attr('data-minutes');
            var s = $cd.attr('data-seconds');

            s = s - 1;

            if (s === -1){ // wrap minutes
                m = m - 1;
                s = 59;
            }

            if (m === -1){ // stop countdown
                clearInterval(countdownInterval);
                $('#bounce-modal').modal('hide');
                return;
            }

            if (s < 10){ // zero-pad seconds
                s = "0" + s;
            }

            if (m < 2){  // turn countdown text red
                $cd.css({color: "red"});
            }

            $cd.text(m + ":" + s);
            $cd.attr('data-minutes', m);
            $cd.attr('data-seconds', s);

        }, 1000)
    }

});