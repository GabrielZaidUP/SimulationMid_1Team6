// Dashboard data state
const dashboardData = {
    productionData: [],
    stationData: [],
    materialData: []
};

// Dashboard settings
const settings = {
    timePeriod: 'daily',
    selectedStation: 'all'
};

// Color schemes
const colors = {
    primary: '#4a6fff',
    secondary: '#ff4a4a',
    tertiary: '#ffaa4a',
    success: '#4aff4a',
    warning: '#ffff4a',
    neutral: '#e0e0e0'
};

// DOM elements
const elements = {
    timePeriod: document.getElementById('time-period'),
    stationFilter: document.getElementById('station-filter'),
    applyFilters: document.getElementById('apply-filters'),
    refreshData: document.getElementById('refresh-data'),
    runSimulation: document.getElementById('run-simulation'),
    kpiContainer: document.querySelector('.kpi-container'),
    productionChart: document.getElementById('production-trend-chart'),
    executiveInsights: document.getElementById('executive-insights'),
    stationHeatmap: document.getElementById('station-heatmap'),
    stationInsights: document.getElementById('station-insights'),
    materialChart: document.getElementById('material-chart'),
    materialInsights: document.getElementById('material-insights'),
    correlationChart: document.getElementById('correlation-chart'),
    correlationStats: document.getElementById('correlation-stats')
};

// Tooltip setup
const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);

// Initialize the dashboard
function initDashboard() {
    // Set up event listeners
    elements.applyFilters.addEventListener('click', updateDashboard);
    elements.refreshData.addEventListener('click', loadData);
    elements.runSimulation.addEventListener('click', runSimulation);
    
    // Load initial data
    loadData().then(() => {
        // Update the dashboard with initial data
        updateDashboard();
    });
}

// Run the Python simulation
async function runSimulation() {
    // Change button state to indicate processing
    const originalText = elements.runSimulation.textContent;
    elements.runSimulation.textContent = "Running...";
    elements.runSimulation.disabled = true;
    
    try {
        // Call the server endpoint to run the simulation
        const response = await fetch('/run_simulation');
        
        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Simulation completed successfully
            alert("Simulation completed successfully!");
            
            // Automatically reload the data
            await loadData();
            updateDashboard();
        } else {
            // Simulation failed
            alert("Simulation failed: " + result.message);
            console.error(result.output);
        }
    } catch (error) {
        console.error('Error running simulation:', error);
        alert("Failed to run simulation. Check console for details.");
    } finally {
        // Reset button state
        elements.runSimulation.textContent = originalText;
        elements.runSimulation.disabled = false;
    }
}

// Load data from CSV files
async function loadData() {
    try {
        // Load production data
        const productionData = await d3.csv('/dashboard_data/production_data.csv');
        dashboardData.productionData = productionData;
        
        // Load station data
        const stationData = await d3.csv('/dashboard_data/station_data.csv');
        dashboardData.stationData = stationData;
        
        // Load material data
        const materialData = await d3.csv('/dashboard_data/material_data.csv');
        dashboardData.materialData = materialData;
        
        // Update the station filter options
        updateStationFilter();
        
        return true;
    } catch (error) {
        console.error('Error loading data:', error);
        
        // If we can't load the actual files, generate sample data
        generateSampleData();
        
        return false;
    }
}

