from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Any
import os
from datetime import datetime
from config import settings

def generate_pdf(analysis_id: int, results: Dict[str, Any], user_email: str) -> str:
    """
    Generate a PDF report from analysis results
    """

    # Create PDF filename
    pdf_filename = f"analysis_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_FOLDER, pdf_filename)

    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Title
    story.append(Paragraph("Meta Ads Campaign Analysis Report", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Metadata
    story.append(Paragraph(f"Analysis ID: #{analysis_id}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Paragraph(f"For: {user_email}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Performance Report
    story.append(Paragraph("Performance Report", heading_style))
    performance = results.get('performance_report', {})
    if isinstance(performance, dict):
        for key, value in performance.items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    else:
        story.append(Paragraph(str(performance), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # AI Insights
    story.append(Paragraph("AI-Powered Insights", heading_style))
    insights = results.get('ai_insights', [])
    for i, insight in enumerate(insights, 1):
        story.append(Paragraph(f"{i}. {insight}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    story.append(Spacer(1, 0.3*inch))

    # Next Ad Plan
    story.append(PageBreak())
    story.append(Paragraph("Recommended Ad Plan", heading_style))
    ad_plan = results.get('next_ad_plan', {})
    if isinstance(ad_plan, dict):
        for key, value in ad_plan.items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    else:
        story.append(Paragraph(str(ad_plan), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # 30-Day Content Strategy
    story.append(Paragraph("30-Day Content Strategy", heading_style))
    content_strategy = results.get('content_strategy', {})
    if isinstance(content_strategy, dict):
        for week, plan in content_strategy.items():
            story.append(Paragraph(f"<b>{week.replace('_', ' ').title()}:</b>", styles['Normal']))
            story.append(Paragraph(str(plan), styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
    else:
        story.append(Paragraph(str(content_strategy), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Creative Prompts
    story.append(PageBreak())
    story.append(Paragraph("Creative Prompts for Your Next Ads", heading_style))
    prompts = results.get('creative_prompts', [])
    for i, prompt in enumerate(prompts, 1):
        story.append(Paragraph(f"{i}. {prompt}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    story.append(Spacer(1, 0.3*inch))

    # Captions & Hashtags
    story.append(Paragraph("Ready-to-Use Captions & Hashtags", heading_style))
    captions = results.get('captions_hashtags', [])
    for i, caption_data in enumerate(captions, 1):
        if isinstance(caption_data, dict):
            caption_text = caption_data.get('caption', '')
            hashtags = caption_data.get('hashtags', '')
            story.append(Paragraph(f"<b>Caption {i}:</b>", styles['Normal']))
            story.append(Paragraph(caption_text, styles['Normal']))
            story.append(Paragraph(f"<i>{hashtags}</i>", styles['Normal']))
        else:
            story.append(Paragraph(f"{i}. {caption_data}", styles['Normal']))
        story.append(Spacer(1, 0.15*inch))

    # Build PDF
    doc.build(story)

    return pdf_path

def generate_pdf_with_charts(analysis_id: int, results: Dict[str, Any], user_email: str, chart_images: Dict[str, str]) -> str:
    """
    Generate a PDF report from analysis results with embedded charts
    """
    from reportlab.platypus import Image as RLImage
    from io import BytesIO
    import base64

    # Create PDF filename
    pdf_filename = f"analysis_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_FOLDER, pdf_filename)

    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Helper function to add chart image
    def add_chart_image(chart_name: str):
        if chart_name in chart_images and chart_images[chart_name]:
            try:
                # Remove the data:image/png;base64, prefix
                image_data = chart_images[chart_name].split(',')[1] if ',' in chart_images[chart_name] else chart_images[chart_name]
                image_bytes = base64.b64decode(image_data)
                img = RLImage(BytesIO(image_bytes), width=6*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"Error adding chart {chart_name}: {e}")

    # Title
    story.append(Paragraph("Meta Ads Campaign Analysis Report", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Metadata
    story.append(Paragraph(f"Analysis ID: #{analysis_id}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Paragraph(f"For: {user_email}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Performance Report
    story.append(Paragraph("Performance Report", heading_style))
    add_chart_image('performance')
    performance = results.get('performance_report', {})
    if isinstance(performance, dict):
        for key, value in performance.items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    else:
        story.append(Paragraph(str(performance), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # AI Insights
    story.append(Paragraph("AI-Powered Insights", heading_style))
    add_chart_image('insights')
    insights = results.get('ai_insights', [])
    for i, insight in enumerate(insights, 1):
        story.append(Paragraph(f"{i}. {insight}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    story.append(Spacer(1, 0.3*inch))

    # Next Ad Plan
    story.append(PageBreak())
    story.append(Paragraph("Recommended Ad Plan", heading_style))
    add_chart_image('adPlan')
    ad_plan = results.get('next_ad_plan', {})
    if isinstance(ad_plan, dict):
        for key, value in ad_plan.items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    else:
        story.append(Paragraph(str(ad_plan), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # 30-Day Content Strategy
    story.append(Paragraph("30-Day Content Strategy", heading_style))
    add_chart_image('strategy')
    content_strategy = results.get('content_strategy', {})
    if isinstance(content_strategy, dict):
        for week, plan in content_strategy.items():
            story.append(Paragraph(f"<b>{week.replace('_', ' ').title()}:</b>", styles['Normal']))
            story.append(Paragraph(str(plan), styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
    else:
        story.append(Paragraph(str(content_strategy), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Creative Prompts
    story.append(PageBreak())
    story.append(Paragraph("Creative Prompts for Your Next Ads", heading_style))
    add_chart_image('prompts')
    prompts = results.get('creative_prompts', [])
    for i, prompt in enumerate(prompts, 1):
        story.append(Paragraph(f"{i}. {prompt}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    story.append(Spacer(1, 0.3*inch))

    # Captions & Hashtags
    story.append(Paragraph("Ready-to-Use Captions & Hashtags", heading_style))
    add_chart_image('captions')
    captions = results.get('captions_hashtags', [])
    for i, caption_data in enumerate(captions, 1):
        if isinstance(caption_data, dict):
            caption_text = caption_data.get('caption', '')
            hashtags = caption_data.get('hashtags', '')
            story.append(Paragraph(f"<b>Caption {i}:</b>", styles['Normal']))
            story.append(Paragraph(caption_text, styles['Normal']))
            story.append(Paragraph(f"<i>{hashtags}</i>", styles['Normal']))
        else:
            story.append(Paragraph(f"{i}. {caption_data}", styles['Normal']))
        story.append(Spacer(1, 0.15*inch))

    # Similar Businesses
    if chart_images.get('businesses'):
        story.append(PageBreak())
        story.append(Paragraph("Competitive Analysis", heading_style))
        add_chart_image('businesses')

    # Build PDF
    doc.build(story)

    return pdf_path
