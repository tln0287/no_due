$(function () {
  $(".select2").select2({ width: "100%" });

  $(".data-table").DataTable({
    pageLength: 25,
    order: [],
    searching: false,
    lengthChange: false,
    dom: "t<'d-flex justify-content-between align-items-center'ip>",
  });

  function closeSidebar() {
    $(".sidebar").removeClass("show-mobile");
    $(".sidebar-backdrop").removeClass("show");
  }

  $("#sidebarToggle").on("click", function () {
    $(".sidebar").toggleClass("show-mobile");
    $(".sidebar-backdrop").toggleClass("show");
  });
  $(".sidebar-backdrop").on("click", closeSidebar);
  $(".sidebar-nav .nav-link").on("click", closeSidebar);
});
