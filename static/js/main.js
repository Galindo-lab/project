function obtenerUbicacion() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (posicion) => {
                const latitud = posicion.coords.latitude.toString(); // Convertir a string
                const longitud = posicion.coords.longitude.toString(); // Convertir a string

                // Enviar la ubicación al servidor
                fetch('/recibir-ubicacion/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'), // Asegúrate de manejar CSRF
                    },
                    body: JSON.stringify({ latitud, longitud }),
                })
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
            },
            (error) => {
                console.error('Error al obtener la ubicación:', error);
            }
        );
    } else {
        console.error('Geolocalización no soportada');
    }
}

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Obtener la ubicación cada 10 segundos
setInterval(obtenerUbicacion, 3000);