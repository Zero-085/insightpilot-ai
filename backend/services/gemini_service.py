import os
import time
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class InsightResponse(BaseModel):
    summary: str = Field(
        description="Executive Summary paragraph outlining the dataset quality, state, and overarching high-level business conclusions."
    )
    findings: List[str] = Field(
        description="List of observations highlighting Key Trends and Potential Problems (such as null metrics, outliers, or anomalies) detected."
    )
    recommendations: List[str] = Field(
        description="List of actionable Business Recommendations and suggested Next Steps based on the metrics."
    )

class GeminiService:
    """
    Service wrapper for Google Gemini API. Handles client connection,
    prompt creation, structured JSON generation, request timeout, and backoff retries.
    """

    def __init__(self) -> None:
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Load timeout (default 30 seconds)
        try:
            self.timeout = float(os.environ.get("GEMINI_TIMEOUT_SECONDS", "30.0"))
        except ValueError:
            self.timeout = 30.0

        self.client = None
        if self.api_key:
            try:
                # Initialize Gemini Client with custom timeout via HttpOptions (converted to milliseconds)
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options=types.HttpOptions(timeout=int(self.timeout * 1000))
                )
                logger.info(f"Gemini client initialized successfully. Model: {self.model_name}, Timeout: {self.timeout}s")
            except Exception as e:
                logger.error("Error initializing Gemini client", exc_info=True)
        else:
            logger.warning("GEMINI_API_KEY is not defined in environment variables. GeminiService will fall back to mock templates.")

    def generate_insights(self, analysis_results: Dict[str, Any], cleaning_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates business insights from data analysis and cleaning report using Gemini.
        Implements exponential backoff on transient errors up to 3 retries.
        """
        num_rows = analysis_results.get("num_rows", 0)
        num_cols = analysis_results.get("num_columns", 0)
        duplicates = cleaning_report.get("duplicates_removed", 0)
        missing_values_sum = sum(cleaning_report.get("missing_values_summary", {}).values())

        # 1. Check if client is initialized
        if not self.client:
            logger.warning("Gemini Client is uninitialized. Returning fallback reports.")
            return self._get_fallback_insights(num_rows, num_cols, duplicates, missing_values_sum, "Gemini client is uninitialized. API Key is missing.")

        # 2. Build the detailed context prompt
        prompt = self._build_prompt(analysis_results, cleaning_report)
        
        max_retries = 3
        last_exception = None

        # 3. Retry Loop with Exponential Backoff
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Request started: sending content to Gemini model {self.model_name} (Attempt {attempt + 1}/{max_retries + 1})...")
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=InsightResponse,
                        temperature=0.2
                    ),
                )
                
                logger.info("Response received: successfully generated insights from Gemini.")
                
                # Parse structured output text
                response_data = json.loads(response.text)
                return {
                    "summary": response_data.get("summary", ""),
                    "findings": response_data.get("findings", []),
                    "recommendations": response_data.get("recommendations", []),
                    "tone": "gemini_generated"
                }

            except (APIError, Exception) as e:
                last_exception = e
                logger.warning(f"Gemini API request failed on attempt {attempt + 1}.", exc_info=True)
                
                # If we have attempts left, wait and retry
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Backoff retry triggered. Waiting for {wait_time}s before next attempt...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded for Gemini API call.", exc_info=True)

        # 4. Fallback execution if all retries fail
        logger.error(f"All {max_retries + 1} attempts to generate insights failed. Returning fallback response.", exc_info=last_exception)
        return self._get_fallback_insights(num_rows, num_cols, duplicates, missing_values_sum, f"Gemini error: {str(last_exception)}")

    def _build_prompt(self, analysis: Dict[str, Any], cleaning: Dict[str, Any]) -> str:
        """
        Builds a comprehensive prompt containing cleaning and analysis metrics.
        """
        missing_summary = cleaning.get("missing_values_summary", {})
        duplicates = cleaning.get("duplicates_removed", 0)
        desc_stats = analysis.get("descriptive_statistics", {})
        correlations = analysis.get("correlation_matrix", {})
        top_cats = analysis.get("top_categorical_values", {})
        
        prompt = f"""
You are a senior business intelligence consultant and data scientist.
Analyze the following dataset metadata and statistical summaries, and generate structured business insights.

### Dataset Metadata
- Number of rows: {analysis.get("num_rows", 0)}
- Number of columns: {analysis.get("num_columns", 0)}
- Inferred types: {json.dumps(cleaning.get("inferred_data_types", {}))}

### Data Cleaning Report
- Duplicate rows removed: {duplicates}
- Missing values count per column: {json.dumps(missing_summary)}

### Descriptive Statistics (Numeric Columns Only)
{json.dumps(desc_stats, indent=2)}

### Pearson Correlation Matrix (Numeric Columns Only)
{json.dumps(correlations, indent=2)}

### Top Categorical Values Distribution
{json.dumps(top_cats, indent=2)}

Based on this information, perform the following tasks:
1. Generate an Executive Summary detailing the overall health and business context of this data.
2. Outline Key Trends observed from the statistics and distributions.
3. Identify Potential Problems (such as columns with high missing value counts, outlier spreads, or anomalous correlations).
4. Provide actionable Business Recommendations.
5. Suggest next steps to refine operations or analyze deeper.

Format your entire response strictly matching the provided JSON schema. Ensure your findings and recommendations are clear, direct, and contain no formatting symbols or raw markdown in the JSON string fields.
"""
        return prompt

    def _get_fallback_insights(self, num_rows: int, num_cols: int, duplicates: int, missing_values_sum: int, error_reason: str) -> Dict[str, Any]:
        """
        Returns a graceful fallback insight payload to prevent application crashes.
        """
        findings = [
            f"The dataset contains {num_rows} rows and {num_cols} columns.",
            f"Validation Warning: AI generation bypassed due to: {error_reason}."
        ]
        if duplicates > 0:
            findings.append(f"Successfully cleaned the dataset by removing {duplicates} duplicate entries.")
        else:
            findings.append("No duplicate entries were found in the dataset.")
            
        if missing_values_sum > 0:
            findings.append(f"Identified {missing_values_sum} missing data cells across columns.")
            
        return {
            "summary": f"Data Ingestion Complete: Processed {num_rows} records and {num_cols} columns. AI Narrative generation was bypassed.",
            "findings": findings,
            "recommendations": [
                "Proceed to inspect the Dataset Preview table and review calculated descriptive statistics manually.",
                "Ensure GEMINI_API_KEY is configured in your environment variables, uvicorn is restarted, and quota limits are active."
            ],
            "tone": "fallback_static"
        }
