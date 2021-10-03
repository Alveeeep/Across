/* Open the sidenav */
var opened = false;
function openNav() {
    if (opened == false){
        document.getElementById("Sidenav").style.width = "100%";
        opened = true;}
    else{
        document.getElementById("Sidenav").style.width = "0";
        opened = false;}
}
