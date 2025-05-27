document.addEventListener("DOMContentLoaded", function () {
    const labelsGrossAdd = JSON.parse(document.getElementById("line-chart").dataset.labels);
    const dataGrossAdd = JSON.parse(document.getElementById("line-chart").dataset.data);

    const ctx = document.getElementById("line-chart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labelsGrossAdd,
            datasets: [{
                label: "Gross Adds",
                fill: false,
                backgroundColor: "rgba(0, 156, 255, .3)",
                borderColor: "rgba(0, 156, 255, 1)",
                data: dataGrossAdd
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});


