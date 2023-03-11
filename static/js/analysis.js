var script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
document.head.appendChild(script);

function get_cat_data(){
    
    var start_date = new Date(document.getElementById('start-date').value).toISOString();
    var end_date = new Date(document.getElementById('end-date').value).toISOString(); 
 
    $.ajax({
        url: "./category_sale",
        type: "GET",
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
        success: function(response) {
            console.log(Object.keys(response));
            console.log(Object.values(response));
            category_chart(Object.keys(response),Object.values(response))
        },
        error: function(xhr, status, error) {
            console.log(error);
        }
    });

    function category_chart(payments,counts){
        const canvas = document.getElementById('category-chart');
        if (canvas.chart) {
        canvas.chart.destroy();
        }
        // Create the chart using Chart.js
        var ctx = canvas.getContext('2d');
        var chart = new Chart(ctx, {
          type: 'doughnut',
          data : {
            labels: payments,
            datasets: [{
              data: counts,
              // backgroundColor: ['#ff6384', '#36a2eb'],
              hoverOffset: 4
            }]
            
          },
          
        });
        canvas.chart = chart;
      }

}