// Generate sample data for testing
function generateSampleData() {
    // Sample production data
    dashboardData.productionData = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 40);
    
    for (let i = 0; i < 40; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        
        dashboardData.productionData.push({
            date: currentDate.toISOString().split('T')[0],
            production: Math.floor(Math.random() * 100) + 200,
            faulty: Math.floor(Math.random() * 20),
            faulty_rate: (Math.random() * 0.1).toFixed(3),
            avg_downtime: (Math.random() * 5).toFixed(2),
            avg_production_time: (Math.random() * 10 + 5).toFixed(2)
        });
    }
    
    // Sample station data
    const stationNames = [
        "Circuit Preparation", 
        "Microcontroller Integration", 
        "LED Display Assembly", 
        "Case Assembly", 
        "Water Sealing", 
        "Testing & Packaging"
    ];
    
    dashboardData.stationData = [];
    for (let i = 0; i < 6; i++) {
        dashboardData.stationData.push({
            station_id: i,
            station_name: stationNames[i],
            occupancy_rate: (Math.random() * 0.7 + 0.2).toFixed(3),
            downtime: (Math.random() * 10).toFixed(2)
        });
    }
    
    // Sample material data
    const materials = [
        "base_circuits",
        "microcontrollers",
        "led_displays",
        "case",
        "water_sealant",
        "batteries"
    ];
    
    dashboardData.materialData = [];
    for (let i = 0; i < materials.length; i++) {
        const usage = Math.floor(Math.random() * 1000) + 500;
        const resupply = Math.floor(Math.random() * 50) + 10;
        
        dashboardData.materialData.push({
            material: materials[i],
            display_name: materials[i].replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            total_usage: usage,
            total_resupply: resupply,
            avg_usage: (usage / 40).toFixed(2),
            avg_resupply: (resupply / 40).toFixed(2)
        });
    }
    
    // Update the station filter
    updateStationFilter();
}

// Update station filter dropdown based on station data
function updateStationFilter() {
    // Clear existing options except the first one
    while (elements.stationFilter.options.length > 1) {
        elements.stationFilter.remove(1);
    }
    
    // Add station options if we have station data
    if (dashboardData.stationData && dashboardData.stationData.length) {
        dashboardData.stationData.forEach(station => {
            const option = document.createElement('option');
            option.value = station.station_name;
            option.textContent = station.station_name;
            elements.stationFilter.appendChild(option);
        });
    }
}

// Update the entire dashboard
function updateDashboard() {
    // Update settings based on filter values
    settings.timePeriod = elements.timePeriod.value;
    settings.selectedStation = elements.stationFilter.value;
    
    // Clear existing content
    clearDashboardContent();
    
    // Create the dashboard sections
    createExecutiveSummary();
    createStationAnalysis();
    createMaterialAnalysis();
    createCorrelationAnalysis();
}

// Clear all dashboard content
function clearDashboardContent() {
    elements.kpiContainer.innerHTML = '';
    elements.executiveInsights.innerHTML = '';
    elements.stationInsights.innerHTML = '';
    elements.materialInsights.innerHTML = '';
    elements.correlationStats.innerHTML = '';
    
    // Clear D3 charts
    d3.select('#production-trend-chart').html('');
    d3.select('#station-heatmap').html('');
    d3.select('#material-chart').html('');
    d3.select('#correlation-chart').html('');
}

// Create executive summary section
function createExecutiveSummary() {
    if (!dashboardData.productionData || !dashboardData.productionData.length) {
        elements.kpiContainer.innerHTML = '<p>No production data available</p>';
        return;
    }
    
    // Calculate KPIs
    const totalProduction = d3.sum(dashboardData.productionData, d => +d.production);
    const totalFaulty = d3.sum(dashboardData.productionData, d => +d.faulty);
    const faultRate = totalFaulty / totalProduction || 0;
    const avgProductionTime = d3.mean(dashboardData.productionData, d => +d.avg_production_time);
    
    // Create KPI cards
    createKPICard('Total Production', totalProduction.toLocaleString(), 'units');
    createKPICard('Fault Rate', (faultRate * 100).toFixed(1) + '%', '');
    createKPICard('Avg Production Time', avgProductionTime.toFixed(2), 'units');
    
    // Create production trend chart
    createProductionTrendChart();
    
    // Add insights
    createExecutiveInsights(faultRate);
}

// Create a KPI card
function createKPICard(label, value, unit) {
    const kpiCard = document.createElement('div');
    kpiCard.className = 'kpi-card';
    
    kpiCard.innerHTML = `
        <div class="kpi-label">${label}</div>
        <div class="kpi-value">${value}</div>
        <div class="kpi-unit">${unit}</div>
    `;
    
    elements.kpiContainer.appendChild(kpiCard);
}

