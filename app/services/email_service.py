import resend
from config import settings
from typing import Dict, Any

resend.api_key = settings.RESEND_API_KEY

def send_analysis_email(to_email: str, analysis_id: int, results: Dict[str, Any], pdf_path: str = None):
    """
    Send analysis results via email with optional PDF attachment
    """

    # Format email content
    insights_html = "<ul>"
    for insight in results.get("ai_insights", [])[:5]:
        insights_html += f"<li>{insight}</li>"
    insights_html += "</ul>"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h1 style="color: #0066cc;">Your Meta Ads Analysis is Ready!</h1>

        <p>Hi there,</p>

        <p>Your Meta Ads campaign analysis (ID: #{analysis_id}) has been completed. Here's a quick preview:</p>

        <h2 style="color: #0066cc;">Key Insights:</h2>
        {insights_html}

        <h2 style="color: #0066cc;">Next Steps:</h2>
        <p>{results.get('next_ad_plan', {}).get('summary', 'Check your full report for detailed recommendations.')}</p>

        <p>
            <a href="{settings.FRONTEND_URL}/dashboard/analysis/{analysis_id}"
               style="background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                View Full Report
            </a>
        </p>

        <p style="margin-top: 30px; color: #666; font-size: 14px;">
            The complete analysis including your 30-day content strategy, creative prompts, and captions is available in your dashboard.
        </p>

        <p style="color: #666; font-size: 14px;">
            Best regards,<br>
            Meta Ads AI Analyzer Team
        </p>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.FROM_EMAIL,
            "to": [to_email],
            "subject": f"Your Meta Ads Analysis is Ready! (ID: #{analysis_id})",
            "html": html_content
        }

        # Add PDF attachment if available
        if pdf_path:
            import base64
            with open(pdf_path, 'rb') as f:
                pdf_content = base64.b64encode(f.read()).decode()
                params["attachments"] = [{
                    "filename": f"meta_ads_analysis_{analysis_id}.pdf",
                    "content": pdf_content
                }]

        email = resend.Emails.send(params)
        return email

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise e
