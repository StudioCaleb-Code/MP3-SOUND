/* analyzer.js - Versión Blindada */

// --- 1. MANEJO DE INTERFAZ ---

function toggleMenu(element) {
    // Evita que el evento se propague al window.onclick
    event.stopPropagation();
    
    const isActive = element.classList.contains('active');
    
    // Cerramos cualquier otro menú abierto
    document.querySelectorAll('.group').forEach(g => g.classList.remove('active'));
    
    // Si no estaba activo, lo abrimos
    if (!isActive) {
        element.classList.add('active');
    }
}

function selectOption(campo, valor, texto) {
    const hiddenTipo = document.getElementById('hiddenTipo');
    const hiddenCalidad = document.getElementById('hiddenCalidad');
    const labelTipo = document.getElementById('selectedTipoText');
    const labelCalidad = document.getElementById('selectedCalidadText');

    if (campo === 'tipo') {
        hiddenTipo.value = valor;
        labelTipo.innerText = texto;
        
        const calidadesAudio = document.querySelectorAll('.opcion-audio');
        const calidadesVideo = document.querySelectorAll('.opcion-video');

        if (valor === 'audio') {
            calidadesAudio.forEach(el => el.style.display = 'block');
            calidadesVideo.forEach(el => el.style.display = 'none');
            // Por defecto para audio
            labelCalidad.innerText = "320 kbps";
            hiddenCalidad.value = "320";
        } else {
            calidadesAudio.forEach(el => el.style.display = 'none');
            calidadesVideo.forEach(el => el.style.display = 'block');
            
            // Forzar selección de la mejor calidad de video disponible
            const primeraOpcionVideo = document.querySelector('.opcion-video');
            if (primeraOpcionVideo) {
                // Extraemos el número de calidad del atributo onclick o texto
                const resMatch = primeraOpcionVideo.innerText.match(/\d+/);
                const res = resMatch ? resMatch[0] : "720";
                labelCalidad.innerText = res + "p";
                hiddenCalidad.value = res;
            }
        }
    } else if (campo === 'calidad') {
        // Limpiamos el valor para que sea solo número (ej: "720p" -> "720")
        const soloNumero = valor.toString().replace(/\D/g, '');
        hiddenCalidad.value = soloNumero;
        labelCalidad.innerText = texto;
    }
    
    // Cerrar todos los menús
    document.querySelectorAll('.group').forEach(g => g.classList.remove('active'));
}

// CERRAR AL TOCAR CUALQUIER PARTE FUERA
window.onclick = function(event) {
    if (!event.target.closest('.group')) {
        document.querySelectorAll('.group').forEach(g => g.classList.remove('active'));
    }
}

// --- 2. ANALIZAR LINK ---

async function analizarLink() {
    const urlInput = document.getElementById('url-input');
    const resDiv = document.getElementById('resultado-analisis');

    if (!urlInput.value) {
        alert("Pega un link de YouTube.");
        return;
    }

    resDiv.innerHTML = `
        <div class="loader-container">
            <div class="spinner-blue"></div>
            <p>Analizando video...</p>
        </div>`;

    try {
        const response = await fetch('/analizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput.value })
        });

        if (response.ok) {
            resDiv.innerHTML = await response.text();

            // Sincronizar estado inicial (Audio por defecto)
            const calidadesVideo = document.querySelectorAll('.opcion-video');
            calidadesVideo.forEach(el => el.style.display = 'none');

            // Iframe de Preview
            const videoId = extraerID(urlInput.value);
            const contenedorImg = document.querySelector('.icono-img');
            if (videoId && contenedorImg) {
                contenedorImg.innerHTML = `
                    <iframe width="100%" height="220" 
                        src="https://www.youtube.com/embed/${videoId}" 
                        frameborder="0" allowfullscreen 
                        style="border-radius: 15px; border: 2px solid #00b3ff;">
                    </iframe>`;
            }

            // Gestionar Formulario de Descarga
            const form = document.getElementById('downloadForm');
            if (form) {
                form.onsubmit = function() {
                    const btn = form.querySelector('button');
                    const span = btn.querySelector('span');
                    
                    btn.disabled = true;
                    btn.style.background = "#28a745"; // Color éxito temporal
                    span.innerHTML = 'DESCARGANDO...';
                    
                    // Restaurar tras 15 seg
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.style.background = ""; 
                        span.innerText = "DESCARGAR";
                    }, 15000);
                };
            }
        }
    } catch (err) {
        resDiv.innerHTML = `<p style="color:red;">Error de conexión.</p>`;
    }
}

function extraerID(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|shorts\/)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length == 11) ? match[2] : null;
}