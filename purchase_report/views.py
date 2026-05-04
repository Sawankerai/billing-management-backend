from collections import defaultdict
from decimal import Decimal

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import PurchaseOrder, PurchaseOrderItem
from .serializers import PurchaseOrderSerializer


ZERO = Decimal("0.00")


def money(value):
    return str((value or ZERO).quantize(Decimal("0.01")))


def number(value):
    return str(value or Decimal("0.00"))


def period_key(date_value, view):
    if view == "yearly":
        return date_value.strftime("%Y")
    if view == "daily":
        return date_value.strftime("%Y-%m-%d")
    return date_value.strftime("%Y-%m")


def period_label(date_value, view):
    if view == "yearly":
        return date_value.strftime("%Y")
    if view == "daily":
        return date_value.strftime("%d %b %Y")
    return date_value.strftime("%b %Y")


def parse_decimal(value):
    return value if value is not None else ZERO


def order_totals(order):
    items = list(order.items.all())
    gross = sum((parse_decimal(item.gross_purchases) for item in items), ZERO)
    returns = sum((parse_decimal(item.returns_adjustments) for item in items), ZERO)
    net = sum((parse_decimal(item.net_purchases) for item in items), ZERO)
    tax = sum((parse_decimal(item.tax_amount) for item in items), ZERO)
    taxable = sum((parse_decimal(item.taxable_value) for item in items), ZERO)
    qty_ordered = sum((parse_decimal(item.qty_ordered) for item in items), ZERO)
    qty_returned = sum((parse_decimal(item.qty_returned) for item in items), ZERO)
    received = parse_decimal(order.received_value)
    pending = net - received

    return {
        "gross": gross,
        "returns": returns,
        "net": net,
        "tax": tax,
        "taxable": taxable,
        "qty_ordered": qty_ordered,
        "qty_returned": qty_returned,
        "received": received,
        "pending": pending if pending > 0 else ZERO,
    }


def filtered_orders(request):
    qs = PurchaseOrder.objects.prefetch_related(
        Prefetch("items", queryset=PurchaseOrderItem.objects.order_by("id"))
    )

    vendor = request.query_params.get("vendor", "").strip()
    po_status = request.query_params.get("po_status", "").strip()
    debit_note = request.query_params.get("debit_note", "").strip()
    from_date = request.query_params.get("from", "").strip()
    to_date = request.query_params.get("to", "").strip()

    if vendor:
        qs = qs.filter(vendor_name__icontains=vendor)
    if po_status:
        qs = qs.filter(po_status=po_status)
    if debit_note:
        qs = qs.filter(debit_note_status=debit_note)
    if from_date:
        qs = qs.filter(order_date__gte=from_date)
    if to_date:
        qs = qs.filter(order_date__lte=to_date)

    return qs


