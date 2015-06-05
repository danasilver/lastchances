(function ($) {
  var entriesEl = $("#entries-form");
  $("#another").on("click", function () {
    entriesEl.append(
      '<div class="row">' +
        '<p class="col-sm-4 col-sm-offset-4">' +
          '<input class="form-control" name="entry" placeholder="Philip J. Hanlon">' +
        '</p>' +
      '</div>');
  });

  $(".suggestion").on("click", function () {
    var $this = $(this);
    $("#entry-" + $this.data("entry")).val($this.text());
  });

  $("#submit").on("click", function (e) {
    entriesEl.submit();
  });
})($);