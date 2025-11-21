import pandas as pd
from typing import Dict, Any, List
from io import StringIO

def parse_meta_ads_csv(file_path_or_content: str, from_string: bool = False) -> Dict[str, Any]:
    """
    Parse Meta Ads CSV and extract relevant metrics
    Args:
        file_path_or_content: Either a file path or CSV content string
        from_string: If True, treat first argument as CSV content string
    """
    try:
        # Read CSV from file path or string content
        if from_string:
            df = pd.read_csv(StringIO(file_path_or_content))
        else:
            df = pd.read_csv(file_path_or_content)

        # Common Meta Ads columns (adjust based on actual CSV format)
        # This is a flexible parser that handles various Meta Ads export formats

        # Calculate summary metrics
        summary = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "date_range": {},
            "metrics": {}
        }

        # Try to find common columns with flexible matching
        column_mappings = {
            "impressions": ["impressions", "Impressions", "Reach"],
            "clicks": ["clicks", "Clicks", "Link Clicks"],
            "spend": ["spend", "Spend", "Amount Spent", "amount_spent"],
            "conversions": ["conversions", "Conversions", "Results"],
            "ctr": ["ctr", "CTR", "Link Click-Through Rate"],
            "cpc": ["cpc", "CPC", "Cost per Link Click"],
            "date": ["date", "Date", "Reporting Starts", "reporting_starts"]
        }

        # Extract metrics if columns exist
        for metric, possible_cols in column_mappings.items():
            for col in possible_cols:
                if col in df.columns:
                    if metric == "date":
                        try:
                            summary["date_range"] = {
                                "start": str(df[col].min()),
                                "end": str(df[col].max())
                            }
                        except:
                            pass
                    else:
                        try:
                            summary["metrics"][metric] = {
                                "total": float(df[col].sum()),
                                "average": float(df[col].mean()),
                                "max": float(df[col].max()),
                                "min": float(df[col].min())
                            }
                        except:
                            pass
                    break

        # Get top performing ads (if ad name column exists)
        ad_name_cols = ["ad_name", "Ad Name", "Ad name", "Campaign Name", "campaign_name"]
        ad_name_col = None
        for col in ad_name_cols:
            if col in df.columns:
                ad_name_col = col
                break

        if ad_name_col:
            # Find a numeric column to sort by
            sort_col = None
            for possible_sort in ["impressions", "Impressions", "spend", "Spend", "clicks", "Clicks"]:
                if possible_sort in df.columns:
                    sort_col = possible_sort
                    break

            if sort_col:
                try:
                    summary["top_ads"] = df.nlargest(5, sort_col)[ad_name_col].tolist()
                except:
                    summary["top_ads"] = df[ad_name_col].head(5).tolist()

        # Convert DataFrame to dict for detailed data
        summary["detailed_data"] = df.to_dict('records')

        return summary

    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")

def format_metrics_for_ai(parsed_data: Dict[str, Any]) -> str:
    """
    Format parsed CSV data into a prompt for AI analysis
    """
    prompt = f"""
Analyze the following Meta Ads campaign data:

**Campaign Overview:**
- Total Ads/Rows: {parsed_data['total_rows']}
- Date Range: {parsed_data.get('date_range', {}).get('start', 'N/A')} to {parsed_data.get('date_range', {}).get('end', 'N/A')}

**Performance Metrics:**
"""

    for metric, values in parsed_data.get('metrics', {}).items():
        prompt += f"\n{metric.upper()}:\n"
        prompt += f"  - Total: {values['total']:,.2f}\n"
        prompt += f"  - Average: {values['average']:,.2f}\n"
        prompt += f"  - Max: {values['max']:,.2f}\n"
        prompt += f"  - Min: {values['min']:,.2f}\n"

    if 'top_ads' in parsed_data:
        prompt += f"\n**Top Performing Ads:** {', '.join(parsed_data['top_ads'][:5])}\n"

    return prompt
