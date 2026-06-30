/**
 * InsightPilot AI - Charts Engine
 * Interacts with Plotly.js to render and resize analytical charts.
 */
const Charts = {
    /**
     * Renders Plotly charts inside target divs.
     * @param {Object} chartsMap Dictionary of chart type -> Plotly figure data
     */
    renderAll: (chartsMap) => {
        console.log("Charts rendering triggered:", chartsMap);
        
        Charts.renderSingle("chartHist", chartsMap.histogram, "No numerical data available to render a histogram.");
        Charts.renderSingle("chartBar", chartsMap.bar_chart, "No categorical data available to render a bar chart.");
        Charts.renderSingle("chartLine", chartsMap.line_chart, "No datetime index or trend series available to render a line chart.");
        Charts.renderSingle("chartPie", chartsMap.pie_chart, "Dataset categorical attributes are not suitable for a pie chart distribution (must have between 2 and 10 categories).");
    },

    /**
     * Renders a single Plotly figure or displays a fallback message.
     */
    renderSingle: (containerId, figureData, fallbackMsg) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Clean up previous content
        container.innerHTML = "";

        if (!figureData || !figureData.data || figureData.data.length === 0) {
            // Display friendly fallback notice
            container.innerHTML = `
                <div class="empty-state-chart">
                    <p>${fallbackMsg}</p>
                </div>
            `;
            return;
        }

        try {
            // Incorporate responsive and aesthetic layout configurations
            const layout = figureData.layout || {};
            layout.autosize = true;
            layout.margin = layout.margin || { l: 40, r: 20, t: 40, b: 45 };
            
            // Adjust dimensions for grid sizing
            const config = {
                responsive: true,
                displayModeBar: false // Keep it clean, hide toolbar
            };

            Plotly.newPlot(container, figureData.data, layout, config);
        } catch (error) {
            console.error(`Error rendering Plotly chart on container #${containerId}:`, error);
            container.innerHTML = `
                <div class="empty-state-chart" style="color: var(--danger);">
                    <p>Failed to render chart: ${error.message}</p>
                </div>
            `;
        }
    },

    /**
     * Triggers Plotly to resize all active figures in accordance with screen sizing changes.
     */
    resizeAll: () => {
        const chartIds = ["chartHist", "chartBar", "chartLine", "chartPie"];
        chartIds.forEach(id => {
            const el = document.getElementById(id);
            // Verify it has been populated with a Plotly layout before resizing
            if (el && el.classList.contains("js-plotly-plot")) {
                Plotly.Plots.resize(el);
            }
        });
    }
};

// Bind window resize listener to maintain responsive sizing
window.addEventListener("resize", () => {
    Charts.resizeAll();
});
