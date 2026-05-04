from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from .models import Customer, Vendor, Product, Category, VendorBillItem
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from .auth_serializers import CustomTokenObtainPairSerializer
from .serializers import (
    CustomerSerializer,
    VendorSerializer,
    ProductSerializer,
    CategorySerializer,
    VendorBillSerializer,
    VendorPaymentSerializer,
    VendorLedgerEntrySerializer,
)

from invoice.serializers import InvoiceSerializer
from invoice.models import Invoice, InvoiceItem
from payments.serializers import PaymentSerializer
from payments.models import Payment
from ledger.serializers import LedgerEntrySerializer
from django.db.models import Count, Sum, Q
from decimal import Decimal
import datetime

from inventory_batch.models import Batch
from stock_adjustment.models import StockAdjustment
from inventory_barcode.models import StockMovement
from sales_orders.models import SalesOrderItem
from transactions.models import Transaction



@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_stats(request):
    total    = Customer.objects.count()
    active   = Customer.objects.filter(outstanding_balance__gt=0).count()
    inactive = total - active
    return Response({
        "total_customers": total,
        "active":          active,
        "inactive":        inactive,
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_detail(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        customer.delete()
        return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_list(request):
    if request.method == 'GET':
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_detail(request, pk):
    try:
        vendor = Vendor.objects.get(pk=pk)
    except Vendor.DoesNotExist:
        return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = VendorSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        serializer = VendorSerializer(vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        vendor.delete()
        return Response({"message": "Vendor deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_stats(request):
    from inventory_batch.models import Batch

    total_products = Product.objects.count()
    low_stock      = Product.objects.filter(stock_quantity__lte=10, stock_quantity__gt=0).count()
    out_of_stock   = Product.objects.filter(stock_quantity=0).count()
    expired_batch  = Batch.objects.filter(expiry_date__lt=datetime.date.today()).count()

    return Response({
        "total_products": total_products,
        "low_stock":      low_stock,
        "out_of_stock":   out_of_stock,
        "expired_batch":  expired_batch,
    }, status=status.HTTP_200_OK)


def _product_name_sku_query(product, name_field, sku_field=None):
    query = Q(**{f"{name_field}__iexact": product.name})
    if product.sku and sku_field:
        query |= Q(**{f"{sku_field}__iexact": product.sku})
    return query


def _product_invoice_items(product):
    return InvoiceItem.objects.filter(
        _product_name_sku_query(product, 'item_name')
    ).select_related('invoice', 'invoice__customer').order_by('-invoice__invoice_date')


def _product_purchase_items(product):
    return VendorBillItem.objects.filter(
        _product_name_sku_query(product, 'item_name')
    ).select_related('bill', 'bill__vendor').order_by('-bill__date')


def _product_sales_order_items(product):
    return SalesOrderItem.objects.filter(
        _product_name_sku_query(product, 'product_name', 'sku')
    ).select_related('sales_order').order_by('-sales_order__order_date')


def _product_stock_movements(product):
    return StockMovement.objects.filter(
        _product_name_sku_query(product, 'product_name', 'sku')
    ).order_by('-scanned_at')


def _product_transactions(product):
    query = (
        Q(reference_no__icontains=product.name) |
        Q(debit_account__icontains=product.name) |
        Q(credit_account__icontains=product.name) |
        Q(narration__icontains=product.name)
    )
    if product.sku:
        query |= (
            Q(reference_no__icontains=product.sku) |
            Q(debit_account__icontains=product.sku) |
            Q(credit_account__icontains=product.sku) |
            Q(narration__icontains=product.sku)
        )
    return Transaction.objects.filter(query).order_by('-transaction_date')


def _product_stats_payload(product):
    today = datetime.date.today()
    invoice_items = _product_invoice_items(product)
    purchase_items = _product_purchase_items(product)
    movements = _product_stock_movements(product)

    total_sales_qty = invoice_items.aggregate(t=Sum('quantity'))['t'] or Decimal('0.00')
    total_sales_amount = invoice_items.aggregate(t=Sum('total'))['t'] or Decimal('0.00')
    total_purchase_qty = purchase_items.aggregate(t=Sum('quantity'))['t'] or Decimal('0.00')
    total_purchase_amount = purchase_items.aggregate(t=Sum('total'))['t'] or Decimal('0.00')

    return {
        "product_id": f"PROD-{product.pk:04d}",
        "total_stock": product.stock_quantity,
        "low_stock_limit": product.low_stock_limit,
        "is_low_stock": product.is_low_stock,
        "is_out_of_stock": product.is_out_of_stock,
        "total_sales_qty": str(total_sales_qty),
        "total_sales_amount": str(total_sales_amount),
        "total_purchase_qty": str(total_purchase_qty),
        "total_purchase_amount": str(total_purchase_amount),
        "total_batches": Batch.objects.filter(product=product).count(),
        "expired_batches": Batch.objects.filter(product=product, expiry_date__lt=today).count(),
        "total_adjustments": StockAdjustment.objects.filter(product=product).count(),
        "total_movements": movements.count(),
    }


def _product_sales_payload(product):
    return {
        "invoice_items": [
            {
                "invoice_id": item.invoice.invoice_id,
                "invoice_number": f"INV-{item.invoice.invoice_id:04d}",
                "invoice_date": str(item.invoice.invoice_date),
                "customer": item.invoice.customer.name,
                "item_name": item.item_name,
                "quantity": str(item.quantity),
                "unit": item.unit,
                "rate": str(item.rate),
                "tax_rate": str(item.tax_rate),
                "total": str(item.total),
                "status": item.invoice.status,
            }
            for item in _product_invoice_items(product)
        ],
        "sales_order_items": [
            {
                "sales_order_id": item.sales_order.id,
                "so_number": item.sales_order.so_number,
                "order_date": str(item.sales_order.order_date),
                "customer": item.sales_order.customer_name,
                "product_name": item.product_name,
                "sku": item.sku,
                "quantity": item.quantity,
                "dispatched_quantity": item.dispatched_quantity,
                "rate": str(item.rate),
                "tax": str(item.tax),
                "total_price": str(item.total_price or Decimal('0.00')),
                "dispatch_status": item.sales_order.dispatch_status,
            }
            for item in _product_sales_order_items(product)
        ],
    }


def _product_purchases_payload(product):
    return [
        {
            "bill_id": item.bill.id,
            "bill_number": f"BILL-{item.bill.id:03d}",
            "date": str(item.bill.date),
            "vendor": item.bill.vendor.name,
            "item_name": item.item_name,
            "quantity": str(item.quantity),
            "unit": item.unit,
            "rate": str(item.rate),
            "tax_rate": str(item.tax_rate),
            "total": str(item.total),
            "status": item.bill.status,
        }
        for item in _product_purchase_items(product)
    ]


def _product_batches_payload(product):
    batches = Batch.objects.filter(product=product).prefetch_related('items').order_by('-received_on')
    return [
        {
            "batch_id": batch.batch_id,
            "batch_number": batch.batch_number,
            "sku": batch.sku,
            "received_on": str(batch.received_on),
            "expiry_date": str(batch.expiry_date) if batch.expiry_date else None,
            "total_units": batch.total_units,
            "available_units": batch.available_units,
            "reserved_units": batch.reserved_units,
            "damaged_units": batch.damaged_units,
            "bin_location": batch.bin_location,
            "batch_status": batch.batch_status,
            "qa_status": batch.qa_status,
            "items": [
                {
                    "quantity": str(item.quantity),
                    "unit": item.unit,
                    "cost_per_unit": str(item.cost_per_unit),
                    "total_cost": str(item.total_cost),
                    "expiry_date": str(item.expiry_date) if item.expiry_date else None,
                    "bin_location": item.bin_location,
                }
                for item in batch.items.all()
            ],
        }
        for batch in batches
    ]


def _product_adjustments_payload(product):
    adjustments = StockAdjustment.objects.filter(product=product).prefetch_related('items').order_by('-adjustment_date')
    return [
        {
            "adjustment_id": adjustment.adjustment_id,
            "adjustment_number": adjustment.adjustment_number,
            "adjustment_type": adjustment.adjustment_type,
            "direction": adjustment.direction,
            "reason": adjustment.reason,
            "reference": adjustment.reference,
            "status": adjustment.status,
            "warehouse": adjustment.warehouse,
            "bin_location": adjustment.bin_location,
            "quantity_before": str(adjustment.quantity_before),
            "adjusted_quantity": str(adjustment.adjusted_quantity),
            "quantity_after": str(adjustment.quantity_after),
            "adjustment_date": str(adjustment.adjustment_date),
            "notes": adjustment.notes,
            "items": [
                {
                    "description": item.description,
                    "quantity_before": str(item.quantity_before),
                    "adjusted_quantity": str(item.adjusted_quantity),
                    "quantity_after": str(item.quantity_after),
                    "unit": item.unit,
                    "bin_location": item.bin_location,
                }
                for item in adjustment.items.all()
            ],
        }
        for adjustment in adjustments
    ]


def _product_movements_payload(product):
    return [
        {
            "id": movement.id,
            "movement_number": movement.movement_number,
            "movement_type": movement.movement_type,
            "barcode": movement.barcode,
            "sku": movement.sku,
            "product_name": movement.product_name,
            "quantity": movement.quantity,
            "from_location": movement.from_location,
            "to_location": movement.to_location,
            "reference": movement.reference,
            "status": movement.status,
            "scanned_at": str(movement.scanned_at),
        }
        for movement in _product_stock_movements(product)
    ]


def _product_transactions_payload(product):
    return [
        {
            "id": txn.id,
            "voucher_number": txn.voucher_number,
            "voucher_type": txn.voucher_type,
            "transaction_date": str(txn.transaction_date),
            "reference_no": txn.reference_no,
            "debit_account": txn.debit_account,
            "credit_account": txn.credit_account,
            "amount": str(txn.amount),
            "gst_tax_rate": txn.gst_tax_rate,
            "status": txn.status,
            "source": txn.source,
            "narration": txn.narration,
        }
        for txn in _product_transactions(product)
    ]


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_detail_stats(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return Response(_product_stats_payload(product), status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_sales(request, pk):
    product = get_object_or_404(Product, pk=pk)

    invoice_items = [
        {
            "invoice_id": item.invoice.invoice_id,
            "invoice_number": f"INV-{item.invoice.invoice_id:04d}",
            "invoice_date": str(item.invoice.invoice_date),
            "customer": item.invoice.customer.name,
            "item_name": item.item_name,
            "quantity": str(item.quantity),
            "unit": item.unit,
            "rate": str(item.rate),
            "tax_rate": str(item.tax_rate),
            "total": str(item.total),
            "status": item.invoice.status,
        }
        for item in _product_invoice_items(product)
    ]

    sales_order_items = [
        {
            "sales_order_id": item.sales_order.id,
            "so_number": item.sales_order.so_number,
            "order_date": str(item.sales_order.order_date),
            "customer": item.sales_order.customer_name,
            "product_name": item.product_name,
            "sku": item.sku,
            "quantity": item.quantity,
            "dispatched_quantity": item.dispatched_quantity,
            "rate": str(item.rate),
            "tax": str(item.tax),
            "total_price": str(item.total_price or Decimal('0.00')),
            "dispatch_status": item.sales_order.dispatch_status,
        }
        for item in _product_sales_order_items(product)
    ]

    return Response({
        "invoice_items": invoice_items,
        "sales_order_items": sales_order_items,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_purchases(request, pk):
    product = get_object_or_404(Product, pk=pk)
    purchases = [
        {
            "bill_id": item.bill.id,
            "bill_number": f"BILL-{item.bill.id:03d}",
            "date": str(item.bill.date),
            "vendor": item.bill.vendor.name,
            "item_name": item.item_name,
            "quantity": str(item.quantity),
            "unit": item.unit,
            "rate": str(item.rate),
            "tax_rate": str(item.tax_rate),
            "total": str(item.total),
            "status": item.bill.status,
        }
        for item in _product_purchase_items(product)
    ]
    return Response(purchases, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_batches(request, pk):
    product = get_object_or_404(Product, pk=pk)
    batches = Batch.objects.filter(product=product).prefetch_related('items').order_by('-received_on')
    data = [
        {
            "batch_id": batch.batch_id,
            "batch_number": batch.batch_number,
            "sku": batch.sku,
            "received_on": str(batch.received_on),
            "expiry_date": str(batch.expiry_date) if batch.expiry_date else None,
            "total_units": batch.total_units,
            "available_units": batch.available_units,
            "reserved_units": batch.reserved_units,
            "damaged_units": batch.damaged_units,
            "bin_location": batch.bin_location,
            "batch_status": batch.batch_status,
            "qa_status": batch.qa_status,
            "items": [
                {
                    "quantity": str(item.quantity),
                    "unit": item.unit,
                    "cost_per_unit": str(item.cost_per_unit),
                    "total_cost": str(item.total_cost),
                    "expiry_date": str(item.expiry_date) if item.expiry_date else None,
                    "bin_location": item.bin_location,
                }
                for item in batch.items.all()
            ],
        }
        for batch in batches
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_adjustments(request, pk):
    product = get_object_or_404(Product, pk=pk)
    adjustments = StockAdjustment.objects.filter(product=product).prefetch_related('items').order_by('-adjustment_date')
    data = [
        {
            "adjustment_id": adjustment.adjustment_id,
            "adjustment_number": adjustment.adjustment_number,
            "adjustment_type": adjustment.adjustment_type,
            "direction": adjustment.direction,
            "reason": adjustment.reason,
            "reference": adjustment.reference,
            "status": adjustment.status,
            "warehouse": adjustment.warehouse,
            "bin_location": adjustment.bin_location,
            "quantity_before": str(adjustment.quantity_before),
            "adjusted_quantity": str(adjustment.adjusted_quantity),
            "quantity_after": str(adjustment.quantity_after),
            "adjustment_date": str(adjustment.adjustment_date),
            "notes": adjustment.notes,
            "items": [
                {
                    "description": item.description,
                    "quantity_before": str(item.quantity_before),
                    "adjusted_quantity": str(item.adjusted_quantity),
                    "quantity_after": str(item.quantity_after),
                    "unit": item.unit,
                    "bin_location": item.bin_location,
                }
                for item in adjustment.items.all()
            ],
        }
        for adjustment in adjustments
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_movements(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = [
        {
            "id": movement.id,
            "movement_number": movement.movement_number,
            "movement_type": movement.movement_type,
            "barcode": movement.barcode,
            "sku": movement.sku,
            "product_name": movement.product_name,
            "quantity": movement.quantity,
            "from_location": movement.from_location,
            "to_location": movement.to_location,
            "reference": movement.reference,
            "status": movement.status,
            "scanned_at": str(movement.scanned_at),
        }
        for movement in _product_stock_movements(product)
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return Response({
        "summary": _product_stats_payload(product),
        "batches": _product_batches_payload(product),
        "adjustments": _product_adjustments_payload(product),
        "movements": _product_movements_payload(product),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_transactions(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = [
        {
            "id": txn.id,
            "voucher_number": txn.voucher_number,
            "voucher_type": txn.voucher_type,
            "transaction_date": str(txn.transaction_date),
            "reference_no": txn.reference_no,
            "debit_account": txn.debit_account,
            "credit_account": txn.credit_account,
            "amount": str(txn.amount),
            "gst_tax_rate": txn.gst_tax_rate,
            "status": txn.status,
            "source": txn.source,
            "narration": txn.narration,
        }
        for txn in _product_transactions(product)
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_full_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = {
        "product_id": f"PROD-{product.pk:04d}",
        "product": ProductSerializer(product).data,
        "stats": _product_stats_payload(product),
        "sales": _product_sales_payload(product),
        "purchases": _product_purchases_payload(product),
        "stock": {
            "summary": _product_stats_payload(product),
            "batches": _product_batches_payload(product),
            "adjustments": _product_adjustments_payload(product),
            "movements": _product_movements_payload(product),
        },
        "transactions": _product_transactions_payload(product),
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def category_stats(request):
    total_categories = Category.objects.count()
    total_products   = Product.objects.count()

    most_products = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count').first()

    least_products = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('product_count').first()

    return Response({
        "total_categories": total_categories,
        "total_products":   total_products,
        "most_products": {
            "category": most_products.name if most_products else None,
            "count":    most_products.product_count if most_products else 0
        },
        "least_products": {
            "category": least_products.name if least_products else None,
            "count":    least_products.product_count if least_products else 0
        }
    }, status=status.HTTP_200_OK)


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




from django.shortcuts import get_object_or_404
from ledger.views import build_ledger_rows
from ledger.models import Invoice as LedgerInvoice, Receipt as LedgerReceipt


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_invoices(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = Invoice.objects.filter(customer=customer).order_by('-invoice_id')
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_payments(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    payments = Payment.objects.filter(customer=customer).order_by('-id')
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_ledgers(request, pk):
    customer  = get_object_or_404(Customer, pk=pk)
    from_date = request.query_params.get('from', '').strip() or None
    to_date   = request.query_params.get('to',   '').strip() or None
    rows      = build_ledger_rows(customer, from_date, to_date)
    serializer = LedgerEntrySerializer(rows, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_full_details(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    total_sales    = LedgerInvoice.objects.filter(customer=customer).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    total_received = LedgerReceipt.objects.filter(customer=customer).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    outstanding    = total_sales - total_received
    total_invoices = Invoice.objects.filter(customer=customer).count()
    last_invoice   = Invoice.objects.filter(customer=customer).order_by('-invoice_date').first()

    invoices_qs = Invoice.objects.filter(customer=customer).prefetch_related('items').order_by('-invoice_id')
    payments_qs = Payment.objects.filter(customer=customer).order_by('-id')

    data = {
        "customer_id":       f"CUST-{customer.pk:04d}",
        "total_sales":       str(total_sales),
        "total_received":    str(total_received),
        "outstanding":       str(outstanding),
        "total_invoices":    total_invoices,
        "last_invoice_date": str(last_invoice.invoice_date) if last_invoice else None,

        "basic_info": {
            "customer_type":   getattr(customer, 'customer_type',   'Business'),
            "industry_type":   getattr(customer, 'industry_type',   ''),
            "customer_name":   customer.name,
            "company_name":    customer.company_name,
            "email":           customer.email,
            "mobile":          customer.phone,
            "gst_no":          customer.gst_number,
            "pan_no":          getattr(customer, 'pan_number',      ''),
            "place_of_supply": getattr(customer, 'place_of_supply', ''),
            "status":          getattr(customer, 'status',          'Active'),
        },
        "contact_person": {
            "name":    customer.name,
            "email":   customer.email,
            "mobile":  customer.phone,
            "address": customer.billing_address,
        },
        "billing_address":  {"address": customer.billing_address},
        "shipping_address": {"address": customer.shipping_address},
        "add_info": {
            "payment_terms":       getattr(customer, 'payment_terms', ''),
            "currency":            getattr(customer, 'currency',      'INR'),
            "outstanding_balance": str(customer.outstanding_balance),
            "tags":                getattr(customer, 'tags',          ''),
            "website":             getattr(customer, 'website',       ''),
            "notes":               getattr(customer, 'notes',         ''),
        },
        "invoices": [
            {
                "invoice_id":       inv.invoice_id,
                "invoice_number":   f"INV-{inv.invoice_id:04d}",
                "invoice_type":     inv.invoice_type,
                "invoice_date":     str(inv.invoice_date),
                "due_date":         str(inv.due_date),
                "status":           inv.status,
                "sub_total":        str(inv.sub_total),
                "discount":         str(inv.discount),
                "total_tax":        str(inv.total_tax),
                "cgst":             str(inv.cgst),
                "sgst":             str(inv.sgst),
                "igst":             str(inv.igst),
                "total_amount":     str(inv.total_amount),
                "paid_amount":      str(inv.paid_amount),
                "total_due":        str(inv.total_due),
                "notes":            inv.notes,
                "terms_conditions": inv.terms_conditions,
                "created_at":       str(inv.created_at),
                "items": [
                    {
                        "item_name":   item.item_name,
                        "description": item.description,
                        "quantity":    str(item.quantity),
                        "unit":        item.unit,
                        "rate":        str(item.rate),
                        "discount":    str(item.discount),
                        "tax_rate":    str(item.tax_rate),
                        "total":       str(item.total),
                    }
                    for item in inv.items.all()
                ],
            }
            for inv in invoices_qs
        ],
        "payments": [
            {
                "id":                 pay.id,
                "receipt_number":     pay.receipt_number,
                "date":               str(pay.date),
                "payment_mode":       pay.payment_mode,
                "amount":             str(pay.amount),
                "advance_amount":     str(pay.advance_amount),
                "status":             pay.status,
                "gateway_status":     pay.gateway_status,
                "allocation_status":  pay.allocation_status,
                "invoice_allocation": pay.invoice_allocation,
                "notes":              pay.notes,
                "created_at":         str(pay.created_at),
                "updated_at":         str(pay.updated_at),
            }
            for pay in payments_qs
        ],
        "ledger": LedgerEntrySerializer(
            build_ledger_rows(customer), many=True
        ).data,
    }

    return Response(data, status=status.HTTP_200_OK)



from .models import VendorBill


def build_vendor_ledger_rows(vendor, from_date=None, to_date=None):
    bill_qs = VendorBill.objects.filter(vendor=vendor).prefetch_related('items')
    payment_qs = Payment.objects.filter(vendor=vendor)

    if from_date:
        bill_qs = bill_qs.filter(date__gte=from_date)
        payment_qs = payment_qs.filter(date__gte=from_date)
    if to_date:
        bill_qs = bill_qs.filter(date__lte=to_date)
        payment_qs = payment_qs.filter(date__lte=to_date)

    rows = []
    for bill in bill_qs:
        first_item = bill.items.first()
        rows.append({
            "date": bill.date,
            "entry_type": "Vendor Bill",
            "ref_no": f"BILL-{bill.id:03d}",
            "product": first_item.item_name if first_item else "",
            "qty": str(first_item.quantity) if first_item else "",
            "debit": Decimal("0.00"),
            "credit": bill.total_amount,
        })
    for pay in payment_qs:
        rows.append({
            "date": pay.date,
            "entry_type": "Payment",
            "ref_no": pay.receipt_number,
            "product": "",
            "qty": "",
            "debit": pay.amount,
            "credit": Decimal("0.00"),
        })

    rows.sort(key=lambda row: row["date"])
    running = Decimal("0.00")
    for row in rows:
        running += row["credit"] - row["debit"]
        row["balance"] = running
    return rows


# ---------------------------------------------------------------------------
# GET /vendors/<pk>/stats/
# The 5 colored summary cards shown at the top of the vendor detail page
# ---------------------------------------------------------------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_stats(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)

    total_purchases = VendorBill.objects.filter(vendor=vendor).aggregate(t=Sum('total_amount'))['t'] or Decimal('0.00')
    total_paid      = Payment.objects.filter(vendor=vendor).aggregate(t=Sum('amount'))['t']          or Decimal('0.00')
    payable         = total_purchases - total_paid
    total_bills     = VendorBill.objects.filter(vendor=vendor).count()
    last_bill       = VendorBill.objects.filter(vendor=vendor).order_by('-date').first()

    return Response({
        "vendor_id":        f"VEN-{vendor.pk:04d}",
        "total_purchases":  str(total_purchases),
        "total_paid":       str(total_paid),
        "payable":          str(payable),
        "total_bills":      total_bills,
        "last_bill_date":   str(last_bill.date) if last_bill else None,
    }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# GET /vendors/<pk>/bills/
# Bills tab (Image 2) â€” all purchase bills for this vendor
# ---------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_bills(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)

    if request.method == 'GET':
        bills  = VendorBill.objects.filter(vendor=vendor).prefetch_related('items').order_by('-date')
        serializer = VendorBillSerializer(bills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = VendorBillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(vendor=vendor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# GET /vendors/<pk>/payments/
# Payments tab (Image 3) â€” same Payment model, filtered by vendor FK
# Cross-maps with Customer module: a payment can carry both customer & vendor FK
# ---------------------------------------------------------------------------
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_payments(request, pk):
    vendor   = get_object_or_404(Vendor, pk=pk)

    if request.method == 'GET':
        payments = Payment.objects.filter(vendor=vendor).order_by('-id')
        serializer = VendorPaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = VendorPaymentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(vendor=vendor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# GET /vendors/<pk>/ledgers/
# Ledger / Statement tab (Image 1) â€” running payable balance
# Uses build_vendor_ledger_rows() â€” mirror of build_ledger_rows() for vendor
# Supports optional ?from=YYYY-MM-DD&to=YYYY-MM-DD query params
# ---------------------------------------------------------------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_ledgers(request, pk):
    vendor    = get_object_or_404(Vendor, pk=pk)
    from_date = request.query_params.get('from', '').strip() or None
    to_date   = request.query_params.get('to',   '').strip() or None
    rows      = build_vendor_ledger_rows(vendor, from_date, to_date)
    serializer = VendorLedgerEntrySerializer(rows, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_full_details(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)

    # â”€â”€ Stat card values â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    total_purchases = VendorBill.objects.filter(vendor=vendor).aggregate(t=Sum('total_amount'))['t'] or Decimal('0.00')
    total_paid      = Payment.objects.filter(vendor=vendor).aggregate(t=Sum('amount'))['t']          or Decimal('0.00')
    payable         = total_purchases - total_paid
    total_bills     = VendorBill.objects.filter(vendor=vendor).count()
    last_bill       = VendorBill.objects.filter(vendor=vendor).order_by('-date').first()

    # â”€â”€ Prefetch tabs data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    bills_qs    = VendorBill.objects.filter(vendor=vendor).prefetch_related('items').order_by('-date')
    payments_qs = Payment.objects.filter(vendor=vendor).order_by('-id')

    data = {

        # â”€â”€ Stat cards (5 colored cards at top of page) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        "vendor_id":       f"VEN-{vendor.pk:04d}",
        "total_purchases": str(total_purchases),
        "total_paid":      str(total_paid),
        "payable":         str(payable),
        "total_bills":     total_bills,
        "last_bill_date":  str(last_bill.date) if last_bill else None,

        # â”€â”€ Details panel â€” Basic Information â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        "basic_info": {
            "customer_type": getattr(vendor, 'customer_type', 'Business'),
            "vendor_type":   getattr(vendor, 'vendor_type',   'Supplier'),
            "vendor_name":   vendor.vendor_name,
            "company_name":  vendor.company_name,
            "email":         vendor.email,
            "mobile":        vendor.mobile,
            "gst_no":        vendor.gst_no,
            "pan_no":        vendor.pan_no,
            "status":        getattr(vendor, 'status', 'Active'),
        },

        # â”€â”€ Details panel â€” Bank Details â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        "bank_details": {
            "account_name":   vendor.account_name,
            "account_number": vendor.account_number,
            "bank_name":      vendor.bank_name,
            "ifsc_code":      vendor.ifsc_code,
            "branch":         vendor.branch,
        },

        # â”€â”€ Details panel â€” Contract Terms â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        "contract_terms": {
            "start_date":          str(vendor.contract_start_date),
            "end_date":            str(vendor.contract_end_date),
            "renewal_terms":       vendor.renewal_terms,
            "termination_clause":  vendor.termination_clause,
        },

        # â”€â”€ Details panel â€” Billing Address â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        "billing_address": {
            "country":  vendor.country,
            "state":    vendor.state,
            "city":     vendor.city,
            "pin_code": vendor.pin_code,
            "address":  vendor.address,
        },

        # â”€â”€ Bills tab â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        "bills": [
            {
                "id":           bill.id,
                "bill_number":  f"BILL-{bill.id:03d}",
                "bill_type":    bill.bill_type,
                "date":         str(bill.date),
                "due_date":     str(bill.due_date),
                "status":       bill.status,
                "sub_total":    str(bill.sub_total),
                "discount":     str(bill.discount),
                "total_tax":    str(bill.total_tax),
                "cgst":         str(bill.cgst),
                "sgst":         str(bill.sgst),
                "igst":         str(bill.igst),
                "total_amount": str(bill.total_amount),
                "paid_amount":  str(bill.paid_amount),
                "outstanding":  str(bill.total_amount - bill.paid_amount),
                "notes":        bill.notes,
                "created_at":   str(bill.created_at),
                "items": [
                    {
                        "item_name":   item.item_name,
                        "description": item.description,
                        "quantity":    str(item.quantity),
                        "unit":        item.unit,
                        "rate":        str(item.rate),
                        "discount":    str(item.discount),
                        "tax_rate":    str(item.tax_rate),
                        "total":       str(item.total),
                    }
                    for item in bill.items.all()
                ],
            }
            for bill in bills_qs
        ],

       
        "payments": [
            {
                "id":                 pay.id,
                "receipt_number":     pay.receipt_number,
                "date":               str(pay.date),
                "payment_mode":       pay.payment_mode,
                "amount":             str(pay.amount),
                "advance_amount":     str(pay.advance_amount),
                "status":             pay.status,
                "gateway_status":     pay.gateway_status,
                "allocation_status":  pay.allocation_status,
                "invoice_allocation": pay.invoice_allocation,
                "notes":              pay.notes,
                "created_at":         str(pay.created_at),
                "updated_at":         str(pay.updated_at),
            }
            for pay in payments_qs
        ],

        
        "ledger": VendorLedgerEntrySerializer(
            build_vendor_ledger_rows(vendor), many=True
        ).data,
    }

    return Response(data, status=status.HTTP_200_OK)
