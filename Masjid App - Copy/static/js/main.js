$(document).ready(function(){
    $('#filter_types').select2({
        placeholder: "Select mosque types",
        width: '100%'
    });
    $('#selected_mosque').select2({
        placeholder: "Select a mosque",
        width: '100%',
        allowClear: true
    });

    $('#tile_choice, #latitude, #longitude').on('change', function(){
        $('#mosqueForm').submit();
    });
    $('#filter_types, #selected_mosque').on('change', function(){
        $('#mosqueForm').submit();
    });
    
    $('#latitude, #longitude').on('keyup', function(e){
        if(e.keyCode === 13){
            $('#mosqueForm').submit();
        }
    });

    $('#getLocation').on('click', function(){
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                $('#latitude').val(position.coords.latitude);
                $('#longitude').val(position.coords.longitude);
                $('#mosqueForm').submit();
            }, function(error) {
                alert("Error getting location: " + error.message);
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    });
});
