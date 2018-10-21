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
