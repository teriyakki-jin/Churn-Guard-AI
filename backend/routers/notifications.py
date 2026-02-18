from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from routers.reports import PDFReport
from auth import User, get_current_user
from service_container import get_churn_service
from limiter import limiter
from logger import logger
import os
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

service = get_churn_service()

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "user@example.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "admin@churnguard.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


async def generate_and_send_report(email_to: List[str]):
    """Generate PDF and send via email."""
    pdf_file = os.path.join(tempfile.gettempdir(), f"churn_report_{uuid.uuid4().hex}.pdf")

    try:
        stats = service.get_stats()
        analysis = service.get_analysis()

        pdf = PDFReport()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Executive Summary", 0, 1)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Total Customers: {stats['total_customers']}", 0, 1)
        pdf.cell(0, 10, f"Churn Rate: {stats['overall_churn_rate']['Yes']:.1%}", 0, 1)

        pdf.output(pdf_file)

        message = MessageSchema(
            subject="Churn Guard AI - Weekly Analysis Report",
            recipients=email_to,
            body="<h3>Monthly Churn Analysis</h3><p>Attached is the latest churn analysis report.</p>",
            subtype=MessageType.html,
            attachments=[pdf_file],
        )

        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        logger.error(f"Error sending report email: {e}")
    finally:
        if os.path.exists(pdf_file):
            os.remove(pdf_file)


@router.post("/send-report", summary="Send Report via Email")
@limiter.limit("5/hour")
async def send_report_email(
    request: Request,
    payload: EmailSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    background_tasks.add_task(generate_and_send_report, payload.email)
    return {"message": "Email sending queued"}
