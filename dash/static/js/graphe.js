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

document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("chart-grossadd-combo");
    const labelsGrossAdd = JSON.parse(canvas.dataset.labels);
    const dataGrossAdd = JSON.parse(canvas.dataset.data);

    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labelsGrossAdd,
            datasets: [{
                label: "Gross Adds par jour",
                backgroundColor: "rgba(0, 156, 255, .3)",
                borderColor: "rgba(0, 156, 255, 1)",
                borderWidth: 1,
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
