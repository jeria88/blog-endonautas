@staff_member_required
def crm_template_edit(request, template_id):
    """Editar subject y html_content de un template."""
    tmpl = get_object_or_404(EmailTemplate, id=template_id)
    if request.method == "POST":
        form = TemplateEditForm(request.POST, instance=tmpl)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plantilla '{tmpl.name}' actualizada.")
            return redirect("crm:templates")
    else:
        form = TemplateEditForm(instance=tmpl)

    return render(request, "crm/template_edit.html", {
        "form": form,
        "tmpl": tmpl,
    })
