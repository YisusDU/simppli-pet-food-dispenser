const esp32Ip = '10.10.0.2';  // Reemplaza con la dirección IP del ESP32

document.addEventListener('DOMContentLoaded', () => {
    // Cargar horarios al iniciar
    loadSchedules();

    // Dispensar comida
    document.getElementById('dispense-button').addEventListener('click', async () => {
        try {
            const response = await fetch(`http://${esp32Ip}/dispense`, { method: 'POST' });
            if (response.ok) {
                alert('Comida dispensada!');
            } else {
                alert('Error al dispensar comida.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de conexión con el servidor.');
        }
    });

    // Actualizar horarios
    document.getElementById('schedule-form').addEventListener('submit', async (event) => {
        event.preventDefault(); // Evitar que el formulario se envíe

        const morningTime = document.getElementById('morning-time').value;
        const afternoonTime = document.getElementById('afternoon-time').value;
        const eveningTime = document.getElementById('evening-time').value;

        if (!morningTime || !afternoonTime || !eveningTime) {
            alert('Por favor, completa todos los campos de tiempo.');
            return;
        }

        try {
            const response = await fetch(`http://${esp32Ip}/update_times`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ morning: morningTime, afternoon: afternoonTime, evening: eveningTime }),
            });
            if (response.ok) {
                alert('Horarios actualizados!');
            } else {
                alert('Error al actualizar horarios.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error de conexión con el servidor.');
        }
    });
});

// Cargar horarios
async function loadSchedules() {
    try {
        const response = await fetch(`http://${esp32Ip}/get_times`);
        if (response.ok) {
            const times = await response.json();
            document.getElementById('morning-time').value = times.morning;
            document.getElementById('afternoon-time').value = times.afternoon;
            document.getElementById('evening-time').value = times.evening;
        } else {
            console.error('Error al cargar los horarios.');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}