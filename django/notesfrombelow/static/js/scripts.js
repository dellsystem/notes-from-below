function toggleHamburger() {
    var rightMenus = document.querySelectorAll('.mobile-hidden');
    rightMenus[0].classList.toggle('visible');
    rightMenus[1].classList.toggle('visible');
    rightMenus[2].classList.toggle('visible');
    return false;
};

function toggleSearch() {
    document.getElementById('search-dropdown').classList.toggle('visible');
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
