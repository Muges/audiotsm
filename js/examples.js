var player = document.getElementById("player");
var source = document.getElementById("playerSource");

function onPlayBtnClicked(e) {
    e.preventDefault();

    source.src = this.getAttribute("href");

    player.parentNode.style.display = "block";
    player.load();
    player.play(); 
}

var buttons = document.getElementsByClassName("play-btn");
for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", onPlayBtnClicked);
}
