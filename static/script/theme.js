
// IMPORTANTE: coloca esto en el <HEAD> antes de cualquier otra etiqueta.
const setTheme = (theme) => {
    theme = theme || localStorage.getItem('appTheme') || "light"; // Asegura la asignación correcta
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('appTheme', theme); // Guarda el tema en localStorage correctamente
};

const toggleTheme = () => {
    const currentTheme = localStorage.getItem('appTheme') || "light";
    const newTheme = currentTheme === "light" ? "dark" : "light";
    setTheme(newTheme);
};

const getCurrentTheme = () => {
    return localStorage.getItem('appTheme') || "light";
};

setTheme(); // Inicializa el tema al cargar la página

window.onpageshow = function (event) {
    if (event.persisted) { // Para manejar la recarga desde el caché
        setTheme();
    }
};