(function($) {
    'use strict';

    $(document).ready(function() {
        
        // Función para actualizar productos disponibles según sucursal
        function updateProductOptions() {
            const branchId = $('#id_branch').val();
            
            if (!branchId) return;

            // Buscar todos los selects de productos en los inlines
            $('.field-product select').each(function() {
                const $select = $(this);
                const currentValue = $select.val();
                
                $.ajax({
                    url: '/admin/sales/sale/get-products-by-branch/',
                    data: { branch_id: branchId },
                    success: function(data) {
                        // Guardar la opción vacía
                        const emptyOption = $select.find('option[value=""]').clone();
                        
                        // Limpiar opciones
                        $select.empty();
                        
                        // Agregar opción vacía
                        $select.append(emptyOption);
                        
                        // Agregar productos disponibles
                        data.products.forEach(function(product) {
                            const option = new Option(product.name, product.id);
                            $select.append(option);
                        });
                        
                        // Restaurar valor si aún existe
                        if (currentValue) {
                            $select.val(currentValue);
                        }
                    }
                });
            });
        }

        // Función para obtener precio de producto
        function updateProductPrice($row) {
            const branchId = $('#id_branch').val();
            const productId = $row.find('.field-product select').val();
            const $priceInput = $row.find('.field-price input');
            
            if (!branchId || !productId) return;

            $.ajax({
                url: '/admin/sales/sale/get-product-price/',
                data: { 
                    branch_id: branchId,
                    product_id: productId
                },
                success: function(data) {
                    $priceInput.val(data.price);
                    calculateRowTotal($row);
                    calculateGrandTotal();
                }
            });
        }

        // Función para calcular total de línea
        function calculateRowTotal($row) {
            const quantity = parseFloat($row.find('.field-quantity input').val()) || 0;
            const price = parseFloat($row.find('.field-price input').val()) || 0;
            const discount = parseFloat($row.find('.field-discount input').val()) || 0;
            
            const rowTotal = (quantity * price) - discount;
            $row.find('.field-row_total_display .readonly').text('$' + rowTotal.toFixed(2));
        }

        // Función para calcular totales generales
        function calculateGrandTotal() {
            let subtotal = 0;
            
            // Sumar todos los totales de línea
            $('.dynamic-saledetail_set').each(function() {
                const $row = $(this);
                if ($row.find('.delete input[type="checkbox"]').is(':checked')) {
                    return; // Skip deleted rows
                }
                
                const quantity = parseFloat($row.find('.field-quantity input').val()) || 0;
                const price = parseFloat($row.find('.field-price input').val()) || 0;
                const discount = parseFloat($row.find('.field-discount input').val()) || 0;
                
                subtotal += (quantity * price) - discount;
            });

            // Aplicar IVA si es CCF
            const saleType = $('#id_sale_type').val();
            let tax = 0;
            let total = subtotal;

            if (saleType === 'CCF') {
                tax = subtotal * 0.13;
                total = subtotal + tax;
            }

            // Actualizar campos readonly
            $('#id_subtotal').val(subtotal.toFixed(2));
            $('#id_tax_amount').val(tax.toFixed(2));
            $('#id_total').val(total.toFixed(2));
        }

        // Evento: cambio de sucursal
        $('#id_branch').on('change', function() {
            updateProductOptions();
            calculateGrandTotal();
        });

        // Evento: cambio de tipo de venta (para IVA)
        $('#id_sale_type').on('change', function() {
            calculateGrandTotal();
        });

        // Eventos en inlines (usando delegación para filas dinámicas)
        $(document).on('change', '.field-product select', function() {
            const $row = $(this).closest('.dynamic-saledetail_set');
            updateProductPrice($row);
        });

        $(document).on('input', '.field-quantity input, .field-price input, .field-discount input', function() {
            const $row = $(this).closest('.dynamic-saledetail_set');
            calculateRowTotal($row);
            calculateGrandTotal();
        });

        // Evento: agregar nueva fila
        $(document).on('click', '.add-row a', function() {
            setTimeout(function() {
                updateProductOptions();
            }, 100);
        });

        // Inicializar al cargar
        if ($('#id_branch').val()) {
            updateProductOptions();
            calculateGrandTotal();
        }

        // Recalcular cuando se elimina una fila
        $(document).on('change', '.delete input[type="checkbox"]', function() {
            calculateGrandTotal();
        });
    });

})(django.jQuery);