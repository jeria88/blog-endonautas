#!/usr/bin/env python3
"""Email v7 — Logo original con zoom CSS, foto Franco en círculo"""

LOGO_IMG = '<img src="https://endonautas.cl/static/img/logo.ffc70eb7b9d7.png" alt="Endonautas" width="80" height="80" style="display:block;border:0;outline:none;border-radius:50%;width:80px;height:80px;object-fit:cover;transform:scale(1.4);" />'

HTML_OPEN = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<div style="display:none;font-size:1px;color:#000;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">
{{{{ preview }}}}
</div>
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
body{{margin:0;padding:0;background-color:#000000;}}
p{{margin:0 0 16px 0;}}
p:last-of-type{{margin-bottom:0;}}
ul{{margin:0 0 16px 0;padding-left:20px;}}
li{{margin-bottom:8px;}}
strong{{font-weight:500;}}
a{{color:#7ECCCD;}}
</style>
</head>
<body style="margin:0;padding:0;background-color:#000000;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#000000">
<tr><td align="center" style="padding:24px 16px 40px 16px;">

<!-- HEADER: Logo circular con zoom -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">
<tr><td align="center" style="padding:0 0 28px 0;overflow:hidden;">
<div style="border-radius:50%;width:80px;height:80px;overflow:hidden;display:inline-block;">
{LOGO_IMG}
</div>
</td></tr>
</table>

<!-- CARD -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#0a0a0a;border-radius:12px;overflow:hidden;">
<tr><td style="padding:0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:#7ECCCD;height:2px;font-size:0;line-height:0;">&nbsp;</td></tr></table></td></tr>
<tr><td style="padding:40px 44px 28px 44px;font-family:'Plus Jakarta Sans',Georgia,serif;font-size:16px;font-weight:300;line-height:1.8;color:#F0E8DC;">
<p style="margin:0 0 24px 0;font-size:14px;color:rgba(240,232,220,0.4);">Hola {{{{ nombre }}}},</p>
{{{{ body }}}}
</td></tr>
<tr><td style="padding:0 44px 36px 44px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="border-top:1px solid rgba(240,232,220,0.06);padding-top:24px;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="padding-right:14px;width:48px;">
<img src="https://endonautas.cl/static/img/franco-jeria.29d377e25215.jpeg" alt="Franco" width="48" height="48" style="display:block;border-radius:24px;border:2px solid rgba(126,204,205,0.2);width:48px;height:48px;object-fit:cover;" />
</td>
<td>
<p style="margin:0;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;font-weight:500;color:#F0E8DC;">Franco</p>
<p style="margin:2px 0 0 0;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:12px;color:rgba(240,232,220,0.35);">Fundador de Endonautas</p>
</td>
</tr>
</table>
</td></tr>
</table>
</td></tr>
<tr><td style="padding:20px 44px 24px 44px;background-color:#000000;border-top:1px solid rgba(240,232,220,0.04);">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:11px;line-height:1.7;color:rgba(240,232,220,0.2);">
<p style="margin:0 0 4px 0;">
<a href="https://endonautas.cl" style="color:rgba(240,232,220,0.2);text-decoration:none;">endonautas.cl</a>
<span style="margin:0 6px;">·</span>
<a href="https://endonautas.cl/contacto/" style="color:rgba(240,232,220,0.2);text-decoration:none;">Contacto</a>
<span style="margin:0 6px;">·</span>
<a href="{{{{ unsubscribe }}}}" style="color:rgba(240,232,220,0.2);text-decoration:none;">Cancelar suscripción</a>
</p>
<p style="margin:0;">Recibiste esto porque te suscribiste en endonautas.cl.</p>
</td></tr>
</table>
</td></tr>
</table>

</td></tr>
</table>

</body>
</html>"""

def _build():
    html = HTML_OPEN.replace("{{ preview }}", "La guía te mostró la máscara. En la app hay tests, un espejo IA y un mapa.")
    html = html.replace("{{ nombre }}", "Camila")
    html = html.replace("{{ unsubscribe }}", "https://endonautas.cl/desuscribir/")
    html = html.replace("{{ body }}", """
<p style="font-size:18px;font-weight:500;color:#F0E8DC;margin-bottom:24px;">¿Qué hay debajo de tu máscara?</p>
<p>La guía te mostró qué máscara usas. El siguiente paso es ver qué hay debajo.</p>
<p>En la app de Endonautas tienes herramientas para eso:</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:24px 0;">
<tr><td style="padding-bottom:16px;vertical-align:top;width:28px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:600;color:#7ECCCD;">01</td>
<td style="padding-bottom:16px;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;color:#F0E8DC;"><strong>Tests psicométricos</strong><br><span style="color:rgba(240,232,220,0.4);font-size:14px;">Miden exactamente esos patrones que reconociste en la guía.</span></td></tr>
<tr><td style="padding-bottom:16px;vertical-align:top;width:28px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:600;color:#7ECCCD;">02</td>
<td style="padding-bottom:16px;font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;color:#F0E8DC;"><strong>El Espejo de Conflictos</strong><br><span style="color:rgba(240,232,220,0.4);font-size:14px;">Una IA que no te da respuestas — te hace las preguntas que importan.</span></td></tr>
<tr><td style="vertical-align:top;width:28px;font-family:'Space Grotesk',Arial,sans-serif;font-size:14px;font-weight:600;color:#7ECCCD;">03</td>
<td style="font-family:'Plus Jakarta Sans',Arial,sans-serif;font-size:15px;color:#F0E8DC;"><strong>Tu Mapa Interior</strong><br><span style="color:rgba(240,232,220,0.4);font-size:14px;">Un registro de tu viaje que se construye con cada exploración.</span></td></tr>
</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0;">
<tr><td align="center">
<a href="https://app.endonautas.cl/accounts/registro/" style="display:inline-block;background-color:#F0E8DC;color:#000000;padding:14px 36px;border-radius:999px;font-family:'Space Grotesk',Arial,sans-serif;font-size:13px;font-weight:600;letter-spacing:0.3px;text-decoration:none;">Comenzar exploración gratuita →</a>
<p style="margin:10px 0 0 0;font-size:12px;color:rgba(240,232,220,0.25);">Sin tarjeta · 2 minutos · Sin compromiso</p>
</td></tr>
</table>""")
    return html

if __name__ == "__main__":
    html = _build()
    out = "/home/nikka/Proyectos/endonautas/platform/preview_v7.html"
    with open(out, "w") as f:
        f.write(html)
    print(f"Preview: {out} ({len(html)} bytes)")
