// darkMode.js
// Js solo para realizar el modo de cambio de tema
document.addEventListener("DOMContentLoaded", () => {
  const btnDarkMode = document.getElementById("darkMode");
  const body = document.body;

  // Cargar preferencia guardada
  if (localStorage.getItem("modo") === "dark") {
    body.classList.add("dark");
  }

  btnDarkMode.addEventListener("click", () => {
    body.classList.toggle("dark");

    // Guardar preferencia
    if (body.classList.contains("dark")) {
      localStorage.setItem("modo", "dark");
    } else {
      localStorage.setItem("modo", "light");
    }
  });
});
