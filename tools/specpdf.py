import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
W,H = letter
BG=HexColor('#09090B'); SURF=HexColor('#111114'); LINE=HexColor('#26272D'); TEXT=HexColor('#ECEDE6'); MUTED=HexColor('#8B8F99'); ACC=HexColor('#2CDB1A')
D=open(os.path.join(ROOT,'src','wc_mark_d.txt')).read()
def mark(c, x, y, size, color):
    p=c.beginPath(); toks=re.findall(r'[MCLZ]|-?\d+\.?\d*', D); i=0; cmd=None
    sx=lambda v: x+float(v)/100*size; sy=lambda v: y+size-float(v)/100*size
    while i<len(toks):
        t=toks[i]
        if t in 'MCLZ': cmd=t; i+=1
        if cmd=='M': p.moveTo(sx(toks[i]),sy(toks[i+1])); i+=2
        elif cmd=='L': p.lineTo(sx(toks[i]),sy(toks[i+1])); i+=2
        elif cmd=='C': p.curveTo(sx(toks[i]),sy(toks[i+1]),sx(toks[i+2]),sy(toks[i+3]),sx(toks[i+4]),sy(toks[i+5])); i+=6
        elif cmd=='Z': p.close(); cmd=None
    c.setFillColor(color); c.drawPath(p, stroke=0, fill=1, fillMode=0)   # even-odd
def frame_logo(c, x, y, s, color):
    c.setStrokeColor(color); c.setLineWidth(s*0.066); c.setLineCap(1)
    k=s/512
    for pts in [((17,160),(17,40),(40,17),(160,17)),((352,17),(472,17),(495,40),(495,160)),((495,352),(495,472),(472,495),(352,495)),((160,495),(40,495),(17,472),(17,352))]:
        P=lambda q:(x+q[0]*k, y+s-q[1]*k)
        a,b,cc,d=pts; p=c.beginPath(); p.moveTo(*P(a)); p.lineTo(*P(b)); 
        # rounded corner approximated by straight join
        p.lineTo(*P(cc)); p.lineTo(*P(d)); c.drawPath(p, stroke=1, fill=0)
SPECS=[
 ("Price","~$5,000, both printers included"),
 ("Printers","2 × Voron 2.4 running Klipper"),
 ("Build volume","300 × 300 × 300 mm per printer"),
 ("Plate bank","15 magnetic, swappable plates"),
 ("Storage","32 shelf slots at 30 mm pitch, sized to each print"),
 ("Swap time","Under 60 s, print to print"),
 ("Filament","4 kg per printer, 8 kg on board"),
 ("Footprint","1.04 × 0.99 m, 1.66 m tall, on casters"),
 ("Power","Standard wall outlets: 1 plug for the cell, 1 per printer"),
 ("Network","Wi-Fi"),
 ("Controller","Raspberry Pi 5 + 2 × Raspberry Pi Pico"),
 ("Vision","Onboard camera + 9 AprilTags, 0.2 mm alignment"),
 ("Software","Web queue, in-browser slicing, Discord alerts, Klipper"),
 ("Longest hands-off run","214 hours"),
 ("Open source","CAD and software, December 2026"),
]
c=canvas.Canvas(os.path.join(ROOT,'site','workcell-spec-sheet.pdf'), pagesize=letter)
c.setTitle('The WorkCell spec sheet'); c.setAuthor('Frame Innovations')
c.setFillColor(BG); c.rect(0,0,W,H,stroke=0,fill=1)
M=54
mark(c, M, H-M-40, 40, ACC)
c.setFillColor(TEXT); c.setFont('Helvetica-Bold', 30); c.drawString(M+56, H-M-24, 'The WorkCell')
c.setFillColor(MUTED); c.setFont('Helvetica', 12); c.drawString(M+57, H-M-42, 'by Frame Innovations  ·  Spec sheet')
c.setFillColor(ACC); c.setFont('Helvetica', 15); c.drawString(M, H-M-80, 'Part to print, worry-free.')
c.setFillColor(MUTED); c.setFont('Helvetica', 10.5)
c.drawString(M, H-M-100, 'A fully autonomous two-printer cell: it prints, clears the bed, stores each part in its own slot,')
c.drawString(M, H-M-114, 'loads a clean plate in under a minute and tells the owner where their part is.')
# headline numbers
y=H-M-170; cols=[('~$5k','all-in, both printers'),('<60 s','between prints'),('214 h','hands-off record'),('300×300','mm build area')]
cw=(W-2*M)/4
for i,(n,l) in enumerate(cols):
    x=M+i*cw
    c.setFillColor(ACC); c.setFont('Helvetica-Bold', 24); c.drawString(x, y, n)
    c.setFillColor(MUTED); c.setFont('Helvetica', 9.5); c.drawString(x, y-15, l)
# spec table
y=H-M-225; rowh=27
c.setStrokeColor(LINE); c.setLineWidth(0.7)
for k,(a,b) in enumerate(SPECS):
    yy=y-k*rowh
    c.line(M, yy+rowh*0.62, W-M, yy+rowh*0.62)
    c.setFillColor(MUTED); c.setFont('Helvetica', 10); c.drawString(M, yy, a)
    c.setFillColor(TEXT); c.setFont('Helvetica', 10.5); c.drawString(M+150, yy, b)
c.line(M, y-len(SPECS)*rowh+rowh*0.62, W-M, y-len(SPECS)*rowh+rowh*0.62)
# footer
frame_logo(c, M, 40, 16, TEXT)
c.setFillColor(TEXT); c.setFont('Helvetica', 9); c.drawString(M+24, 45, 'FRAME INNOVATIONS')
c.setFillColor(MUTED); c.drawRightString(W-M, 45, '© 2026 Frame Innovations')
c.showPage(); c.save()
print('ok')
