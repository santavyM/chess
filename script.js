function toggleMenu() {
    document.querySelector(".mobile-menu").classList.toggle("show");
}


// SEZNAM SVÁTKŮ
const svatky = {
    "1-2": "Hynek",
    "2-2": "Nela",
    "3-2": "Blažej",
    "4-2": "Jarmila",
    "5-2": "Dobromila",
    "6-2": "Vanda",
    "7-2": "Veronika",
    "8-2": "Milada",
    "9-2": "Apolena",
    "10-2": "Mojmír",
    "11-2": "Božena",
    "12-2": "Slavěna, Slávka",
    "13-2": "Věnceslav, Věnceslava",
    "14-2": "Valentýn, Valentýna",
    "15-2": "Jiřina",
    "16-2": "Ljuba",
    "17-2": "Miloslava",
    "18-2": "Gizela",
    "19-2": "Patrik",
    "20-2": "Oldřich",
    "21-2": "Eleonora, Lenka",
    "22-2": "Petr",
    "23-2": "Svatopluk",
    "24-2": "Matyáš, Matěj",
    "25-2": "Liliana",
    "26-2": "Dorota",
    "27-2": "Alexandr",
    "28-2": "Lumír"
};

// GENEROVÁNÍ TEČEK NA CIFERNÍKU
function generateDial() {
    const dial = document.querySelector(".dial");
    
    for (let i = 0; i < 60; i++) {
        let mark = document.createElement("span");
        mark.style.transform = `rotate(${i * 6}deg) translateY(-55px)`;
        
        // Každá pátá značka je bílá (hodinová)
        if (i % 5 === 0) {
            mark.style.height = "4px";
            mark.style.width = "2px";
            mark.style.background = "#DFDDD2";
        } else {
            mark.style.height = "2px";
            mark.style.background = "dimgray";
        }
        
        dial.appendChild(mark);
    }
}

// AKTUALIZACE ČASU A DATUMU
function updateClock() {
    const now = new Date();
    
    // Čas
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    
    // Nastavení ručiček
    document.querySelector(".hour-hand").style.transform = `translateX(-50%) rotate(${hours * 30 + minutes * 0.5}deg)`;
    document.querySelector(".minute-hand").style.transform = `translateX(-50%) rotate(${minutes * 6}deg)`;
    document.querySelector(".second-hand").style.transform = `translateX(-50%) rotate(${seconds * 6}deg)`;

    // Formátovaný čas
    document.querySelector(".time").textContent = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
    
    // Datum a svátek
    const den = now.getDate();
    const mesic = now.getMonth() + 1;
    const rok = now.getFullYear();
    let denVTydnu = now.toLocaleDateString("cs-CZ", { weekday: "long" });

    // První písmeno velké
    denVTydnu = denVTydnu.charAt(0).toUpperCase() + denVTydnu.slice(1);

    document.querySelector(".date").innerHTML = `${denVTydnu}<br>${den}. ${mesic}. ${rok}`;
    
    // Zobrazení svátku
    const svatekDnes = svatky[`${den}-${mesic}`] || "Neznámý";
    document.querySelector(".nameday").textContent = svatekDnes;
}

// Spuštění aktualizace
generateDial();
setInterval(updateClock, 1000);
updateClock();

