from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from auth import User, get_current_user
from service_container import get_churn_service
from limiter import limiter
import pandas as pd
import io
from fpdf import FPDF
from datetime import datetime

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

service = get_churn_service()

@router.get("/export/csv", summary="Export Statistics CSV")
@limiter.limit("10/hour")
async def export_csv(request: Request, current_user: User = Depends(get_current_user)):
    """Export churn statistics as CSV."""
    try:
        stats = service.get_stats()
        
        # Flatten the stats dictionary for CSV
        flat_stats = {
            "Total Customers": stats["total_customers"],
            "Churned Customers": stats["churned_customers"],
            "Overall Churn Rate (Yes)": f"{stats['overall_churn_rate']['Yes']:.2%}",
            "Model Version": stats["model_version"]
        }
        
        # Add feature importance
        for feature, score in stats["feature_importance"].items():
            flat_stats[f"Feature: {feature}"] = score
            
        df = pd.DataFrame([flat_stats])
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=churn_stats.csv"
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Churn Guard AI - Analytics Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

@router.get("/export/pdf", summary="Export PDF Report")
@limiter.limit("10/hour")
async def export_pdf(request: Request, current_user: User = Depends(get_current_user)):
    """Generate a PDF report of current churn usage."""
    try:
        stats = service.get_stats()
        analysis = service.get_analysis()
        
        pdf = PDFReport()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # 1. Summary Section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "1. Executive Summary", 0, 1)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.cell(0, 10, f"Total Customers: {stats['total_customers']}", 0, 1)
        pdf.cell(0, 10, f"Churn Rate: {stats['overall_churn_rate']['Yes']:.1%}", 0, 1)
        pdf.ln(5)
        
        # 2. Financial Impact
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "2. Financial Impact Estimations", 0, 1)
        pdf.set_font("Arial", size=12)
        impact = analysis["financial_impact"]
        pdf.cell(0, 10, f"Annual Exposure: ${impact['total_annual_exposure']:,.2f}", 0, 1)
        pdf.cell(0, 10, f"Avg Customer Lifetime: {impact['avg_customer_lifetime_months']} months", 0, 1)
        pdf.ln(5)
        
        # 3. High Risk Segments
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "3. High Risk Segments", 0, 1)
        pdf.set_font("Arial", size=10)
        
        # Table Header
        pdf.cell(80, 10, "Segment", 1)
        pdf.cell(30, 10, "Churn Rate", 1)
        pdf.cell(30, 10, "Size", 1)
        pdf.ln()
        
        # Table Rows
        for segment in analysis["segments"]:
            pdf.cell(80, 10, segment["segment"], 1)
            pdf.cell(30, 10, f"{segment['churn_rate']}%", 1)
            pdf.cell(30, 10, str(segment["size"]), 1)
            pdf.ln()
            
        # Output
        pdf_output = bytes(pdf.output())
        
        response = StreamingResponse(io.BytesIO(pdf_output), media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=churn_report.pdf"
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
