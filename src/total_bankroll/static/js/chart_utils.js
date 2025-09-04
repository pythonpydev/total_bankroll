/*
 * Custom Chart.js Utility for StakeEasy.net
 * This file provides a centralized function to create beautiful,
 * interactive, and consistent charts across the application.
 */

// A modern, consistent color palette for the charts
const CHART_COLORS = [
    'rgba(54, 162, 235, 0.9)', // Blue
    'rgba(255, 99, 132, 0.9)',  // Red
    'rgba(75, 192, 192, 0.9)',  // Green
    'rgba(255, 206, 86, 0.9)',  // Yellow
    'rgba(153, 102, 255, 0.9)', // Purple
    'rgba(255, 159, 64, 0.9)',  // Orange
    'rgba(101, 115, 128, 0.9)', // Grey
];

// Function to get a color from the palette based on index
function getColor(index) {
    return CHART_COLORS[index % CHART_COLORS.length];
}

// Function to create a semi-transparent version of a color for backgrounds
function getBackgroundColor(color) {
    return color.replace('0.9', '0.2');
}

/**
 * Creates a Chart.js instance with enhanced default options.
 * @param {CanvasRenderingContext2D} ctx - The context of the canvas element.
 * @param {string} chartType - The type of chart (e.g., 'line', 'bar', 'pie').
 * @param {object} chartData - The data object for the chart (labels, datasets).
 * @param {object} customOptions - Custom options to merge with the defaults.
 */
function createChart(ctx, chartType, chartData, customOptions = {}) {

    // Apply the color palette to the datasets
    chartData.datasets.forEach((dataset, index) => {
        const color = getColor(index);
        dataset.borderColor = color;
        dataset.backgroundColor = (chartType === 'line' || chartType === 'radar') ? getBackgroundColor(color) : color;
        dataset.pointBackgroundColor = color;
        dataset.pointHoverBorderColor = 'rgba(0, 0, 0, 1)';
        dataset.pointHoverBackgroundColor = '#fff';
        dataset.fill = (chartType === 'line' || chartType === 'radar'); // Fill area under line/radar
    });

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart',
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        family: "'Merriweather Sans', sans-serif",
                    }
                },
            },
            tooltip: {
                enabled: true,
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleFont: {
                    size: 14,
                    weight: 'bold',
                    family: "'Merriweather Sans', sans-serif",
                },
                bodyFont: {
                    size: 12,
                    family: "'Merriweather Sans', sans-serif",
                },
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        },
    };

    // Deep merge custom options into default options
    const finalOptions = _.merge(defaultOptions, customOptions);

    return new Chart(ctx, {
        type: chartType,
        data: chartData,
        options: finalOptions,
    });
}