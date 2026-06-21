// MultiTaller - JavaScript principal

// Toggle del sidebar
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const wrapper = document.getElementById('wrapper');
    
    if (menuToggle && wrapper) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.toggle('toggled');
        });
    }
    
    // Confirmación para acciones destructivas
    const deleteLinks = document.querySelectorAll('a[href*="eliminar"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Validación de formularios
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Búsqueda en tiempo real con debounce
    const searchInputs = document.querySelectorAll('input[data-search-target]');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('keyup', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                const target = input.getAttribute('data-search-target');
                const value = input.value;
                
                // Filtrar filas de la tabla
                const rows = document.querySelectorAll(target + ' tbody tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(value.toLowerCase()) ? '' : 'none';
                });
            }, 300);
        });
    });
    
    // Selección de todos los checkboxes
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.item-checkbox');
            checkboxes.forEach(function(cb) {
                cb.checked = selectAllCheckbox.checked;
            });
        });
    }
    
    // Confirmación de contraseñas
    const passwordConfirm = document.getElementById('password_confirm');
    const passwordInput = document.getElementById('password');
    
    if (passwordConfirm && passwordInput) {
        passwordConfirm.addEventListener('input', function() {
            if (passwordInput.value !== passwordConfirm.value) {
                passwordConfirm.setCustomValidity('Las contraseñas no coinciden');
            } else {
                passwordConfirm.setCustomValidity('');
            }
        });
    }
    
    // Formateo de moneda en inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][data-currency]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            const value = parseFloat(input.value);
            if (!isNaN(value)) {
                input.value = value.toFixed(2);
            }
        });
    });
    
    // Cálculo automático de totales
    const cantidadInputs = document.querySelectorAll('input[name*="cantidad"]');
    const precioInputs = document.querySelectorAll('input[name*="precio"]');
    
    [cantidadInputs, precioInputs].forEach(function(inputs) {
        inputs.forEach(function(input) {
            input.addEventListener('change', calculateTotals);
        });
    });
});

// Función para calcular totales en formularios de orden
function calculateTotals() {
    const cantidades = document.querySelectorAll('input[name*="cantidad"]');
    const precios = document.querySelectorAll('input[name*="precio"]');
    let total = 0;
    
    cantidades.forEach(function(cantidad, index) {
        const qty = parseFloat(cantidad.value) || 0;
        const price = parseFloat(precios[index]?.value) || 0;
        total += qty * price;
    });
    
    const totalDisplay = document.getElementById('total-calculado');
    if (totalDisplay) {
        totalDisplay.textContent = total.toFixed(2);
    }
}

// Función para imprimir órdenes/recibos
function imprimirOrden(ordenId) {
    window.open('/orden/' + ordenId + '/imprimir', '_blank');
}

// Exportar tabla a CSV
function exportTableToCSV(tableSelector, filename) {
    const table = document.querySelector(tableSelector);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });
    
    downloadCSV(csv.join('\n'), filename);
}

// Descargar archivo CSV
function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Mostrar/ocultar contraseña
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = 'Ocultar';
    } else {
        input.type = 'password';
        button.textContent = 'Mostrar';
    }
}
