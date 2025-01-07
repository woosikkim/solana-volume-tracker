<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solana DEX Volume Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
    </style>
</head>
<body>
    <h1>Solana Total Trading Volume</h1>
    <canvas id="volumeChart"></canvas>
    <script>
        let ctx = document.getElementById('volumeChart').getContext('2d');
        let volumeChart = new Chart(ctx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: '24H Volume (USD)', data: [], borderColor: 'blue', borderWidth: 2 }] },
            options: { responsive: true, scales: { x: { display: true }, y: { display: true } } }
        });

        function updateChart() {
            fetch('/volume')
                .then(response => response.json())
                .then(data => {
                    let now = new Date().toLocaleTimeString();
                    volumeChart.data.labels.push(now);
                    volumeChart.data.datasets[0].data.push(data.volume);
                    if (volumeChart.data.labels.length > 10) {
                        volumeChart.data.labels.shift();
                        volumeChart.data.datasets[0].data.shift();
                    }
                    volumeChart.update();
                });
        }
        setInterval(updateChart, 1000); // Update every 5 minutes
        updateChart();
    </script>
</body>
</html>
