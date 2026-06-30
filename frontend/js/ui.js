/**
 * InsightPilot AI - UI Manager
 * Handles DOM manipulation, table assembly, notification logs, loading overlays, and alerts.
 */
const UI = {
    /**
     * Shows a notification banner at the top of the workspace.
     * @param {string} message 
     * @param {"success" | "error"} type 
     */
    showNotification: (message, type = "success") => {
        const container = document.getElementById("notificationArea");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `notification-toast ${type}`;
        
        const text = document.createElement("span");
        text.textContent = message;
        
        const closeBtn = document.createElement("button");
        closeBtn.className = "toast-close-btn";
        closeBtn.innerHTML = "&times;";
        closeBtn.onclick = () => {
            toast.remove();
        };

        toast.appendChild(text);
        toast.appendChild(closeBtn);
        container.appendChild(toast);

        // Auto remove success notifications after 6 seconds
        if (type === "success") {
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 6000);
        }
    },

    clearNotifications: () => {
        const container = document.getElementById("notificationArea");
        if (container) container.innerHTML = "";
    },

    /**
     * Controls the loading spinner overlay screen.
     */
    showLoading: (message) => {
        const overlay = document.getElementById("loadingOverlay");
        const msgEl = document.getElementById("loadingMessage");
        if (overlay) {
            if (msgEl && message) msgEl.textContent = message;
            overlay.style.display = "flex";
        }
    },

    hideLoading: () => {
        const overlay = document.getElementById("loadingOverlay");
        if (overlay) overlay.style.display = "none";
    },

    /**
     * Controls the upload progress bar values.
     */
    updateUploadProgress: (percent) => {
        const container = document.getElementById("uploadProgressContainer");
        const bar = document.getElementById("uploadProgressBar");
        const txt = document.getElementById("uploadProgressText");
        
        if (container) container.style.display = "block";
        if (bar) bar.style.width = `${percent}%`;
        if (txt) txt.textContent = `Uploading: ${percent}%`;
    },

    hideUploadProgress: () => {
        const container = document.getElementById("uploadProgressContainer");
        if (container) container.style.display = "none";
    },

    /**
     * Fills the four dashboard KPI slots.
     */
    populateKPIs: (analysis, cleaning) => {
        const rowsVal = document.getElementById("kpiRows");
        const rowsSub = document.getElementById("kpiRowsSub");
        const colsVal = document.getElementById("kpiCols");
        const colsSub = document.getElementById("kpiColsSub");
        const typesVal = document.getElementById("kpiTypes");
        const typesSub = document.getElementById("kpiTypesSub");
        const cleanedVal = document.getElementById("kpiCleaned");
        const cleanedSub = document.getElementById("kpiCleanedSub");

        if (rowsVal) rowsVal.textContent = analysis.num_rows.toLocaleString();
        if (rowsSub) rowsSub.textContent = "Total records found";

        if (colsVal) colsVal.textContent = analysis.num_columns.toLocaleString();
        if (colsSub) colsSub.textContent = "Dimensions in CSV";

        const numCount = analysis.numeric_columns ? analysis.numeric_columns.length : 0;
        const catCount = analysis.categorical_columns ? analysis.categorical_columns.length : 0;
        if (typesVal) typesVal.textContent = `${numCount} / ${catCount}`;
        if (typesSub) typesSub.textContent = "Num / Cat split";

        const dups = cleaning.duplicates_removed || 0;
        const nulls = Object.values(cleaning.missing_values_summary || {}).reduce((a, b) => a + b, 0);
        if (cleanedVal) cleanedVal.textContent = `${dups} / ${nulls}`;
        if (cleanedSub) cleanedSub.textContent = "Duplicates / Null cells";
    },

    /**
     * Renders dataset columns & preview rows as a table.
     */
    renderDatasetPreview: (filename, preview) => {
        const title = document.getElementById("previewTitle");
        const container = document.getElementById("previewTableContainer");
        if (!container) return;

        if (title) title.textContent = `Dataset Preview (${filename})`;

        if (!preview || !preview.columns || preview.columns.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Failed to generate data preview rows.</p>
                </div>
            `;
            return;
        }

        const table = document.createElement("table");
        
        // Assemble header
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        preview.columns.forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Assemble body
        const tbody = document.createElement("tbody");
        preview.rows.forEach(row => {
            const tr = document.createElement("tr");
            preview.columns.forEach(col => {
                const td = document.createElement("td");
                // Check for nulls and format them cleanly
                const val = row[col];
                if (val === null || val === undefined) {
                    td.innerHTML = `<span style="color: var(--text-muted); font-style: italic;">null</span>`;
                } else {
                    td.textContent = typeof val === "number" ? val.toLocaleString() : val;
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        // Clean container and insert table
        container.innerHTML = "";
        container.appendChild(table);
    },

    /**
     * Builds data validation/cleaning log entries.
     */
    renderCleaningLogs: (cleaning) => {
        const container = document.getElementById("logsContainer");
        if (!container) return;

        container.innerHTML = "";

        const addLogItem = (statusSymbol, text, typeClass) => {
            const logItem = document.createElement("div");
            logItem.className = `log-item ${typeClass}`;
            logItem.innerHTML = `
                <span class="log-status">${statusSymbol}</span>
                <div class="log-content">
                    <span class="log-time">Just Now</span>
                    <p>${text}</p>
                </div>
            `;
            container.appendChild(logItem);
        };

        // 1. Duplicates Log
        const dups = cleaning.duplicates_removed || 0;
        if (dups > 0) {
            addLogItem("✔", `Removed <strong>${dups} duplicate rows</strong> from the dataset automatically.`, "success");
        } else {
            addLogItem("✔", `Zero duplicates detected. Data structure integrity is intact.`, "success");
        }

        // 2. Missing Value summary log
        const missingSum = Object.values(cleaning.missing_values_summary || {}).reduce((a, b) => a + b, 0);
        if (missingSum > 0) {
            let details = Object.entries(cleaning.missing_values_summary)
                .filter(([_, count]) => count > 0)
                .map(([col, count]) => `<strong>${col}</strong> (${count} empty)`)
                .join(", ");
            addLogItem("⚠", `Detected <strong>${missingSum} empty cells</strong> across: ${details}.`, "warning");
        } else {
            addLogItem("✔", "No missing or null data fields found. The table is complete.", "success");
        }

        // 3. Inferred Datatypes Log
        const types = cleaning.inferred_data_types || {};
        if (Object.keys(types).length > 0) {
            const typeLabels = Object.entries(types)
                .map(([col, type]) => `<strong>${col}</strong> (${type})`)
                .join(", ");
            addLogItem("ℹ", `Inferred datatypes: ${typeLabels}`, "info");
        }

        // 4. Completed status log
        addLogItem("✔", "Dataset successfully processed and locked for business queries.", "success");
    },

    /**
     * Displays AI Narrative summary and bullet items.
     */
    renderInsights: (insights) => {
        const container = document.getElementById("insightsContainer");
        if (!container) return;

        container.innerHTML = "";

        // 1. Text Summary Card
        const summaryCard = document.createElement("div");
        summaryCard.style.padding = "0.75rem";
        summaryCard.style.marginBottom = "1rem";
        summaryCard.style.backgroundColor = "var(--primary-light)";
        summaryCard.style.borderRadius = "8px";
        summaryCard.style.borderLeft = "4px solid var(--primary)";
        summaryCard.style.fontSize = "0.9rem";
        summaryCard.style.fontWeight = "500";
        summaryCard.textContent = insights.summary;
        container.appendChild(summaryCard);

        // 2. Narrative Bullets
        const findings = insights.findings || [];
        const recommendations = insights.recommendations || [];

        findings.forEach(finding => {
            const bullet = document.createElement("div");
            bullet.className = "insight-bullet";
            bullet.innerHTML = `
                <span class="bullet-emoji">💡</span>
                <div class="bullet-content">
                    <h5>Key Observation</h5>
                    <p>${finding}</p>
                </div>
            `;
            container.appendChild(bullet);
        });

        recommendations.forEach(rec => {
            const bullet = document.createElement("div");
            bullet.className = "insight-bullet";
            bullet.innerHTML = `
                <span class="bullet-emoji">🎯</span>
                <div class="bullet-content">
                    <h5>Action Plan Recommendation</h5>
                    <p>${rec}</p>
                </div>
            `;
            container.appendChild(bullet);
        });

        if (findings.length === 0 && recommendations.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No narratives generated for this dataset.</p>
                </div>
            `;
        }
    }
};
