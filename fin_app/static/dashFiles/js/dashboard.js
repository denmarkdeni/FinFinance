
$(function () {

  // =====================================
  // Users & Budget (Bar Chart)
  // =====================================
  let chartData;
  try {
    chartData = JSON.parse(document.getElementById('chart-data').textContent);
    console.log("Chart data:", chartData);
  } catch (e) {
    console.error('JSON parse error:', e, document.getElementById('chart-data').textContent);
    return;
  }
  console.log("Script running");

  const budgetChartData = chartData.budget_chart_data || { labels: [], data: [] };
  const profit = {
    series: [
      {
        name: "Total Budgeted",
        data: budgetChartData.data
      }
    ],
    chart: {
      fontFamily: "Poppins,sans-serif",
      type: "bar",
      height: 360,
      offsetY: 10,
      toolbar: {
        show: false,
      },
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
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      width: 5,
      colors: ["transparent"],
    },
    xaxis: {
      type: "category",
      categories: budgetChartData.labels.length ? budgetChartData.labels : ['No Data'],
      axisTicks: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
      labels: {
        style: {
          colors: "#a1aab2",
        },
      },
    },
    yaxis: {
      title: {
        text: 'Total Budgeted (₹)',
        style: {
          color: "#a1aab2",
        },
      },
      labels: {
        style: {
          colors: "#a1aab2",
        },
        formatter: function (val) {
          return "₹" + val.toFixed(0);
        },
      },
    },
    fill: {
      opacity: 1,
      colors: ["var(--bs-primary)"],
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: function (val) {
          return "₹" + val;
        },
      },
    },
    legend: {
      show: false,
    },
    responsive: [
      {
        breakpoint: 767,
        options: {
          stroke: {
            show: false,
            width: 5,
            colors: ["transparent"],
          },
        },
      },
    ],
  };

  const chart_column_basic = new ApexCharts(
    document.querySelector("#budget-chart"),
    profit
  );
  chart_column_basic.render();

  // =====================================
  // Total Users (Donut Chart)
  // =====================================
  const userRoleData = chartData.user_role_data || { labels: [], data: [] };
  const grade = {
    series: userRoleData.data.length ? userRoleData.data : [1],
    labels: userRoleData.labels.length ? userRoleData.labels : ['No Data'],
    chart: {
      height: 170,
      type: "donut",
      fontFamily: "Plus Jakarta Sans, sans-serif",
      foreColor: "#c6d1e9",
    },
    tooltip: {
      theme: "dark",
      fillSeriesColor: false,
    },
    colors: [ "var(--bs-primary)","var(--bs-danger)", "var(--bs-success)"],
    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    stroke: {
      show: false,
    },
    responsive: [
      {
        breakpoint: 991,
        options: {
          chart: {
            width: 150,
          },
        },
      },
    ],
    plotOptions: {
      pie: {
        donut: {
          size: '80%',
          background: "none",
          labels: {
            show: true,
            name: {
              show: true,
              fontSize: "12px",
              color: undefined,
              offsetY: 5,
            },
            value: {
              show: true,
              color: "#98aab4",
              formatter: function (val) {
                return val;
              },
            },
          },
        },
      },
    },
  };

  const chart = new ApexCharts(document.querySelector("#grade"), grade);
  chart.render();

  // =====================================
  // Total Budgets (Area Chart)
  // =====================================
  const budgetTrendData = chartData.budget_trend_data || { labels: [], data: [] };
  const earning = {
    chart: {
      id: "sparkline3",
      type: "area",
      height: 60,
      sparkline: {
        enabled: true,
      },
      group: "sparklines",
      fontFamily: "Plus Jakarta Sans, sans-serif",
      foreColor: "#adb0bb",
    },
    series: [
      {
        name: "Total Budgeted",
        color: "#8763da",
        data: budgetTrendData.data.length ? budgetTrendData.data : [0],
      },
    ],
    stroke: {
      curve: "smooth",
      width: 2,
    },
    fill: {
      colors: ["#f3feff"],
      type: "solid",
      opacity: 0.05,
    },
    markers: {
      size: 0,
    },
    xaxis: {
      categories: budgetTrendData.labels.length ? budgetTrendData.labels : ['No Data'],
    },
    tooltip: {
      theme: "dark",
      fixed: {
        enabled: true,
        position: "right",
      },
      x: {
        show: true,
        formatter: function (val, { dataPointIndex }) {
          return budgetTrendData.labels[dataPointIndex] || 'No Data';
        },
      },
      y: {
        formatter: function (val) {
          return "₹" + val;
        },
      },
    },
  };

  new ApexCharts(document.querySelector("#earning"), earning).render();


});