// Aggregate data by time period
function aggregateDataByTimePeriod(data, period) {
    let aggregatedData = [];
    
    // Group data by time period
    switch (period) {
        case 'daily':
            // Use the data as is, just format date
            aggregatedData = data.map(d => ({
                timeKey: formatDate(new Date(d.date)),
                ...d
            }));
            break;
        case 'weekly':
            // Group by week
            const weekGroups = d3.group(data, d => {
                const date = new Date(d.date);
                const weekStart = new Date(date);
                weekStart.setDate(date.getDate() - date.getDay());
                return formatDate(weekStart);
            });
            
            weekGroups.forEach((group, weekStart) => {
                aggregatedData.push({
                    timeKey: `Week of ${weekStart}`,
                    production: d3.sum(group, d => +d.production),
                    faulty: d3.sum(group, d => +d.faulty),
                    faulty_rate: d3.sum(group, d => +d.faulty) / d3.sum(group, d => +d.production)
                });
            });
            break;
        case 'monthly':
            // Group by month
            const monthGroups = d3.group(data, d => {
                const date = new Date(d.date);
                return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            });
            
            monthGroups.forEach((group, monthKey) => {
                const [year, month] = monthKey.split('-');
                const monthName = new Date(year, month - 1, 1).toLocaleString('default', { month: 'long' });
                
                aggregatedData.push({
                    timeKey: `${monthName} ${year}`,
                    production: d3.sum(group, d => +d.production),
                    faulty: d3.sum(group, d => +d.faulty),
                    faulty_rate: d3.sum(group, d => +d.faulty) / d3.sum(group, d => +d.production)
                });
            });
            break;
        case 'quarterly':
            // Group by quarter
            const quarterGroups = d3.group(data, d => {
                const date = new Date(d.date);
                const quarter = Math.floor(date.getMonth() / 3) + 1;
                return `${date.getFullYear()}-Q${quarter}`;
            });
            
            quarterGroups.forEach((group, quarterKey) => {
                aggregatedData.push({
                    timeKey: quarterKey,
                    production: d3.sum(group, d => +d.production),
                    faulty: d3.sum(group, d => +d.faulty),
                    faulty_rate: d3.sum(group, d => +d.faulty) / d3.sum(group, d => +d.production)
                });
            });
            break;
    }
    
    return aggregatedData;
}

// Helper function to format date
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

// Helper function to capitalize first letter
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Format metric name for display
function formatMetricName(metric) {
    return metric.split('_').map(capitalizeFirst).join(' ');
}

