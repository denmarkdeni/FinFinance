$(function () {
  // Transaction Summary Chart
  const transactionDataElement = document.getElementById('transaction-data');
  if (transactionDataElement) {
    let transactionData;
    try {
      transactionData = JSON.parse(transactionDataElement.textContent);
      console.log("Transaction data:", transactionData);
    } catch (e) {
      console.error('Transaction JSON parse error:', e, transactionDataElement.textContent);
      return;
    }

    const transactionChart = {
      series: [{
        name: "Amount (₹)",
        data: transactionData.data
      }],
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
      colors: transactionData.data.map((_, index) => 
        transactionData.labels[index] === 'Income' ? "var(--bs-primary)" : "var(--bs-danger)"
      ),
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
        categories: transactionData.labels,
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

    const transaction_chart = new ApexCharts(document.querySelector("#transaction-chart"), transactionChart);
    
    transaction_chart.render();
    console.log(transactionChart);
    
  } else {
    console.error("Transaction data element not found.");
  }
});