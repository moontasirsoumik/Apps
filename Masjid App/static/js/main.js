$(document).ready(function() {
  // Initialize Select2
  $('#filter_types').select2({
    placeholder: "Select mosque types",
    width: '100%'
  });
  $('#selected_mosque').select2({
    placeholder: "Select a mosque",
    width: '100%',
    allowClear: true
  });

  // Persist left panel state.
  if (localStorage.getItem("leftPanelOpen") === null) {
    localStorage.setItem("leftPanelOpen", "false");
  }
  if (localStorage.getItem("leftPanelOpen") === "true") {
    $('#leftPanel').addClass('open');
  }

  // Auto-submit form on changes
  $('#tile_choice, #latitude, #longitude').on('change', function() {
    $('#mosqueForm').submit();
  });
  $('#filter_types, #selected_mosque').on('change', function() {
    $('#mosqueForm').submit();
  });

  // Submit on pressing Enter in latitude/longitude
  $('#latitude, #longitude').on('keyup', function(e) {
    if (e.keyCode === 13) {
      $('#mosqueForm').submit();
    }
  });

  // Get current location (GPS)
  $('#getLocation').on('click', function() {
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

  // Toggle left panel
  $('#toggleLeftPanel').on('click', function(e) {
    e.stopPropagation();
    $('#leftPanel').toggleClass('open');
    localStorage.setItem("leftPanelOpen", $('#leftPanel').hasClass('open') ? "true" : "false");
  });

  // Close left panel
  $('#closeLeftPanel').on('click', function(e) {
    e.stopPropagation();
    $('#leftPanel').removeClass('open');
    localStorage.setItem("leftPanelOpen", "false");
  });

  // Toggle right panel
  $('#toggleRightPanel').on('click', function(e) {
    e.stopPropagation();
    $('#rightPanel').toggleClass('open');
  });

  // Close right panel
  $('#closeRightPanel').on('click', function(e) {
    e.stopPropagation();
    $('#rightPanel').removeClass('open');
  });

  // --- COLLAPSIBLE SEARCH BAR ---
  // Toggle the search bar (icon changes between search & cross)
  $('#toggleSearchBar').on('click', function() {
    $('#searchBar').toggleClass('open');

    if ($('#searchBar').hasClass('open')) {
      $(this).html('<i class="fas fa-times"></i>');
    } else {
      $(this).html('<i class="fas fa-search"></i>');
    }
  });

  // jQuery UI Autocomplete (real-time suggestions)
  $('#searchInput').autocomplete({
    source: function(request, response) {
      var nominatimUrl = "https://nominatim.openstreetmap.org/search?format=json&limit=5&q=" + encodeURIComponent(request.term);
      $.getJSON(nominatimUrl, function(data) {
        response($.map(data, function(item) {
          // Truncate display_name to ~30 chars
          var displayName = item.display_name;
          if (displayName.length > 30) {
            displayName = displayName.substring(0, 30) + '...';
          }
          return {
            label: displayName,
            value: item.display_name, // full address for hidden value
            lat: item.lat,
            lon: item.lon
          };
        }));
      });
    },
    minLength: 3,
    select: function(event, ui) {
      // Update lat/lon when user picks a suggestion
      $('#latitude').val(ui.item.lat);
      $('#longitude').val(ui.item.lon);

      // Submit form to reload map
      $('#mosqueForm').submit();

      // Collapse search bar & revert icon
      $('#searchBar').removeClass('open');
      $('#toggleSearchBar').html('<i class="fas fa-search"></i>');
    }
  });
});