// Create production trend chart
function createProductionTrendChart() {
    // Filter and prepare data based on selected time period
    const data = aggregateDataByTimePeriod(dashboardData.productionData, settings.timePeriod);
    
    // Set chart dimensions
    const margin = {top: 30, right: 70, bottom: 60, left: 50};
    const width = elements.productionChart.clientWidth - margin.left - margin.right;
    const height = elements.productionChart.clientHeight - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select('#production-trend-chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Add title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text(`Production Trend (${capitalizeFirst(settings.timePeriod)})`);
    
    // Create scales
    const x = d3.scaleBand()
        .domain(data.map(d => d.timeKey))
        .range([0, width])
        .padding(0.2);
    
    const y1 = d3.scaleLinear()
        .domain([0, d3.max(data, d => +d.production) * 1.1])
        .nice()
        .range([height, 0]);
    
    const y2 = d3.scaleLinear()
        .domain([0, Math.max(0.2, d3.max(data, d => +d.faulty_rate) * 1.2)])
        .nice()
        .range([height, 0]);
    
    // Add axes
    svg.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(y1).ticks(5).tickSize(-width))
        .call(g => g.select('.domain').remove())
        .call(g => g.selectAll('.tick line').attr('stroke-opacity', 0.5));
    
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-45)');
    
    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y1));
    
    svg.append('g')
        .attr('class', 'y-axis-right')
        .attr('transform', `translate(${width},0)`)
        .call(d3.axisRight(y2).tickFormat(d => (d * 100).toFixed(0) + '%'));
    
    // Add y-axis labels
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -height / 2)
        .attr('text-anchor', 'middle')
        .text('Production');
    
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', width + 40)
        .attr('x', -height / 2)
        .attr('text-anchor', 'middle')
        .text('Fault Rate (%)');
    
    // Draw production bars
    svg.selectAll('.production-bar')
        .data(data)
        .enter()
        .append('rect')
        .attr('class', 'production-bar')
        .attr('x', d => x(d.timeKey))
        .attr('y', d => y1(+d.production))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y1(+d.production))
        .attr('fill', colors.primary)
        .on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>${d.timeKey}</strong><br/>
                Production: ${(+d.production).toLocaleString()}<br/>
                Faulty: ${(+d.faulty).toLocaleString()}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        }).on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Draw fault rate line
    const line = d3.line()
        .x(d => x(d.timeKey) + x.bandwidth() / 2)
        .y(d => y2(+d.faulty_rate));
    
    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', colors.secondary)
        .attr('stroke-width', 2)
        .attr('d', line);
    
    // Add dots for each data point
    svg.selectAll('.fault-dot')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'fault-dot')
        .attr('cx', d => x(d.timeKey) + x.bandwidth() / 2)
        .attr('cy', d => y2(+d.faulty_rate))
        .attr('r', 4)
        .attr('fill', colors.secondary)
        .on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>${d.timeKey}</strong><br/>
                Fault Rate: ${(+d.faulty_rate * 100).toFixed(1)}%
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Add target line for fault rate
    svg.append('line')
        .attr('x1', 0)
        .attr('y1', y2(0.05))
        .attr('x2', width)
        .attr('y2', y2(0.05))
        .attr('stroke', colors.secondary)
        .attr('stroke-dasharray', '4')
        .attr('stroke-width', 1);
    
    svg.append('text')
        .attr('x', 5)
        .attr('y', y2(0.05) - 5)
        .attr('text-anchor', 'start')
        .style('font-size', '12px')
        .style('fill', colors.secondary)
        .text('Target (5%)');
}

// Create executive insights
function createExecutiveInsights(faultRate) {
    // Determine production status based on fault rate
    const statusClass = faultRate < 0.05 ? 'success-insight' : 'warning-insight';
    const statusText = faultRate < 0.05 ? 
        'Production is running smoothly' : 
        'High fault rate detected';
    
    const insightElem = document.createElement('div');
    insightElem.className = `insight-item ${statusClass}`;
    insightElem.textContent = `${statusText} (${(faultRate * 100).toFixed(1)}%)`;
    elements.executiveInsights.appendChild(insightElem);
    
    // Add bottleneck insight if we have station data
    if (dashboardData.stationData && dashboardData.stationData.length) {
        // Find bottleneck station - station with highest occupancy rate
        const bottleneck = dashboardData.stationData.reduce((prev, current) => {
            return +prev.occupancy_rate > +current.occupancy_rate ? prev : current;
        });
        
        const bottleneckElem = document.createElement('div');
        bottleneckElem.className = 'insight-item';
        bottleneckElem.textContent = `Bottleneck identified at ${bottleneck.station_name} (Occupancy: ${(+bottleneck.occupancy_rate * 100).toFixed(1)}%)`;
        elements.executiveInsights.appendChild(bottleneckElem);
        
        // Find high downtime station
        const highDowntime = dashboardData.stationData.reduce((prev, current) => {
            return +prev.downtime > +current.downtime ? prev : current;
        });
        
        const downtimeElem = document.createElement('div');
        downtimeElem.className = 'insight-item';
        downtimeElem.textContent = `Maintenance needed at ${highDowntime.station_name} (Downtime: ${(+highDowntime.downtime).toFixed(1)} units)`;
        elements.executiveInsights.appendChild(downtimeElem);
    }
}

