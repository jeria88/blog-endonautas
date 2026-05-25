"""
Ingesta el libro Endonautica (207 págs) y el Diccionario de Biodescodificación
en la KB del Mirror como MirrorDocumento + MirrorChunks.

Uso:
    python3 manage.py seed_endonautica_kb
    python3 manage.py seed_endonautica_kb --force   # re-procesa aunque ya existan
"""
import os
from django.core.management.base import BaseCommand
from mirror.models import MirrorDocumento, MirrorChunk


ENDONAUTICA_PDF  = '/home/nikka/Proyectos/endonautas/assets/pdfs/endonautica-teoria-autoconocimiento.pdf'
BIODESCO_PDF     = '/home/nikka/Descargas/Diccionario-de-Biodescodificacion-Joan-Marc.pdf'
CHUNK_SIZE       = 700   # caracteres por chunk


def _extract_text(pdf_path, start_page=0, end_page=None):
    import pdfplumber
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        end = end_page or len(pdf.pages)
        for i in range(start_page, min(end, len(pdf.pages))):
            t = pdf.pages[i].extract_text()
            if t and t.strip():
                pages.append(t.strip())
    return '\n\n'.join(pages)


def _chunkify(text, size=CHUNK_SIZE):
    chunks = []
    paragraphs = text.split('\n\n')
    buf = ''
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(buf) + len(p) > size and buf:
            chunks.append(buf.strip())
            buf = p
        else:
            buf = (buf + '\n\n' + p).strip() if buf else p
    if buf.strip():
        chunks.append(buf.strip())
    return [c for c in chunks if len(c) > 80]


class Command(BaseCommand):
    help = 'Ingesta Endonautica + Biodescodificacion en la KB del Mirror'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Elimina y re-ingesta aunque ya existan')

    def handle(self, *args, **options):
        force = options['force']

        self._seed_endonautica(force)
        self._seed_biodesco(force)

        self.stdout.write(self.style.SUCCESS('\n✅ KB endonauta actualizada.'))

    def _seed_endonautica(self, force):
        nombre = 'Endonautica — Teoría del Autoconocimiento'
        if MirrorDocumento.objects.filter(nombre=nombre).exists():
            if not force:
                self.stdout.write(f'  ⏭  {nombre} ya existe (usa --force para re-ingestar)')
                return
            MirrorDocumento.objects.filter(nombre=nombre).delete()

        self.stdout.write(f'  📖 Procesando {nombre}…')
        try:
            # saltamos páginas 1-3 (copyright, dedicatoria, tabla de contenidos)
            text = _extract_text(ENDONAUTICA_PDF, start_page=3)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ No se pudo leer el PDF: {e}'))
            return

        chunks = _chunkify(text)
        doc = MirrorDocumento.objects.create(
            nombre=nombre,
            categoria='ebook',
            autor_ref='Franco Jeria Castro',
            procesado=True,
            n_chunks=len(chunks),
        )
        MirrorChunk.objects.bulk_create([
            MirrorChunk(
                documento=doc,
                categoria='ebook',
                contenido=c,
                chunk_index=i,
            )
            for i, c in enumerate(chunks)
        ])
        self.stdout.write(self.style.SUCCESS(f'  ✅ {nombre} — {len(chunks)} chunks'))

    def _seed_biodesco(self, force):
        nombre = 'Diccionario de Biodescodificación — Joan Marc Vilanova'
        if MirrorDocumento.objects.filter(nombre=nombre).exists():
            if not force:
                self.stdout.write(f'  ⏭  {nombre} ya existe (usa --force para re-ingestar)')
                return
            MirrorDocumento.objects.filter(nombre=nombre).delete()

        self.stdout.write(f'  📖 Procesando {nombre} (páginas 21–560)…')
        try:
            # Solo el diccionario (págs 21-560), saltamos índice y apéndices
            text = _extract_text(BIODESCO_PDF, start_page=20, end_page=560)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ No se pudo leer el PDF: {e}'))
            return

        chunks = _chunkify(text, size=600)
        doc = MirrorDocumento.objects.create(
            nombre=nombre,
            categoria='marco_teorico',
            autor_ref='Joan Marc Vilanova i Pujó',
            procesado=True,
            n_chunks=len(chunks),
        )
        MirrorChunk.objects.bulk_create([
            MirrorChunk(
                documento=doc,
                categoria='marco_teorico',
                contenido=c,
                chunk_index=i,
            )
            for i, c in enumerate(chunks)
        ])
        self.stdout.write(self.style.SUCCESS(f'  ✅ {nombre} — {len(chunks)} chunks'))
