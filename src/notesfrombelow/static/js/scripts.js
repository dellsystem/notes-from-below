function toggleHamburger() {
    var rightMenus = document.querySelectorAll('.menu.mobile-hidden');
    rightMenus[0].classList.toggle('visible');
    rightMenus[1].classList.toggle('visible');
    rightMenus[2].classList.toggle('visible');
    return false;
};

// hide the large logo + show the small logo when scrolling down
$(window).scroll(function () {
    // DO NOT activate this on mobile
    if ($(window).width() < 1200) {
        return;
    }

    var scrollTop = $(window).scrollTop();
    if (scrollTop > 0) {
        if ($('#nfb-mini-logo').is(":hidden")) {
            // large image fades out; small one appears right away
            $('#nfb-mini-logo').show();
            $('#nfb-large-logo').hide(400);
        }
    } else {
        if ($('#nfb-large-logo').is(":hidden")) {
            // large image fades in; small one disappears right away
            $('#nfb-mini-logo').hide();
            $('#nfb-large-logo').show(400);
        }
    }
})

function toggleSearch() {
    // TODO: use jquery for everything lol
    document.getElementById('search-dropdown').classList.toggle('visible');
    $('#search-input').focus();
    return false;
};

$('.ui.dropdown').dropdown();

$('.footnote-backref,.footnote-ref').click(function(e) {
    e.preventDefault();
    // There is a colon in the ID so can't just put into $() directly
    var dest = document.getElementById($(this).attr('href').substring(1));
    // Only add the "highlighted" class for the actual footnote text.
    if (dest.tagName == 'LI') {
        $(dest).addClass('highlighted');
        setTimeout(function () {
            $(dest).removeClass('highlighted');
        }, 3000)
    }
    var offset = $(dest).offset().top;
    console.log(offset);
    $('html').animate({ scrollTop: offset}, 'slow');
});