// Create station analysis section
function createStationAnalysis() {
    if (!dashboardData.stationData || !dashboardData.stationData.length) {
        d3.select('#station-heatmap').html('<p>No station data available</p>');
        return;
    }
    
    // Filter station data if a specific station is selected
    let filteredData = dashboardData.stationData;
    if (settings.selectedStation !== 'all') {
        filteredData = dashboardData.stationData.filter(
            d => d.station_name === settings.selectedStation
        );
    }
    
    // Create the heatmap
    createStationHeatmap(filteredData);
    
    // Create station insights
    createStationInsights();
}

// Create station heatmap
function createStationHeatmap(data) {
    // Set chart dimensions
    const margin = {top: 30, right: 50, bottom: 50, left: 150};
    const width = elements.stationHeatmap.clientWidth - margin.left - margin.right;
    const height = elements.stationHeatmap.clientHeight - margin.top - margin.bottom;
    
    // Prepare heatmap data
    const heatmapData = [];
    const metrics = ['occupancy_rate', 'downtime'];
    
    data.forEach(station => {
        metrics.forEach(metric => {
            let value = +station[metric];
            
            // Normalize values based on metric
            if (metric === 'occupancy_rate') {
                // Already between 0-1
            } else if (metric === 'downtime') {
                // Normalize downtime relative to max
                const maxDowntime = d3.max(dashboardData.stationData, d => +d.downtime);
                value = value / maxDowntime;
            }
            
            heatmapData.push({
                station: station.station_name,
                metric: formatMetricName(metric),
                value: value
            });
        });
    });
    
    // Create SVG
    const svg = d3.select('#station-heatmap')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Add title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text('Station Performance Heatmap');
    
    // Create scales
    const x = d3.scaleBand()
        .domain(metrics.map(formatMetricName))
        .range([0, width])
        .padding(0.05);
    
    const y = d3.scaleBand()
        .domain(data.map(d => d.station_name))
        .range([0, height])
        .padding(0.05);
    
    const color = d3.scaleSequential()
        .interpolator(d3.interpolateYlOrRd)
        .domain([0, 1]);
    
    // Draw heatmap cells
    svg.selectAll('rect')
        .data(heatmapData)
        .enter()
        .append('rect')
        .attr('x', d => x(d.metric))
        .attr('y', d => y(d.station))
        .attr('width', x.bandwidth())
        .attr('height', y.bandwidth())
        .attr('fill', d => color(d.value))
        .on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            
            let displayValue;
            if (d.metric === 'Occupancy Rate') {
                displayValue = (d.value * 100).toFixed(1) + '%';
            } else {
                displayValue = d.value.toFixed(2);
            }
            
            tooltip.html(`
                <strong>${d.station}</strong><br/>
                ${d.metric}: ${displayValue}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Add axes
    svg.append('g')
        .call(d3.axisTop(x));
    
    svg.append('g')
        .call(d3.axisLeft(y));
    
    // Add color legend
    const legendWidth = 20;
    const legendHeight = height;
    
    const legend = svg.append('g')
        .attr('transform', `translate(${width + 20}, 0)`);
    
    // Create gradient
    const legendGradient = legend.append('defs')
        .append('linearGradient')
        .attr('id', 'legend-gradient')
        .attr('x1', '0%')
        .attr('y1', '100%')
        .attr('x2', '0%')
        .attr('y2', '0%');
    
    // Add gradient stops
    legendGradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', color(0));
        
    legendGradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', color(1));
    
    // Add gradient rectangle
    legend.append('rect')
        .attr('width', legendWidth)
        .attr('height', legendHeight)
        .style('fill', 'url(#legend-gradient)');
    
    // Add legend axis
    const legendScale = d3.scaleLinear()
        .domain([0, 1])
        .range([legendHeight, 0]);
    
    legend.append('g')
        .attr('transform', `translate(${legendWidth}, 0)`)
        .call(d3.axisRight(legendScale)
            .ticks(5)
            .tickFormat(d => {
                // Format as percentage for occupancy rate
                return (d * 100).toFixed(0) + '%';
            })
        );
    
    legend.append('text')
        .attr('transform', 'rotate(90)')
        .attr('x', legendHeight / 2)
        .attr('y', -legendWidth - 25)
        .attr('text-anchor', 'middle')
        .text('Performance Metric (Normalized)');
}

// Create station insights
function createStationInsights() {
    if (!dashboardData.stationData || !dashboardData.stationData.length) {
        return;
    }
    
    // Find high occupancy station
    const highOccupancy = dashboardData.stationData.reduce((prev, current) => {
        return +prev.occupancy_rate > +current.occupancy_rate ? prev : current;
    });
    
    const highOccElem = document.createElement('div');
    highOccElem.className = 'insight-item';
    highOccElem.textContent = `Increase capacity at ${highOccupancy.station_name} (Occupancy: ${(+highOccupancy.occupancy_rate * 100).toFixed(1)}%)`;
    elements.stationInsights.appendChild(highOccElem);
    
    // Find high downtime station
    const highDowntime = dashboardData.stationData.reduce((prev, current) => {
        return +prev.downtime > +current.downtime ? prev : current;
    });
    
    const highDownElem = document.createElement('div');
    highDownElem.className = 'insight-item';
    highDownElem.textContent = `Maintenance needed at ${highDowntime.station_name} (Downtime: ${(+highDowntime.downtime).toFixed(1)} units)`;
    elements.stationInsights.appendChild(highDownElem);
    
    // Check if same station needs both interventions
    if (highOccupancy.station_name === highDowntime.station_name) {
        const criticalElem = document.createElement('div');
        criticalElem.className = 'insight-item warning-insight';
        criticalElem.textContent = `Critical intervention required at ${highOccupancy.station_name}`;
        elements.stationInsights.appendChild(criticalElem);
    }
}

// Create material analysis section
function createMaterialAnalysis() {
    if (!dashboardData.materialData || !dashboardData.materialData.length) {
        d3.select('#material-chart').html('<p>No material data available</p>');
        return;
    }
    
    // Calculate risk score for each material
    dashboardData.materialData.forEach(material => {
        material.risk_score = +material.avg_usage / (Math.max(0.1, +material.avg_resupply));
    });
    
    // Sort by risk score
    const sortedMaterials = [...dashboardData.materialData].sort((a, b) => b.risk_score - a.risk_score);
    
    // Create bar chart
    createMaterialChart(sortedMaterials);
    
    // Create material insights
    createMaterialInsights(sortedMaterials);
}

// Create material chart
function createMaterialChart(data) {
    // Set chart dimensions
    const margin = {top: 30, right: 50, bottom: 70, left: 60};
    const width = elements.materialChart.clientWidth - margin.left - margin.right;
    const height = elements.materialChart.clientHeight - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select('#material-chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Add title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text('Supply Chain Risk Assessment');
    
    // Create scales
    const x = d3.scaleBand()
        .domain(data.map(d => d.display_name))
        .range([0, width])
        .padding(0.3);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.risk_score) * 1.1])
        .nice()
        .range([height, 0]);
    
    // Create color scale for risk based on value
    const colorScale = d3.scaleSequential()
        .interpolator(d3.interpolateYlOrRd)
        .domain([0, d3.max(data, d => d.risk_score)]);
    
    // Add axes
    svg.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(y).ticks(5).tickSize(-width))
        .call(g => g.select('.domain').remove())
        .call(g => g.selectAll('.tick line').attr('stroke-opacity', 0.5));
    
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-45)');
    
    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y));
    
    // Add y-axis label
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -height / 2)
        .attr('text-anchor', 'middle')
        .text('Risk Score');
    
    // Draw bars
    svg.selectAll('.material-bar')
        .data(data)
        .enter()
        .append('rect')
        .attr('class', 'material-bar')
        .attr('x', d => x(d.display_name))
        .attr('y', d => y(d.risk_score))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.risk_score))
        .attr('fill', d => colorScale(d.risk_score))
        .on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>${d.display_name}</strong><br/>
                Risk Score: ${d.risk_score.toFixed(2)}<br/>
                Avg Usage: ${d.avg_usage}<br/>
                Avg Resupply: ${d.avg_resupply}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Add bar labels
    svg.selectAll('.bar-label')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'bar-label')
        .attr('x', d => x(d.display_name) + x.bandwidth() / 2)
        .attr('y', d => y(d.risk_score) - 5)
        .attr('text-anchor', 'middle')
        .text(d => d.risk_score.toFixed(1))
        .style('font-size', '10px');
}

// Create material insights
function createMaterialInsights(data) {
    // Add recommendations for top risk materials
    if (data.length > 0) {
        // Top 2 highest risk materials
        for (let i = 0; i < Math.min(2, data.length); i++) {
            const material = data[i];
            const insightElem = document.createElement('div');
            insightElem.className = 'insight-item';
            insightElem.textContent = `Increase order quantity for ${material.display_name} (Risk: ${material.risk_score.toFixed(1)})`;
            elements.materialInsights.appendChild(insightElem);
        }
        
        // Add insight for excessive inventory if any material has very low risk
        const lowRiskMaterials = data.filter(m => m.risk_score < 0.5);
        if (lowRiskMaterials.length > 0) {
            const lowestRisk = lowRiskMaterials[lowRiskMaterials.length - 1];
            const insightElem = document.createElement('div');
            insightElem.className = 'insight-item success-insight';
            insightElem.textContent = `Consider reducing inventory of ${lowestRisk.display_name} (Low Risk: ${lowestRisk.risk_score.toFixed(1)})`;
            elements.materialInsights.appendChild(insightElem);
        }
    }
}

// Create correlation analysis section
function createCorrelationAnalysis() {
    if (!dashboardData.stationData || dashboardData.stationData.length < 2) {
        d3.select('#correlation-chart').html('<p>Insufficient data for correlation analysis</p>');
        return;
    }
    
    // Create scatter plot
    createCorrelationChart();
    
    // Calculate correlation
    const occupancyValues = dashboardData.stationData.map(d => +d.occupancy_rate);
    const downtimeValues = dashboardData.stationData.map(d => +d.downtime);
    
    const correlation = calculateCorrelation(occupancyValues, downtimeValues);
    
    // Create stats
    createCorrelationStats(correlation);
}

// Create correlation chart
function createCorrelationChart() {
    // Set chart dimensions
    const margin = {top: 30, right: 30, bottom: 50, left: 60};
    const width = elements.correlationChart.clientWidth - margin.left - margin.right;
    const height = elements.correlationChart.clientHeight - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select('#correlation-chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Add title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text('Correlation: Station Occupancy vs Downtime');
    
    // Create scales
    const x = d3.scaleLinear()
        .domain([0, d3.max(dashboardData.stationData, d => +d.occupancy_rate) * 1.1])
        .nice()
        .range([0, width]);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(dashboardData.stationData, d => +d.downtime) * 1.1])
        .nice()
        .range([height, 0]);
    
    // Add grid
    svg.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(y).ticks(5).tickSize(-width))
        .call(g => g.select('.domain').remove())
        .call(g => g.selectAll('.tick line').attr('stroke-opacity', 0.5));
    
    svg.append('g')
        .attr('class', 'grid')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5).tickSize(-height))
        .call(g => g.select('.domain').remove())
        .call(g => g.selectAll('.tick line').attr('stroke-opacity', 0.5));
    
    // Add axes
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat(d => (d * 100).toFixed(0) + '%'));
    
    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y));
    
    // Add axis labels
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height + 40)
        .attr('text-anchor', 'middle')
        .text('Occupancy Rate');
    
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -height / 2)
        .attr('text-anchor', 'middle')
        .text('Downtime (units)');
    
    // Calculate regression line
    const regression = linearRegression(
        dashboardData.stationData.map(d => +d.occupancy_rate),
        dashboardData.stationData.map(d => +d.downtime)
    );
    
    // Draw regression line
    svg.append('line')
        .attr('x1', x(0))
        .attr('y1', y(regression.intercept))
        .attr('x2', x(1))
        .attr('y2', y(regression.intercept + regression.slope))
        .attr('stroke', colors.secondary)
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '4');
    
    // Draw scatter points
    svg.selectAll('.dot')
        .data(dashboardData.stationData)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => x(+d.occupancy_rate))
        .attr('cy', d => y(+d.downtime))
        .attr('r', 7)
        .attr('fill', colors.primary)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
        .on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>${d.station_name}</strong><br/>
                Occupancy: ${(+d.occupancy_rate * 100).toFixed(1)}%<br/>
                Downtime: ${(+d.downtime).toFixed(1)} units
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Add point labels
    svg.selectAll('.point-label')
        .data(dashboardData.stationData)
        .enter()
        .append('text')
        .attr('class', 'point-label')
        .attr('x', d => x(+d.occupancy_rate) + 10)
        .attr('y', d => y(+d.downtime) - 5)
        .text(d => d.station_name)
        .style('font-size', '10px');
}

// Create correlation stats
function createCorrelationStats(correlation) {
    const correlationElem = document.createElement('div');
    correlationElem.className = 'insight-item';
    correlationElem.innerHTML = `<strong>Correlation coefficient:</strong> ${correlation.toFixed(2)}`;
    elements.correlationStats.appendChild(correlationElem);
    
    // Interpret correlation
    let interpretation, conclusion;
    
    if (Math.abs(correlation) < 0.3) {
        interpretation = "Weak or no relationship between occupancy and downtime.";
    } else if (Math.abs(correlation) < 0.7) {
        interpretation = "Moderate relationship between occupancy and downtime.";
    } else {
        interpretation = "Strong relationship between occupancy and downtime.";
    }
    
    if (correlation > 0) {
        conclusion = "Stations with higher occupancy tend to have more downtime.";
    } else {
        conclusion = "Stations with higher occupancy tend to have less downtime.";
    }
    
    const interpretElem = document.createElement('div');
    interpretElem.className = 'insight-item';
    interpretElem.textContent = interpretation;
    elements.correlationStats.appendChild(interpretElem);
    
    const conclusionElem = document.createElement('div');
    conclusionElem.className = 'insight-item';
    conclusionElem.textContent = conclusion;
    elements.correlationStats.appendChild(conclusionElem);
    
    // Add recommendation based on correlation
    const recommendationElem = document.createElement('div');
    recommendationElem.className = 'insight-item';
    
    if (correlation > 0.3) {
        recommendationElem.textContent = "Consider adding more resources to high-occupancy stations to reduce downtime.";
    } else if (correlation < -0.3) {
        recommendationElem.textContent = "The inverse relationship suggests current resource allocation is effective.";
    } else {
        recommendationElem.textContent = "No clear pattern - investigate stations individually for optimization.";
    }
    
    elements.correlationStats.appendChild(recommendationElem);
}

// Calculate Pearson correlation coefficient
function calculateCorrelation(x, y) {
    const n = x.length;
    
    // Calculate means
    const xMean = x.reduce((sum, val) => sum + val, 0) / n;
    const yMean = y.reduce((sum, val) => sum + val, 0) / n;
    
    // Calculate correlation
    let numerator = 0;
    let xDenom = 0;
    let yDenom = 0;
    
    for (let i = 0; i < n; i++) {
        const xDiff = x[i] - xMean;
        const yDiff = y[i] - yMean;
        
        numerator += xDiff * yDiff;
        xDenom += xDiff * xDiff;
        yDenom += yDiff * yDiff;
    }
    
    const denominator = Math.sqrt(xDenom * yDenom);
    
    return numerator / denominator;
}

// Calculate linear regression
function linearRegression(x, y) {
    const n = x.length;
    
    // Calculate means
    const xMean = x.reduce((sum, val) => sum + val, 0) / n;
    const yMean = y.reduce((sum, val) => sum + val, 0) / n;
    
    // Calculate slope and intercept
    let numerator = 0;
    let denominator = 0;
    
    for (let i = 0; i < n; i++) {
        numerator += (x[i] - xMean) * (y[i] - yMean);
        denominator += (x[i] - xMean) * (x[i] - xMean);
    }
    
    const slope = numerator / denominator;
    const intercept = yMean - slope * xMean;
    
    return { slope, intercept };
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', initDashboard);