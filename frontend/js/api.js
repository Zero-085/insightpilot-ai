/**
 * InsightPilot AI - API Client
 * Manages all AJAX requests to the FastAPI backend.
 */
const API = {
    /**
     * Uploads a CSV file to the backend, tracking progress with a callback.
     * @param {File} file The CSV file to upload
     * @param {Function} onProgress Progress callback (percentNum) => {}
     * @returns {Promise<Object>} Response JSON containing dataset_id
     */
    uploadCSV: (file, onProgress) => {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/upload");

            // Track upload progress
            if (xhr.upload && onProgress) {
                xhr.upload.addEventListener("progress", (event) => {
                    if (event.lengthComputable) {
                        const percentComplete = Math.round((event.loaded / event.total) * 100);
                        onProgress(percentComplete);
                    }
                });
            }

            xhr.onload = () => {
                let responseData;
                try {
                    responseData = JSON.parse(xhr.responseText);
                } catch (e) {
                    responseData = { detail: "Failed to parse server response." };
                }

                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(responseData);
                } else {
                    reject(new Error(responseData.detail || `Upload failed with status code ${xhr.status}`));
                }
            };

            xhr.onerror = () => {
                reject(new Error("Network failure occurred during upload."));
            };

            const formData = new FormData();
            formData.append("file", file);
            xhr.send(formData);
        });
    },

    /**
     * Fetches dataset cleaning and statistical analysis summary from GET /analysis
     * @param {string} datasetId 
     * @returns {Promise<Object>} Analysis response dictionary
     */
    fetchAnalysis: async (datasetId) => {
        const url = datasetId ? `/analysis?dataset_id=${encodeURIComponent(datasetId)}` : "/analysis";
        const response = await fetch(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: "Unknown server error." }));
            throw new Error(errData.detail || `Fetch analysis failed with status: ${response.status}`);
        }
        return await response.json();
    },

    /**
     * Fetches Plotly chart configurations from GET /charts
     * @param {string} datasetId 
     * @returns {Promise<Object>} Charts response dictionary
     */
    fetchCharts: async (datasetId) => {
        const url = datasetId ? `/charts?dataset_id=${encodeURIComponent(datasetId)}` : "/charts";
        const response = await fetch(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: "Unknown server error." }));
            throw new Error(errData.detail || `Fetch charts failed with status: ${response.status}`);
        }
        return await response.json();
    }
};
