'use strict';

window.addEventListener('load', function() {
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
        return;
    }

    const $ = django.jQuery;
    console.log('--- Sale Dynamic JS: MODO DETAILS ---');

    const INLINE_CLASS = '.dynamic-details'; 
    const FORMSET_NAME = 'details'; 

    const $branchSelect = $('#id_branch');
    const $saleTypeSelect = $('#id_sale_type');

    let baseUrl = window.location.pathname;
    if (baseUrl.includes('/change/')) {
        baseUrl = baseUrl.substring(0, baseUrl.indexOf('/change/'));
        baseUrl = baseUrl.substring(0, baseUrl.lastIndexOf('/') + 1); 
    } else if (baseUrl.includes('/add/')) {
        baseUrl = baseUrl.replace('add/', '');
    }

    // --- FUNCIONES AJAX ---

    function loadProductsForSelect($select) {
        const branchId = $branchSelect.val();
        if (!branchId) return;

        const currentVal = $select.val();
        $select.css('background-color', '#f0f0f0');

        $.ajax({
            url: baseUrl + 'get-products-by-branch/',
            data: { branch_id: branchId },
            success: function(data) {
                const previousVal = $select.val();
                
                $select.empty();
                $select.append(new Option('---------', ''));
                
                data.products.forEach(function(item) {
                    $select.append(new Option(item.name, item.id));
                });

                if (previousVal) {
                    $select.val(previousVal);
                }
                $select.css('background-color', 'white');
            },
            error: function(err) {
                console.error("Error AJAX Productos:", err);
                $select.css('background-color', '#ffcccc');
            }
        });
    }

    function updateProductPrice($row) {
        const branchId = $branchSelect.val();
        const productId = $row.find('.field-product select').val();
        const $priceInput = $row.find('.field-price input');
        
        if (!productId) {
            $priceInput.val('0.00');
            calculateRowTotal($row);
            return;
        }
        if (!branchId) return;

        $priceInput.css('opacity', '0.5');

        $.ajax({
            url: baseUrl + 'get-product-price/',
            data: { branch_id: branchId, product_id: productId },
            success: function(data) {
                $priceInput.val(data.price);
                $priceInput.css('opacity', '1');
                calculateRowTotal($row);
                calculateGrandTotal();
            },
            error: function() {
                $priceInput.css('opacity', '1');
            }
        });
    }

    // --- CÁLCULOS MATEMÁTICOS ---

    function calculateRowTotal($row) {
        const quantity = parseFloat($row.find('.field-quantity input').val()) || 0;
        const price = parseFloat($row.find('.field-price input').val()) || 0;
        const discountPercent = parseFloat($row.find('.field-discount input').val()) || 0;
        
        const subtotalBruto = quantity * price;
        const discountAmount = subtotalBruto * (discountPercent / 100);
        const rowTotal = subtotalBruto - discountAmount;
        
        $row.find('.field-row_total_display .readonly').text('$' + rowTotal.toFixed(2));
        return rowTotal;
    }

    function calculateGrandTotal() {
        let subtotalAccumulator = 0;
        
        $(INLINE_CLASS).each(function() {
            const $row = $(this);
            if ($row.find('.delete input[type="checkbox"]').is(':checked') || 
                $row.hasClass('empty-form') || 
                !$row.find('.field-product select').val()) {
                return;
            }
            subtotalAccumulator += calculateRowTotal($row);
        });

        const saleType = $saleTypeSelect.val();
        let tax = 0;
        if (saleType === 'CCF') {
            tax = subtotalAccumulator * 0.13;
        }
        const total = subtotalAccumulator + tax;

        $('.field-subtotal .readonly').text(subtotalAccumulator.toFixed(2));
        $('.field-tax_amount .readonly').text(tax.toFixed(2));
        $('.field-total .readonly').text(total.toFixed(2));
    }

    // --- EVENT LISTENERS ---

    // Cambio de Sucursal
    $branchSelect.on('change', function() {
        $(INLINE_CLASS).each(function() {
            const $row = $(this);
            if (!$row.hasClass('empty-form')) {
                loadProductsForSelect($row.find('.field-product select'));
            }
        });
    });

    // Cambio Tipo Venta
    $saleTypeSelect.on('change', calculateGrandTotal);

    // Cambio Producto
    $(document).on('change', INLINE_CLASS + ' .field-product select', function() {
        updateProductPrice($(this).closest(INLINE_CLASS));
    });

    // Inputs numéricos
    $(document).on('input', INLINE_CLASS + ' input', function() {
        if ($(this).closest('.field-quantity, .field-discount, .field-price').length) {
            calculateRowTotal($(this).closest(INLINE_CLASS));
            calculateGrandTotal();
        }
    });

    // Borrar
    $(document).on('click', '.delete input[type="checkbox"]', calculateGrandTotal);

    // NUEVA FILA
    $(document).on('formset:added', function(event, $row, formsetName) {
        if (formsetName === FORMSET_NAME) {
            const $select = $row.find('.field-product select');
            loadProductsForSelect($select);
        }
    });

    // --- INICIALIZACIÓN ---
    setTimeout(function() {
        if ($branchSelect.val()) {
            $(INLINE_CLASS).each(function() {
                const $row = $(this);
                const $select = $row.find('.field-product select');
                if (!$row.hasClass('empty-form') && $select.children('option').length <= 1) {
                    loadProductsForSelect($select);
                }
            });
        }
        calculateGrandTotal();
    }, 500);
});