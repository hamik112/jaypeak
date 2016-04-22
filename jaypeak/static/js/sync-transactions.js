function getSyncTransactionsStatus(url){
    $.getJSON(url, function(data) {
        if (data['state'] == 'SUCCESS') {
            $("#sync-transactions-incomplete").addClass("hidden");
            $("#sync-transactions-complete").removeClass("hidden");
            $("#next-button").removeClass("hidden");
        } else {
            setTimeout(function(){
                getSyncTransactionsStatus(url);
            }, 2000);
        }
    });
}

$(document).ready(function() {
    getSyncTransactionsStatus(SYNC_TRANSACTIONS_STATUS_URL);
});

