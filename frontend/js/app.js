/**
 * InsightPilot AI - App Orchestrator
 * Bootstraps frontend modules and coordinates sessions.
 */
document.addEventListener("DOMContentLoaded", () => {
    console.log("InsightPilot AI Frontend Orchestrator Bootstrapping...");

    const dropzoneEl = document.getElementById("uploadDropzone");
    const fileInputEl = document.getElementById("csvFileInput");

    // Track active dataset ID in memory
    let activeDatasetId = null;

    // Define upload callbacks
    const uploadCallbacks = {
        onSelect: async (file) => {
            console.log("Selected file for upload:", file.name);
            UI.clearNotifications();
            UI.updateUploadProgress(0);
            Upload.setDisabled(dropzoneEl, fileInputEl, true);

            try {
                // 1. Upload CSV to backend
                const uploadRes = await API.uploadCSV(file, (percent) => {
                    UI.updateUploadProgress(percent);
                });

                if (uploadRes.success) {
                    activeDatasetId = uploadRes.dataset_id;
                    UI.showNotification(`File "${file.name}" uploaded successfully! Starting analysis...`, "success");
                    
                    // 2. Trigger pipeline automatically
                    await runDataPipeline(activeDatasetId);
                } else {
                    throw new Error(uploadRes.message || "Failed to upload file.");
                }
            } catch (error) {
                console.error("Upload error:", error);
                UI.showNotification(error.message || "Connection error during file upload.", "error");
                UI.hideUploadProgress();
                Upload.setDisabled(dropzoneEl, fileInputEl, false);
            }
        },
        onError: (errorMsg) => {
            UI.showNotification(errorMsg, "error");
        }
    };

    // Initialize Upload logic
    Upload.init(dropzoneEl, fileInputEl, uploadCallbacks);

    /**
     * Executes the multi-agent analysis and rendering flow.
     */
    async function runDataPipeline(datasetId) {
        UI.showLoading("CleanerAgent is deduplicating and analyzing schema types...");
        UI.hideUploadProgress();

        try {
            // 1. Fetch analysis stats, cleaning report, and insights
            const analysisData = await API.fetchAnalysis(datasetId);
            console.log("Pipeline analysis received:", analysisData);

            UI.showLoading("VisualizerAgent is plotting distributions and trends...");

            // 2. Fetch Plotly chart specifications
            const chartsData = await API.fetchCharts(datasetId);
            console.log("Pipeline charts received:", chartsData);

            // 3. Update DOM components
            UI.populateKPIs(analysisData.analysis, analysisData.cleaning_report);
            UI.renderCleaningLogs(analysisData.cleaning_report);
            UI.renderInsights(analysisData.insights);
            
            // Render table preview using the new backend support
            if (analysisData.analysis && analysisData.analysis.dataset_preview) {
                UI.renderDatasetPreview(analysisData.filename, analysisData.analysis.dataset_preview);
            }

            // 4. Render charts
            if (chartsData && chartsData.charts) {
                Charts.renderAll(chartsData.charts);
            }

            UI.showNotification("Multi-agent analysis completed successfully!", "success");

        } catch (pipelineError) {
            console.error("Pipeline execution failure:", pipelineError);
            UI.showNotification(`Pipeline Error: ${pipelineError.message}`, "error");
        } finally {
            UI.hideLoading();
            Upload.setDisabled(dropzoneEl, fileInputEl, false);
        }
    }
});
