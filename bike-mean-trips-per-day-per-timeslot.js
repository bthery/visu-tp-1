// Mastère Big Data : Visualisation des données TP1
//
// Cécile Boukamel-Donnou / Benjamin Thery
//
//     Los Angeles Metro Share Bike Trips data
//
// With help from:
// - Tooltips: http://bl.ocks.org/d3noob/a22c42db65eb00d4e369

var debug = false;
var weekendBar = false;
var chartData = [];

const WEEKDAY_IDX = 1;
const WEEKEND_IDX = 2;

// Chargement du fichier .csv contenant les données
// Attention: operation asynchrone! Le reste du code doit être dans la routine callback.
d3.csv("data/bike-mean-trips-per-day-per-timeslot.csv", chartDataReady);

// Fonction appelée quand le .csv a été lu
function chartDataReady(error, csv) {

    console.log("Finished reading csv");

    if (error) throw error;

    csv.forEach(function(x) {
        chartData.push([x.time_slot_label,
                  parseFloat(x.mean_weekday_trips),
                  parseFloat(x.mean_weekend_trips)]);
        if (debug) {
            console.log(x.time_slot_label);
            console.log(x.mean_weekend_trips);
            console.log(chartData);
        }
    });

    drawChart(weekendBar ? WEEKEND_IDX : WEEKDAY_IDX);
}

// Fonction dessinant le graphe en barre
function drawChart(dataIndex) {

    var maxBarHeight = 400;
    var barWidth = 16;
    var timeLabelHeight = 40;
    var chartHeight = maxBarHeight + timeLabelHeight;
    var chartWidth = barWidth * chartData.length;
    var maxYValue = Math.ceil(d3.max(chartData, function(x) { return x[dataIndex]; }) / 5) *5;

    if (debug) {
        console.log("Max value: " + maxYValue);
        console.log(`Chart Width: ${chartWidth} chartHeight: ${chartHeight}`);
    }

    // Ajout d'un div pour le tooltip
    var tooltipBar = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    // Calcul l'echelle en fonction de la donnée la plus grande
    var scaleY = d3.scale.linear()
        .domain([0, maxYValue])
        .range([maxBarHeight, 0]);

    // Definir les axes
    var yAxis = d3.svg.axis().scale(scaleY)
        .orient("right").ticks(5)
        .tickSize(chartWidth);

    // Creer le graphique
    var chart = d3.select("#svgchart")
        .attr("width", chartWidth)
		.attr("height", chartHeight);

    // Add background image
    chart.append("defs")
        .append("pattern")
            .attr("id", "bgimage")
            .attr('patternUnits', 'userSpaceOnUse')
            .attr('width', chartWidth )
            .attr('height', chartHeight)
        .append("image")
            .attr("xlink:href", "images/los-angeles-metro-bike-blurred.jpg")
            .attr('width', chartWidth )
            .attr('height', chartHeight);
    chart.append("rect")
        .attr("width", chartWidth)
		.attr("height", chartHeight)
        //.attr("fill", "red");
        .attr("fill", "url(#bgimage)");

    // Ajoute autant d'élément g que de lignes de données
    // et positione les éléments
    var oneBar = chart.selectAll("g")
        .data(chartData)
		.enter().append("g")
		.attr("transform", function(d, i) { return "translate(" + i * barWidth + ", 0)"; });

    // Pour chaque element g: ajoute un element rectangle avec une hauteur fixe
    // et une largeur correspondant a la valeur de l'entree mise a l'echelle
    oneBar.append("rect")
        .attr("y", function(d) { return scaleY(d[dataIndex]); } )
        .attr("width", barWidth - 1)
        .attr("height", function(d) { return chartHeight - timeLabelHeight - scaleY(d[dataIndex]); })
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("fill", "#a0d53f")
        .attr("fill-opacity","0.9")
        .on("mouseover", function(d, i) {
            d3.select(this)
            	.attr("fill", "#ccfb76");
            tooltipBar.transition()
                .duration(200)
                .style("opacity", .7);
            tooltipBar.html(chartData[i][0] + "-" + chartData[(i+1) % chartData.length][0] + "<br/><b>"  + d[dataIndex] + " trips</b>")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
        .on("mouseout", function(d) {
            d3.select(this)
            	.attr("fill", "#a0d53f");
            tooltipBar.transition()
                .duration(500)
                .style("opacity", 0);
        });

    // Pour chaque element g: ajoute un element texte avec la valeur de la donnee
    /*
    oneBar.append("text")
        .attr("x", barWidth / 2)
        .attr("y", function(d) { return scaleY(d[dataIndex]) - 2; })
        .attr("dy", ".35em")
        .attr("transform", function(d) { return "rotate(-75, " + (barWidth / 2) + "," + (scaleY(d[dataIndex]) - 2) + ")";})
        .text(function(d) { return "" + d[dataIndex]; });
    */

    // Pour chaque element g: ajoute le label
    oneBar.append("text")
        .attr("x", barWidth / 2)
        .attr("y", chartHeight-4)
        .attr("dy", ".35em")
        .attr("text-anchor", "begin")
        .attr("transform", function() { return "rotate(-90, " + (barWidth / 2) +"," + (chartHeight-4) + ")";})
        .text(function(d) { return "" + d[0]; });

    // Ajoute l'axe des ordonnées
    chart.append("g")
        .attr("class", "y axis")
        .call(customYAxis);

    function customYAxis(g) {
        g.call(yAxis);
        g.select(".domain").remove();
        g.selectAll(".tick:not(:first-of-type) line").attr("stroke", "#777").attr("stroke-dasharray", "2,2");
        g.selectAll(".tick text").attr("x", 4).attr("dy", -4);
    }

    console.log("Chart drawn !");
}

//
// Appelé quand les boutons semaine/weekend sont cliqués
//

$('#weekday_button_bar').click(function() {
    $(this).siblings().removeClass('active');
    console.log("Weekday!");
    if (weekendBar) {
        weekendBar = false;
        d3.select("#svgchart").selectAll("*").remove();
        drawChart(WEEKDAY_IDX);
    }
});

$('#weekend_button_bar').click(function() {
    $(this).siblings().removeClass('active');
    console.log("Weekend!");
    if (!weekendBar) {
        weekendBar = true;
        d3.select("#svgchart").selectAll("*").remove();
        drawChart(WEEKEND_IDX);
    }
});
