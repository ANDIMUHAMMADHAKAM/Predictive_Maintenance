// Menampilkan nilai slider dalam format angka pada elemen <span>
document.getElementById('age').addEventListener('input', function(event) { 
    document.getElementById('displayAge').innerText = event.target.value;
});


function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    document.getElementById("contentArea").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
    document.getElementById("contentArea").style.marginLeft = "0";
}

function toggleNav() {
    const sidenav = document.getElementById("mySidenav");
    const navToggle = document.getElementById("nav-toggle");

    if (sidenav.style.width === "250px") {
        // Jika navigasi terbuka, panggil fungsi closeNav dan ubah tombol ke "open"
        closeNav();
        navToggle.innerHTML = "&#9776;";
    } else {
        // Jika navigasi tertutup, panggil fungsi openNav dan ubah tombol ke "close"
        openNav();
        navToggle.innerHTML = "&times; close";
    }
}