@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchase_order_list(request):
    if request.method == "GET":
        orders = filtered_orders(request).order_by("-order_date", "-id")
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = PurchaseOrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == "GET":
        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "PUT":
        serializer = PurchaseOrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "PATCH":
        serializer = PurchaseOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    order.delete()
    return Response(
        {"message": "Purchase order deleted successfully"},
        status=status.HTTP_204_NO_CONTENT,
    )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchase_report(request):
    view = request.query_params.get("view", "monthly").strip().lower()
    if view not in {"daily", "monthly", "yearly"}:
        view = "monthly"

    orders = list(filtered_orders(request).order_by("order_date", "id"))
    today = timezone.localdate()

    cards = {
        "gross_purchases": ZERO,
        "returns_adjustments": ZERO,
        "net_purchases": ZERO,
        "input_tax_net": ZERO,
        "received_value": ZERO,
        "pending_value": ZERO,
    }
    performance = {}
    vendor_map = {}
    item_map = {}
    aging_map = {
        "Current": {"orders": 0, "pending_value": ZERO, "oldest_expected": None},
        "1-30 Days": {"orders": 0, "pending_value": ZERO, "oldest_expected": None},
        "31-60 Days": {"orders": 0, "pending_value": ZERO, "oldest_expected": None},
        "61-90 Days": {"orders": 0, "pending_value": ZERO, "oldest_expected": None},
        "90+ Days": {"orders": 0, "pending_value": ZERO, "oldest_expected": None},
    }
    register = []

    for order in orders:
        totals = order_totals(order)
        cards["gross_purchases"] += totals["gross"]
        cards["returns_adjustments"] += totals["returns"]
        cards["net_purchases"] += totals["net"]
        cards["input_tax_net"] += totals["tax"]
        cards["received_value"] += totals["received"]
        cards["pending_value"] += totals["pending"]

        key = period_key(order.order_date, view)
        if key not in performance:
            performance[key] = {
                "period": period_label(order.order_date, view),
                "orders": 0,
                "qty_ordered": ZERO,
                "gross_purchases": ZERO,
                "returns_adjustments": ZERO,
                "net_purchases": ZERO,
                "tax_net": ZERO,
                "received_value": ZERO,
                "pending_value": ZERO,
            }

        performance[key]["orders"] += 1
        performance[key]["qty_ordered"] += totals["qty_ordered"]
        performance[key]["gross_purchases"] += totals["gross"]
        performance[key]["returns_adjustments"] += totals["returns"]
        performance[key]["net_purchases"] += totals["net"]
        performance[key]["tax_net"] += totals["tax"]
        performance[key]["received_value"] += totals["received"]
        performance[key]["pending_value"] += totals["pending"]

        vendor_key = (order.vendor_name, order.vendor_company)
        if vendor_key not in vendor_map:
            vendor_map[vendor_key] = {
                "vendor": order.vendor_name,
                "company": order.vendor_company,
                "orders": 0,
                "gross_purchases": ZERO,
                "returns": ZERO,
                "net_purchases": ZERO,
                "received": ZERO,
                "pending": ZERO,
                "last_order": order.order_date,
            }

        vendor_map[vendor_key]["orders"] += 1
        vendor_map[vendor_key]["gross_purchases"] += totals["gross"]
        vendor_map[vendor_key]["returns"] += totals["returns"]
        vendor_map[vendor_key]["net_purchases"] += totals["net"]
        vendor_map[vendor_key]["received"] += totals["received"]
        vendor_map[vendor_key]["pending"] += totals["pending"]
        if order.order_date > vendor_map[vendor_key]["last_order"]:
            vendor_map[vendor_key]["last_order"] = order.order_date

        for item in order.items.all():
            if item.item_name not in item_map:
                item_map[item.item_name] = {
                    "item": item.item_name,
                    "qty_ordered": ZERO,
                    "returns": ZERO,
                    "taxable": ZERO,
                    "tax_est": ZERO,
                    "gross_purchases": ZERO,
                    "net_purchases": ZERO,
                }
            item_map[item.item_name]["qty_ordered"] += parse_decimal(item.qty_ordered)
            item_map[item.item_name]["returns"] += parse_decimal(item.qty_returned)
            item_map[item.item_name]["taxable"] += parse_decimal(item.taxable_value)
            item_map[item.item_name]["tax_est"] += parse_decimal(item.tax_amount)
            item_map[item.item_name]["gross_purchases"] += parse_decimal(
                item.gross_purchases
            )
            item_map[item.item_name]["net_purchases"] += parse_decimal(
                item.net_purchases
            )

        is_open = order.po_status not in {"received", "cancelled"}
        if is_open and totals["pending"] > 0:
            expected = order.expected_receipt_date or today
            days_old = (today - expected).days
            if days_old <= 0:
                bucket = "Current"
            elif days_old <= 30:
                bucket = "1-30 Days"
            elif days_old <= 60:
                bucket = "31-60 Days"
            elif days_old <= 90:
                bucket = "61-90 Days"
            else:
                bucket = "90+ Days"

            aging_map[bucket]["orders"] += 1
            aging_map[bucket]["pending_value"] += totals["pending"]
            oldest = aging_map[bucket]["oldest_expected"]
            if oldest is None or expected < oldest:
                aging_map[bucket]["oldest_expected"] = expected

        register.append(
            {
                "bill": order.bill_number or f"PO-{order.pk:04d}",
                "date": str(order.order_date),
                "vendor": order.vendor_name,
                "amount": money(totals["net"]),
                "paid": money(totals["received"]),
                "balance": money(totals["pending"]),
                "status": order.po_status,
            }
        )

    performance_rows = list(performance.values())
    total_net = cards["net_purchases"]

    top_vendors = sorted(
        vendor_map.values(),
        key=lambda row: row["net_purchases"],
        reverse=True,
    )
    top_items = sorted(
        item_map.values(),
        key=lambda row: row["net_purchases"],
        reverse=True,
    )

    data = {
        "summary_cards": {
            "gross_purchases": money(cards["gross_purchases"]),
            "returns_adjustments": money(cards["returns_adjustments"]),
            "net_purchases": money(cards["net_purchases"]),
            "input_tax_net": money(cards["input_tax_net"]),
            "received_value": money(cards["received_value"]),
            "pending_value": money(cards["pending_value"]),
        },
        "purchase_performance": [
            {
                "period": row["period"],
                "orders": row["orders"],
                "qty_ordered": number(row["qty_ordered"]),
                "gross_purchases": money(row["gross_purchases"]),
                "returns_adjustments": money(row["returns_adjustments"]),
                "net_purchases": money(row["net_purchases"]),
                "tax_net": money(row["tax_net"]),
                "received_value": money(row["received_value"]),
                "pending_value": money(row["pending_value"]),
            }
            for row in performance_rows
        ],
        "charts": {
            "purchases_vs_returns": [
                {
                    "period": row["period"],
                    "gross_purchases": money(row["gross_purchases"]),
                    "returns_adjustments": money(row["returns_adjustments"]),
                    "received_value": money(row["received_value"]),
                }
                for row in performance_rows
            ],
            "open_order_trend": [
                {
                    "period": row["period"],
                    "pending_value": money(row["pending_value"]),
                }
                for row in performance_rows
            ],
            "vendor_mix": [
                {
                    "vendor": row["vendor"],
                    "net_purchases": money(row["net_purchases"]),
                }
                for row in top_vendors[:5]
            ],
        },
        "top_vendors": [
            {
                "vendor": row["vendor"],
                "company": row["company"],
                "orders": row["orders"],
                "gross_purchases": money(row["gross_purchases"]),
                "returns": money(row["returns"]),
                "net_purchases": money(row["net_purchases"]),
                "received": money(row["received"]),
                "pending": money(row["pending"]),
                "last_order": str(row["last_order"]),
            }
            for row in top_vendors[:10]
        ],
        "top_items": [
            {
                "item": row["item"],
                "qty_ordered": number(row["qty_ordered"]),
                "returns": number(row["returns"]),
                "taxable": money(row["taxable"]),
                "tax_est": money(row["tax_est"]),
                "gross_purchases": money(row["gross_purchases"]),
                "net_purchases": money(row["net_purchases"]),
                "share": (
                    float((row["net_purchases"] / total_net) * 100)
                    if total_net > 0
                    else 0
                ),
            }
            for row in top_items[:10]
        ],
        "open_po_aging": [
            {
                "bucket": bucket,
                "orders": row["orders"],
                "pending_value": money(row["pending_value"]),
                "oldest_expected": (
                    str(row["oldest_expected"]) if row["oldest_expected"] else "-"
                ),
            }
            for bucket, row in aging_map.items()
        ],
        "purchase_register": register,
        "filters": {
            "view": view,
            "vendor": request.query_params.get("vendor", ""),
            "po_status": request.query_params.get("po_status", ""),
            "debit_note": request.query_params.get("debit_note", ""),
            "from": request.query_params.get("from", ""),
            "to": request.query_params.get("to", ""),
        },
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchase_report_stats(request):
    orders = list(filtered_orders(request))
    total_orders = len(orders)
    open_orders = 0
    received_orders = 0
    cancelled_orders = 0
    pending_value = ZERO

    for order in orders:
        totals = order_totals(order)
        pending_value += totals["pending"]
        if order.po_status == "received":
            received_orders += 1
        elif order.po_status == "cancelled":
            cancelled_orders += 1
        else:
            open_orders += 1

    return Response(
        {
            "total_orders": total_orders,
            "open_orders": open_orders,
            "received_orders": received_orders,
            "cancelled_orders": cancelled_orders,
            "pending_value": money(pending_value),
        },
        status=status.HTTP_200_OK,
    )
