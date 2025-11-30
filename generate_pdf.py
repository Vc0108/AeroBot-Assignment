from reportlab.pdfgen import canvas
import os

# Create the PDF in the CURRENT directory
pdf_file = "flight_policy.pdf"

c = canvas.Canvas(pdf_file)
c.drawString(100, 800, "JetSet Aviation Academy - General Policies")
c.drawString(100, 780, "1. Services:")
c.drawString(100, 760, "- Discovery Flight (Cessna 172): $150 (Age 14+)")
c.drawString(100, 740, "- Private Pilot Ground School: $300/month")
c.drawString(100, 720, "- Full Motion Simulator: $50/hour")
c.drawString(100, 700, "- Charter Quote (Citation Mustang): $2,500/hour")
c.drawString(100, 660, "2. Policies:")
c.drawString(100, 640, "- Cancellation: 24h notice required or $50 fee.")
c.drawString(100, 620, "- Weather: No fee if cancelled due to VFR conditions.")
c.drawString(100, 600, "- ID: Valid Govt ID required for all flights.")
c.save()

print(f"✅ SUCCESS! Created {pdf_file} at: {os.path.abspath(pdf_file)}")