from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from NEMO.decorators import staff_member_required
from NEMO.forms import ResourceScheduledOutageForm, save_scheduled_outage
from NEMO.models import Resource, ScheduledOutage, ScheduledOutageCategory, Tool, UsageEvent
from NEMO.utilities import RecurrenceFrequency
from NEMO.views.customization import CalendarCustomization


@staff_member_required
@require_GET
def resources(request):
    return render(
        request, "resources/resources.html", {"resources": Resource.objects.all().order_by("category", "name")}
    )


@staff_member_required
@require_GET
def resource_details(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    dictionary = {
        "resource": resource,
        "outages": ScheduledOutage.objects.filter(resource__id=resource_id, end__gt=timezone.now()),
    }
    return render(request, "resources/resource_details.html", dictionary)


@staff_member_required
@require_http_methods(["GET", "POST"])
def modify_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    dictionary = {"resource": resource}
    if request.method == "GET":
        in_use = set(map(lambda t: t.tool.tool_or_parent_id(), UsageEvent.objects.filter(end=None)))
        fully_dependent_tools = set(map(lambda f: f.id, resource.fully_dependent_tools.all()))
        fully_dependent_tools_in_use = Tool.objects.in_bulk(list(in_use & fully_dependent_tools)).values()
        dictionary["fully_dependent_tools_in_use"] = fully_dependent_tools_in_use
        return render(request, "resources/modify_resource.html", dictionary)
    elif request.method == "POST":
        status = request.POST.get("status")
        if status == "unavailable":
            resource.available = False
            reason = request.POST.get("reason")
            if not reason:
                dictionary["error"] = "You must explain why the resource is unavailable."
                return render(request, "resources/modify_resource.html", dictionary)
            resource.restriction_message = reason
            resource.save()
        elif status == "available":
            resource.available = True
            resource.save()
        else:
            dictionary["error"] = "The server received an invalid resource modification request."
            return render(request, "resources/modify_resource.html", dictionary)
        return redirect("resources")


@staff_member_required
@require_http_methods(["GET", "POST"])
def schedule_outage(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    outage_id = request.GET.get("outage_id") or request.POST.get("outage_id")
    try:
        outage = ScheduledOutage.objects.get(id=outage_id)
    except:
        outage = None
    form = ResourceScheduledOutageForm(data=request.POST or None, instance=outage)
    if request.method == "POST":
        if form.is_valid():
            title = f"{resource.name} scheduled outage"
            save_scheduled_outage(form, request.user, resource, title=title, check_policy=False)
            return redirect("resource_details", resource.id)
    calendar_outage_recurrence_limit = CalendarCustomization.get("calendar_outage_recurrence_limit")
    dictionary = {
        "resource": resource,
        "form": form,
        "editing": True if form.instance.id else False,
        "resources": Resource.objects.all().prefetch_related("category").order_by("category__name", "name"),
        "outage_categories": ScheduledOutageCategory.objects.all(),
        "recurrence_intervals": RecurrenceFrequency.choices(),
        "calendar_outage_recurrence_limit": calendar_outage_recurrence_limit,
    }
    return render(request, "resources/scheduled_outage.html", dictionary)


@staff_member_required
@require_POST
def delete_scheduled_outage(request, resource_id, outage_id):
    try:
        get_object_or_404(Resource, id=resource_id)
        get_object_or_404(ScheduledOutage, id=outage_id).delete()
    except Http404:
        pass
    return redirect(request.META.get("HTTP_REFERER", "landing"))
