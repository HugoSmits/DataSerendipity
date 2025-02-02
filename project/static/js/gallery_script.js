function showTab(tabId) {
    document.getElementById('ticker-content').style.display = 'none';
    document.getElementById('stock-data').style.display = 'none';
    document.getElementById('stock-chart').style.display = 'none';

    document.getElementById(tabId).style.display = 'block';
}


document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM Loaded. Fetching data...");
    
    fetchTickers();
    fetchStockData();
    fetchTickersForChart();
});


// ✅ Show tabs dynamically
function showTab(tabId) {
    document.getElementById('ticker-content').style.display = 'none';
    document.getElementById('stock-data').style.display = 'none';
    document.getElementById('stock-chart').style.display = 'none';

    document.getElementById(tabId).style.display = 'block';
}

// ✅ Fetch AEX Tickers from API
function fetchTickers() {
    fetch('/api/tickers')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#ticker-table tbody');
            tableBody.innerHTML = "";

            data.forEach(entry => {
                let row = document.createElement('tr');
                row.innerHTML = `<td>${entry["Ticker Symbol"]}</td><td>${entry["Last Updated"]}</td>`;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('❌ Error fetching tickers:', error));
}

// ✅ Fetch Stock Data Download History
function fetchStockData() {
    fetch('/api/stock_data')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#stock-data-table tbody');
            tableBody.innerHTML = "";

            if (data.error) {
                console.error("❌ API Error:", data.error);
                return;
            }

            data.forEach(entry => {
                let row = document.createElement('tr');
                row.innerHTML = `<td>${entry["Ticker Symbol"]}</td>
                                 <td>${entry["Start Date"]}</td>
                                 <td>${entry["End Date"]}</td>
                                 <td>${entry["Downloaded At"]}</td>`;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('❌ Error fetching stock data:', error));
}

// ✅ Fetch Stocks from Stock Data Table
function fetchTickersForChart() {
    fetch('/api/stocks_from_data')
        .then(response => response.json())
        .then(data => {
            console.log("✅ Fetching stocks from Stock Data:", data);

            const chartSelector = document.getElementById('stock-chart-selector');
            chartSelector.innerHTML = '';

            let defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "-- Select a Stock --";
            chartSelector.appendChild(defaultOption);

            data.forEach(ticker => {
                let option = document.createElement("option");
                option.value = ticker;
                option.textContent = ticker;
                chartSelector.appendChild(option);
            });
        })
        .catch(error => console.error('❌ Error fetching stocks from Stock Data:', error));
}

// ✅ Fetch Stock Chart Data
let stockData = [];

function fetchStockChart(ticker) {
    if (!ticker) return;

    fetch(`/api/stock_data/${ticker}`)
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) {
                console.error("❌ No Data from API");
                document.getElementById("year-selector").innerHTML = "<option value=''>No Data</option>";
                return;
            }

            stockData = data;
            console.log("✅ Stock Data Loaded:", stockData);

            populateYearDropdown();
            updateChart();
        })
        .catch(error => console.error('❌ Error fetching stock data:', error));
}

// ✅ Populate Year Dropdown
function populateYearDropdown() {
    const yearSelector = document.getElementById("year-selector");
    yearSelector.innerHTML = "";

    if (stockData.length === 0) {
        yearSelector.innerHTML = "<option value=''>No Data</option>";
        return;
    }

    const years = [...new Set(stockData.map(entry => entry.Date.split("-")[0]))].sort();

    console.log("📅 Extracted Years:", years);

    let allYearsOption = document.createElement("option");
    allYearsOption.value = "all";
    allYearsOption.textContent = "All Years";
    yearSelector.appendChild(allYearsOption);

    years.forEach(year => {
        let option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        yearSelector.appendChild(option);
    });

    yearSelector.addEventListener("change", updateChart);
}

// ✅ Update Chart Based on Selected Year
function updateChart() {
    if (stockData.length === 0) return;

    const selectedYear = document.getElementById("year-selector").value;
    let filteredData = stockData;

    if (selectedYear !== "all") {
        filteredData = stockData.filter(entry => entry.Date.startsWith(selectedYear));
    }

    if (filteredData.length === 0) {
        console.warn("⚠ No data available for the selected year:", selectedYear);
        return;
    }

    let dates = filteredData.map(entry => entry["Date"]);
    let prices = filteredData.map(entry => parseFloat(entry["Close"]) || 0);
    let volumes = filteredData.map(entry => parseFloat(entry["Volume"]) || 0);

    volumes = volumes.map(v => v / 1e9);

    drawChart(dates, prices, volumes);
}

// ✅ Draw Stock Chart
function drawChart(dates, prices, volumes) {
    const chartCanvas = document.getElementById("stockChart").getContext('2d');

    if (window.stockChartInstance) {
        window.stockChartInstance.destroy();
    }

    window.stockChartInstance = new Chart(chartCanvas, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: "Stock Price",
                    data: prices,
                    borderColor: 'teal',
                    backgroundColor: 'rgba(0, 128, 128, 0.2)',
                    fill: true,
                    yAxisID: "yPrice"
                },
                {
                    label: "Volume (Billions)",
                    data: volumes,
                    borderColor: 'blue',
                    backgroundColor: 'rgba(0, 0, 255, 0.2)',
                    fill: true,
                    type: 'bar',
                    yAxisID: "yVolume"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yPrice: {
                    position: "left",
                    title: { display: true, text: "Price" }
                },
                yVolume: {
                    position: "right",
                    title: { display: true, text: "Volume (Billions)" }
                }
            }
        }
    });
}
