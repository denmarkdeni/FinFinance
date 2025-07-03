$(function () {
    let chartData;
    try {
      chartData = JSON.parse(document.getElementById('chart-data').textContent);
      console.log("Chart data:", chartData);
    } catch (e) {
      console.error('JSON parse error:', e, document.getElementById('chart-data').textContent);
      return;
    }
  
    // Company Budget by Month (Bar Chart)
    const budgetChartData = chartData.budget_chart_data || { labels: [], data: [] };
    const budgetChart = {
      series: [
        {
          name: "Total Income",
          data: budgetChartData.data
        }
      ],
      chart: {
        fontFamily: "Poppins,sans-serif",
        type: "bar",
        height: 360,
        offsetY: 10,
        toolbar: { show: false },
      },
      grid: {
        show: true,
        strokeDashArray: 3,
        borderColor: "rgba(0,0,0,.1)",
      },
      colors: ["var(--bs-primary)"],
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: "30%",
          endingShape: "flat",
        },
      },
      dataLabels: { enabled: false },
      stroke: {
        show: true,
        width: 5,
        colors: ["transparent"],
      },
      xaxis: {
        type: "category",
        categories: budgetChartData.labels.length ? budgetChartData.labels : ['No Data'],
        axisTicks: { show: false },
        axisBorder: { show: false },
        labels: {
          style: { colors: "#a1aab2" },
        },
      },
      yaxis: {
        title: {
          text: 'Total Income (₹)',
          style: { color: "#a1aab2" },
        },
        labels: {
          style: { colors: "#a1aab2" },
          formatter: function (val) { return "₹" + val.toFixed(0); },
        },
      },
      fill: { opacity: 1, colors: ["var(--bs-primary)"] },
      tooltip: {
        theme: "dark",
        y: { formatter: function (val) { return "₹" + val; } },
      },
      legend: { show: false },
      responsive: [
        {
          breakpoint: 767,
          options: {
            stroke: { show: false, width: 5, colors: ["transparent"] },
          },
        },
      ],
    };
  
    const chart_column_basic = new ApexCharts(document.querySelector("#budget-chart"), budgetChart);
    chart_column_basic.render();
  
    // Transaction Breakdown (Donut Chart)
    const transactionData = chartData.transaction_data || { labels: [], data: [] };
    const transactionChart = {
      series: transactionData.data.length ? transactionData.data : [1],
      labels: transactionData.labels.length ? transactionData.labels : ['No Data'],
      chart: {
        height: 170,
        type: "donut",
        fontFamily: "Plus Jakarta Sans, sans-serif",
        foreColor: "#c6d1e9",
      },
      tooltip: { theme: "dark", fillSeriesColor: false },
      colors: ["var(--bs-primary)", "var(--bs-danger)"],
      dataLabels: { enabled: false },
      legend: { show: false },
      stroke: { show: false },
      responsive: [
        {
          breakpoint: 991,
          options: { chart: { width: 150 } },
        },
      ],
      plotOptions: {
        pie: {
          donut: {
            size: '80%',
            background: "none",
            labels: {
              show: true,
              name: { show: true, fontSize: "12px", color: undefined, offsetY: 5 },
              value: { show: true, color: "#98aab4", formatter: function (val) { return val; } },
            },
          },
        },
      },
    };
  
    const chart = new ApexCharts(document.querySelector("#grade"), transactionChart);
    chart.render();
  
    // Net Amount Trend (Area Chart)
    const netTrendData = chartData.net_trend_data || { labels: [], data: [] };
    const earning = {
      chart: {
        id: "sparkline3",
        type: "area",
        height: 60,
        sparkline: { enabled: true },
        group: "sparklines",
        fontFamily: "Plus Jakarta Sans, sans-serif",
        foreColor: "#adb0bb",
      },
      series: [
        {
          name: "Net Amount",
          color: "#8763da",
          data: netTrendData.data.length ? netTrendData.data : [0],
        },
      ],
      stroke: { curve: "smooth", width: 2 },
      fill: { colors: ["#f3feff"], type: "solid", opacity: 0.05 },
      markers: { size: 0 },
      xaxis: { categories: netTrendData.labels.length ? netTrendData.labels : ['No Data'] },
      tooltip: {
        theme: "dark",
        fixed: { enabled: true, position: "right" },
        x: {
          show: true,
          formatter: function (val, { dataPointIndex }) {
            return netTrendData.labels[dataPointIndex] || 'No Data';
          },
        },
        y: { formatter: function (val) { return "₹" + val; } },
      },
    };
  
    new ApexCharts(document.querySelector("#earning"), earning).render();
  });