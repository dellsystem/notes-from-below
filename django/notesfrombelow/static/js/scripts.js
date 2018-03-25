function toggleHamburger() {
    var rightMenus = document.querySelectorAll('.right.menu');
    rightMenus[0].classList.toggle('visible');
    rightMenus[1].classList.toggle('visible');
    return false;
};

$('.ui.dropdown').dropdown();
