from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

from .system import get_cpu, get_ram, get_disk


def analyze_system(cpu, ram, disk):
    problems = []

    # CPU
    if cpu > 85:
        problems.append("CPU em nível crítico, pode causar travamentos.")
    elif cpu > 65:
        problems.append("CPU em uso elevado, possível lentidão em multitarefa.")

    # RAM
    if ram > 85:
        problems.append("Memória RAM quase cheia, risco alto de travamentos.")
    elif ram > 65:
        problems.append("Uso de RAM elevado, sistema pode ficar lento.")

    # DISCO
    if disk > 90:
        problems.append("Disco quase cheio, impacto severo no desempenho.")
    elif disk > 75:
        problems.append("Pouco espaço em disco, pode afetar performance.")

    if not problems:
        problems.append("Sistema operando dentro dos parâmetros normais.")

    return problems


def generate_pdf_report(path="relatorio_fastbyte.pdf"):
    cpu = get_cpu()
    ram = get_ram()["percent"]
    disk = get_disk()[0]["percent"]

    problems = analyze_system(cpu, ram, disk)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Fastbyte - Relatório de Diagnóstico do Sistema")

    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    y -= 30

    c.drawString(50, y, f"CPU: {cpu:.0f}%")
    y -= 20
    c.drawString(50, y, f"RAM: {ram:.0f}%")
    y -= 20
    c.drawString(50, y, f"Disco: {disk:.0f}%")

    y -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Diagnóstico:")

    y -= 25

    c.setFont("Helvetica", 12)

    for p in problems:
        c.drawString(50, y, f"- {p}")
        y -= 20

        if y < 80:
            c.showPage()
            y = height - 50

    c.save()

    return path
