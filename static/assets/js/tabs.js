/* CUSTOM JS */
$(document).ready(function () {

	/* ####### TABS START ####### */
    $("li[role='tab']").click(function () {
        $("li[role='tab']:not(this)").attr("aria-selected", "false");
        //$("li[role='tab']").attr("tabindex","-1");
        $(this).attr("aria-selected", "true");
        //$(this).attr("tabindex","0");
        var tabpanid = $(this).attr("aria-controls");
        var tabpan = $("#" + tabpanid);
        $("div[role='tabpanel']:not(tabpan)").attr("aria-hidden", "true");
        $("div[role='tabpanel']:not(tabpan)").addClass("hidden");

        tabpan.removeClass("hidden");
//tabpan.className = "panel";
        tabpan.attr("aria-hidden", "false");
    });

    //This adds keyboard accessibility by adding the enter key to the basic click event.
    $("li[role='tab']").keydown(function (ev) {
        if (ev.which == 13) {
            $(this).click();
        }
    });

    //This adds keyboard function that pressing an arrow left or arrow right from the tabs toggel the tabs.
    $("li[role='tab']").keydown(function (ev) {
        if ((ev.which == 39) || (ev.which == 37)) {
            var selected = $(this).attr("aria-selected");
            if (selected == "true") {
                $("li[aria-selected='false']").attr("aria-selected", "true").focus();
                $(this).attr("aria-selected", "false");

                var tabpanid = $("li[aria-selected='true']").attr("aria-controls");
                var tabpan = $("#" + tabpanid);
                $("div[role='tabpanel']:not(tabpan)").attr("aria-hidden", "true");
                $("div[role='tabpanel']:not(tabpan)").addClass("hidden");

                tabpan.attr("aria-hidden", "false");
                tabpan.removeClass("hidden");
//tabpan.className = "panel";
            }
        }
    });
    /* ####### TABS END ####### */

});