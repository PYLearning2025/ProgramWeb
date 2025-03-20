$(document).ready(function() {
    $("#sidebarToggle").click(function() {
        $("#sidebar").toggleClass("active");
        $("#sidebarToggle").toggleClass("active");
    });
});