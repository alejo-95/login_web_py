fetch('/historico/data')
    .then(response => response.json())
    .then(data => {
        // Gráfico de todas las temperaturas
        let all = document.getElementById('allTemp').getContext('2d');
        let allTemp = new Chart(all, {
            type: 'line',
            data: {
                labels: data.all.labels,
                datasets: [{
                    label: 'Temperatura Promedio',
                    data: data.all.values,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    tooltip: {
                        enabled: true
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        formatter: (value, context) => {
                            return value.toFixed(2); // Formato de los valores
                        }
                    }
                },
                scales: {
                    y: {
                        grid: {
                            display: false, // Desactivar la cuadrícula en el eje x
                        },
                        beginAtZero: true
                    },
                    x: {
                        grid: {
                            display: false, // Desactivar la cuadrícula en el eje x
                        },
                        type: 'time',
                        time: {
                            unit: 'minute',
                            stepSize: 5,
                            tooltipFormat: 'yyyy-MM-dd HH:mm:ss'
                        },
                        title: {
                            display: true,
                            text: 'Fecha y Hora'
                        }
                        //beginAtZero: true
                    }
                }
            },
            plugins: [ChartDataLabels]
        });

        // Gráfico de temperatura máxima
        let max = document.getElementById('maxTemp').getContext('2d');
        let maxTemp = new Chart(max, {
            type: 'bar',
            data: {
                labels: data.max.labels,
                datasets: [{
                    label: 'Temperatura Máxima',
                    data: data.max.values,
                    backgroundColor: 'rgba(225, 51, 51, 0.8)',
                    borderColor: 'rgba(225, 51, 51, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    tooltip: {
                        enabled: true
                    },
                    legend: {
                        display: false
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        formatter: (value, context) => {
                            return value.toFixed(2); // Formato de los valores
                        }
                    }
                },
                scales: {
                    y: {
                        grid: {
                        display: false, // Desactivar la cuadrícula en el eje x
                    },
                        beginAtZero: true
                    },
                    x: {
                        grid: {
                            display: false, // Desactivar la cuadrícula en el eje x
                        },
                        beginAtZero: true
                    },
                }
            },
            plugins: [ChartDataLabels]
        });

        // Gráfico de temperatura mínima
        let min = document.getElementById('minTemp').getContext('2d');
        let minTemp = new Chart(min, {
            type: 'bar',
            data: {
                labels: data.min.labels,
                datasets: [{
                    label: 'Temperatura Mínima',
                    data: data.min.values,
                    backgroundColor: 'rgba(35, 48, 179, 0.8)',
                    borderColor: 'rgba(35, 48, 179, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    tooltip: {
                        enabled: true
                    },
                    legend: {
                        display: false
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        formatter: (value, context) => {
                            return value.toFixed(2); // Formato de los valores
                        }
                    }
                },
                scales: {
                    y: {
                        grid: {
                        display: false, // Desactivar la cuadrícula en el eje x
                    },
                        beginAtZero: true
                    },
                    x: {
                        grid: {
                            display: false, // Desactivar la cuadrícula en el eje x
                        },
                        beginAtZero: true
                    },
                }
            },
            plugins: [ChartDataLabels]
        });
    })
    .catch(error => console.error('Error:', error));
