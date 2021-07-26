/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_stock.models',function(require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');
    var model_list = models.PosModel.prototype.models
    var SuperOrder = models.Order.prototype;
    var SuperPosModel = models.PosModel.prototype;
    var SuperOrderline = models.Orderline.prototype;
    var product_model = null;
    var _t = core._t;


    models.load_fields('product.product',['qty_available','virtual_available','outgoing_qty','type']);

    models.load_models([{
        model:'stock.picking.type',
        loaded: function(self,operaciones){
            operaciones.forEach(function(item){
                if(self.config.picking_type_id[0]==item['id'])
                    self.config['stock_location_id']=item['default_location_src_id'][0]
            })
        }
    }],
    {
    'after': 'pos.config'
    })

    for(var i = 0,len = model_list.length;i<len;i++){
        if(model_list[i].model == "product.product"){
            product_model = model_list[i];
            break;
        }
    }

    //--Updating product model dictionary--
    var super_product_loaded = product_model.loaded;
    product_model.context =  function(self){
                                return {
                                    display_default_code: false,
                                    location: self.config.stock_location_id
                                };
                             }

    product_model.loaded = function(self,products){
        var res = super_product_loaded(self,products);
        rpc.query({
                model:'pos.config',
                method: 'existe_conexion',
                args:[],
            },
            {
                timeout: 300,
            }).then(function(){
                rpc.query({
                    model: 'product.product',
                    method: 'get_real_qty',
                    args:[
                        self.config.company_id[0],
                        self.config.stock_location_id,
                    ],
                    timeout:1000,
                }).then(function(stocks){
                    self.set({'wk_product_qtys':stocks});
                    self.chrome.wk_change_qty_css();
                });
		    })
        self.chrome.wk_change_qty_css();
        return res
    };


    screens.NumpadWidget.include({
        start: function() {
            var self = this;
            this._super();
            this.$el.find('.numpad-backspace').on('update_buffer',function(){
                return self.state.delete_last_char_of_buffer();
            });

            //$('.pos-logo').before("<div style='position: absolute;right: 2px; border-left: 1px solid #292929;'><a ><li class='button descarga_venta_smay'>descarga</li></a></div>")
			$('.pos-logo').before("<div style='position: absolute;right: 2px; border-left: 1px solid #292929;'><a><li class='button descarga_venta_smay'>descarga</li></a><a><li class='button descarga_recibo_smay'>recibo</li></a></div>")
        }
    });

    screens.ReceiptScreenWidget.include({
        show: function(){
            this._super()
            if(self.pos.get_order().get_total_paid()>0){
				//informacion en archivo para importar
				var fecha = moment().format('YYYY-MM-DD-HH-mm-ss')
                var href_params = self.pos.gui.prepare_file_blob(self.pos.export_paid_orders(), self.pos.get_order().name+'_'+ fecha+'.json');
                $('.button.descarga_venta_smay').removeClass('oe_hidden')
                $('.button.descarga_venta_smay').parent().attr(href_params);
                $('.button.descarga_venta_smay').click()
                $('.button.descarga_venta_smay').addClass('oe_hidden')
				
				// informacion de ticket
				
				var href_params = self.pos.gui.prepare_file_blob($('.pos-receipt-container').text(), self.pos.get_order().name+'_'+ fecha+'_TICKET.txt');
                $('.button.descarga_recibo_smay').removeClass('oe_hidden')
                $('.button.descarga_recibo_smay').parent().attr(href_params);
				setTimeout(function(){
                $('.button.descarga_recibo_smay').click()
				},1000)
                $('.button.descarga_recibo_smay').addClass('oe_hidden')
            }else{
				var fecha = moment().format('YYYY-MM-DD-HH-mm-ss')
                var href_params = self.pos.gui.prepare_file_blob(self.pos.get_order().name, self.pos.get_order().name+'_'+ fecha+'_Operacion.json');
                $('.button.descarga_venta_smay').removeClass('oe_hidden')
                $('.button.descarga_venta_smay').parent().attr(href_params);
                $('.button.descarga_venta_smay').click()
                $('.button.descarga_venta_smay').addClass('oe_hidden')
				
				// informacion de ticket
				
				var href_params = self.pos.gui.prepare_file_blob('Operación', self.pos.get_order().name+'_'+ fecha+'_TICKET_Operacion.txt');
                $('.button.descarga_recibo_smay').removeClass('oe_hidden')
                $('.button.descarga_recibo_smay').parent().attr(href_params);
				setTimeout(function(){
                $('.button.descarga_recibo_smay').click()
				},4000)
                $('.button.descarga_recibo_smay').addClass('oe_hidden')
            }
        }
    });


    screens.ProductScreenWidget.include({
		show: function(reset){
			var self = this;
			this._super(reset)
            rpc.query({
                model:'pos.config',
                method: 'existe_conexion',
                args:[],
            },
            {
                timeout: 1500,
            }).then(function(){
                rpc.query({
                    model: 'product.product',
                    method: 'get_real_qty',
                    args:[
                        self.pos.config.company_id[0],
                        self.pos.config.stock_location_id,
                    ],
                    timeout:1500,
                }).then(function(stocks){
                    self.pos.set({'wk_product_qtys':stocks});
                    self.pos.chrome.set_stock_qtys(self.pos.get('wk_product_qtys'))
                    self.pos.chrome.wk_change_qty_css();
                });
		    }).catch(function(){
		        //self.pos.chrome.set_stock_qtys(self.pos.get('wk_product_qtys'))
		    })
		    //this._super(reset)
		}
	});

	screens.ProductScreenWidget.include({
		show: function(reset){
		    this._super(reset)
		}
	});


	models.Order = models.Order.extend({
        add_product: function(product, options){
            var self = this;
            self.pos.chrome.wk_change_qty_css();
            options = options || {};

            for (var i = 0; i < this.orderlines.length; i++) {
                if(self.orderlines.at(i).product.id == product.id && self.orderlines.at(i).stock_location_id)
                    options.merge = false;
            }

            if(!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && !self.pos.get_order().is_return_order) {
                var product_qty = self.pos.get('wk_product_qtys')[product.id]
                if(product_qty == undefined)
                    $("#qty-tag"+ product.id).html('0')

                if ((parseFloat(product_qty) <= self.pos.config.wk_deny_val || product_qty == undefined )  && product.type=='product'){
                    self.pos.gui.show_popup('out_of_stock',{
                        'title':  _t("Warning !!!!"),
                        'body': _t("("+product.display_name+")"+self.pos.config.wk_error_msg+"."),
                        'product_id': product.id
                    });
                    return
                }else
                    SuperOrder.add_product.call(this, product, options);
            }else 
                SuperOrder.add_product.call(this, product, options);
            self.pos.chrome.wk_change_qty_css();
        },
    });


    models.Orderline = models.Orderline.extend({
        template: 'Orderline',

        initialize: function(attr,options){
            this.option = options;
            this.wk_line_stock_qty = 0.0
            if (options.product && self.pos.get('wk_product_qtys')[options.product.id] )
                this.wk_line_stock_qty = parseFloat(self.pos.get('wk_product_qtys')[options.product.id]);
            SuperOrderline.initialize.call(this,attr,options);
        },

        set_quantity: function(quantity, keep_price){
            var self = this;

            // -------code for POS Warehouse Management----------------
            if(self.stock_location_id && quantity && quantity!='remove'){
                if(self.pos.get_order() &&  self.pos.get_order().selected_orderline &&  self.pos.get_order().selected_orderline.cid == self.cid){
                    self.pos.gui.show_popup('out_of_stock',{
                        'title':  _t("Warning !!!!"),
                        'body': _t("Selected orderline product have different stock location, you can't update the qty of this orderline"),
                        'product_id': self.product.id
                    });
                    $('.numpad-backspace').trigger("update_buffer");
                    return ;
                }
                else{
                    SuperOrderline.set_quantity.call(this, quantity, keep_price);
                    return;
                }
            }

            // -------code for POS Warehouse Management----------------
            if( !self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && !isNaN(quantity) && quantity!=''
                    && parseFloat(self.wk_line_stock_qty)-parseFloat(quantity)<self.pos.config.wk_deny_val
                    && self.wk_line_stock_qty !=0.0 && this.option.product.type=='product'){
                self.pos.gui.show_popup('out_of_stock',{
                    'title':  _t("Warning !!!!"),
                    'body': _t("("+this.option.product.display_name+")"+self.pos.config.wk_error_msg+"."),
                    'product_id': this.option.product.id
                });
                $('.numpad-backspace').trigger("update_buffer");
                return
            }
            else{
                var wk_avail_pro = 0;
                if (self.pos.get('selectedOrder')) {
                    var wk_pro_order_line = (self.pos.get('selectedOrder')).get_selected_orderline();
                    if (!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && wk_pro_order_line){
                        var wk_current_qty = parseFloat(self.pos.get('wk_product_qtys')[wk_pro_order_line.product.id]);
                        if (quantity == '' || quantity == 'remove')
                            wk_avail_pro = wk_current_qty + wk_pro_order_line;
                        else
                            wk_avail_pro = wk_current_qty + wk_pro_order_line - quantity;
                        if ((wk_avail_pro < self.pos.config.wk_deny_val || wk_current_qty == undefined)
                                && (!(quantity == '' || quantity == 'remove' && wk_pro_order_line.product.type == 'product'))) {
                            self.pos.gui.show_popup('out_of_stock',{
                                'title':  _t("Warning !!!!"),
                                'body': _t("("+wk_pro_order_line.product.display_name+")"+self.pos.config.wk_error_msg+"."),
                                'product_id':wk_pro_order_line.product.id
                            });
                            return
                        }else
                            SuperOrderline.set_quantity.call(this, quantity, keep_price);
                    }else
                        SuperOrderline.set_quantity.call(this, quantity, keep_price);
                    self.pos.chrome.wk_change_qty_css();
                }
                else
                    SuperOrderline.set_quantity.call(this, quantity, keep_price);
            }
        },
    });


    models.PosModel = models.PosModel.extend({

        push_and_invoice_order: function(order) {
            var self = this;
            if (order != undefined) {
                if(!order.is_return_order){
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                    }
                }else{
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] + wk_order_line[j].quantity;
                    }
                }
            }
            return SuperPosModel.push_and_invoice_order.call(this, order);
        },

        push_order: function(order, opts) {
            var self = this;
            if (order != undefined) {
                if(!order.is_return_order){
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        if(!wk_order_line[j].stock_location_id)
                            self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                    }
                }else{
                    var wk_order_line = order.get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] + wk_order_line[j].quantity;
                    }
                }
            }
            return SuperPosModel.push_order.call(this, order, opts);
        },
    });


    models.NumpadState = models.NumpadState.extend({
        delete_last_char_of_buffer: function() {
            var self = this;
            if(this.get('buffer') === ""){
                if(this.get('mode') === 'quantity')
                    this.trigger('set_value','remove');
                else
                    this.trigger('set_value',this.get('buffer'));
            }else if(this.get('buffer').length >1){
                var newBuffer = this.get('buffer').slice(0,-1) || "";
                this.set({ buffer: newBuffer });
                this.trigger('set_value',this.get('buffer'));
            }
        }
    });

});
