$(function () {
    const chartDataElement = document.getElementById('chart-data');
    if (chartDataElement) {
      let chartData;
      try {
        chartData = JSON.parse(chartDataElement.textContent);
        // console.log("Budget chart data:", chartData);
      } catch (e) {
        console.error('Chart JSON parse error:', e, chartDataElement.textContent);
        return;
      }
  
      const budgetChart = {
        series: [
          {
            name: "Total Budgeted / Income",
            data: chartData.budgeted || chartData.income
          },
          {
            name: "Total Expenses",
            data: chartData.expenses
          }
        ],
        chart: {
          fontFamily: "Poppins, sans-serif",
          type: "bar",
          height: 300,
          toolbar: { show: false },
        },
        grid: {
          show: true,
          strokeDashArray: 3,
          borderColor: "rgba(0,0,0,.1)",
        },
        colors: ["var(--bs-primary)", "var(--bs-danger)"],
        plotOptions: {
          bar: { 
            horizontal: false, 
            columnWidth: "30%", 
            endingShape: "flat" 
          },
        },
        dataLabels: { enabled: false },
        stroke: { 
          show: true, 
          width: 5, 
          colors: ["transparent"] 
        },
        xaxis: {
          categories: chartData.labels,
          axisTicks: { show: false },
          axisBorder: { show: false },
          labels: { 
            style: { colors: "#a1aab2" },
            rotate: -45,
            rotateAlways: true
          },
        },
        yaxis: {
          title: { 
            text: 'Amount (₹)', 
            style: { color: "#a1aab2" } 
          },
          labels: {
            style: { colors: "#a1aab2" },
            formatter: function (val) { return "₹" + val.toFixed(0); }
          },
        },
        fill: { opacity: 1 },
        tooltip: {
          theme: "dark",
          y: { 
            formatter: function (val) { return "₹" + val.toFixed(2); } 
          },
        },
        responsive: [
          {
            breakpoint: 767,
            options: { 
              chart: { height: 250 },
              plotOptions: { bar: { columnWidth: "50%" } }
            }
          }
        ]
      };
  
      const budget_chart = new ApexCharts(document.querySelector("#budget-chart"), budgetChart);
      budget_chart.render();
    } else {
      console.error("Chart data element not found.");
    }
  });