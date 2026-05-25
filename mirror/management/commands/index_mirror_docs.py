"""
Genera embeddings para todos los MirrorChunk sin embedding.
Requiere OPENAI_API_KEY en .env y openai instalado.

Uso: python3 manage.py index_mirror_docs
     python3 manage.py index_mirror_docs --force   # re-indexa todo
"""

import os
import time
from django.core.management.base import BaseCommand
from mirror.models import MirrorChunk


class Command(BaseCommand):
    help = "Genera embeddings OpenAI para los chunks de la KB Mirror"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-generar embeddings aunque ya existan",
        )

    def handle(self, *args, **options):
        try:
            from openai import OpenAI
        except ImportError:
            self.stderr.write("openai no instalado. Ejecuta: pip install openai")
            return

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            self.stderr.write("OPENAI_API_KEY no encontrada en .env")
            return

        client = OpenAI(api_key=api_key)

        qs = MirrorChunk.objects.all()
        if not options["force"]:
            qs = qs.filter(embedding__isnull=True)

        total = qs.count()
        if total == 0:
            self.stdout.write("No hay chunks por indexar. Usa --force para re-indexar.")
            return

        self.stdout.write(f"Indexando {total} chunks…")
        procesados = 0

        for chunk in qs.iterator():
            try:
                resp = client.embeddings.create(
                    input=chunk.contenido,
                    model="text-embedding-3-small",
                )
                chunk.embedding = resp.data[0].embedding
                chunk.save(update_fields=["embedding"])
                procesados += 1

                if procesados % 10 == 0:
                    self.stdout.write(f"  {procesados}/{total}…")

                # Rate limit: text-embedding-3-small permite ~3000 req/min
                time.sleep(0.02)

            except Exception as e:
                self.stderr.write(f"  Error en chunk {chunk.id}: {e}")

        # Marcar documentos como procesados
        from mirror.models import MirrorDocumento
        for doc in MirrorDocumento.objects.all():
            if doc.chunks.filter(embedding__isnull=False).count() == doc.n_chunks:
                doc.procesado = True
                doc.save(update_fields=["procesado"])

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ {procesados}/{total} chunks indexados.")
        )
