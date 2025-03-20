// Función para dispensar comida
document.getElementById('dispense-button').addEventListener('click', function() {
    fetch('http://10.10.0.2/dispense', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                alert('Comida dispensada!');
            } else {
                alert('Error al dispensar comida.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión con el servidor.');
        });
});

// Función para actualizar los horarios de dispensado
function updateDispensingTimes() {
    const morningTime = document.getElementById('morning-time').value;
    const afternoonTime = document.getElementById('afternoon-time').value;
    const eveningTime = document.getElementById('evening-time').value;

    // Aquí se puede agregar la lógica para enviar los horarios al servidor
}

// Agregar eventos para actualizar los horarios
document.getElementById('morning-time').addEventListener('change', updateDispensingTimes);
document.getElementById('afternoon-time').addEventListener('change', updateDispensingTimes);
document.getElementById('evening-time').addEventListener('change', updateDispensingTimes);
