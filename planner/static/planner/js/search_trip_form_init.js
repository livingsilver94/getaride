$(function () {
    $(".city-autocomplete").on("autocompleteselect", function (event, ui) {
        show_place_on_map(event.target.id, ui.item.id);
    });
})

// Datepicker init
$(function () {
    var picker = $('#datetimepicker').datetimepicker({
        format: 'DD/MM/YYYY HH:mm',
        inline: true,
        sideBySide: true,
        stepping: 10,
        minDate: moment().valueOf(),
    });
    picker.on("changeDate", function (event) {
        document.getElementById("searchtrip_datetime").value = picker.date;
    });
    picker.show();
});

var marker_state = 0;
var markers = new Array(3);
var api_key = 'pk.eyJ1IjoiYm9uaXMiLCJhIjoiY2o5NWNmNzFsMWZ5ZDMzbXc4cHU2YndrcSJ9.QZy2V8z1VZQyOqwGfab4Rw';

function render_marker(index, marker) {
    if (markers[index] == null) {
        marker_state++;
    } else {
        map.removeLayer(markers[index]);
    }
    markers[index] = marker;
    markers[index].addTo(map);
}

function show_place_on_map(input_id, city_id) {
    $.ajax({
        url: coordinates_url,
        data: {'city_id': city_id},
        dataType: 'json',
        success: function (coords) {
            if (!$.isEmptyObject(coords)) {
                var marker = L.marker([coords.lat, coords.lon], {title: coords.name});
                if (marker_state >= 2) {
                    markers.forEach(function (obj) {
                        map.removeLayer(obj);
                    });
                    marker_state = 0;
                    markers.length = 0;
                }
                if (input_id === "searchtrip_origin_auto") {
                    render_marker(0, marker);
                }
                else {
                    render_marker(1, marker);
                }
                if (marker_state >= 2) {
                    var router = L.Routing.mapbox(api_key);
                    waypoints = [];
                    waypoints.push({latLng: markers[0].getLatLng()});
                    waypoints.push({latLng: markers[1].getLatLng()});
                    router.route(waypoints, function (err, routes) {
                        if (!err) {
                            markers.push(L.Routing.line(routes[0]).addTo(map));
                        }
                    });
                }
            }
        },
    });
}