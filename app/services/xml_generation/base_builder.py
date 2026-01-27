from lxml import etree
from datetime import datetime

class BaseECFBuilder:
    def __init__(self, data_json):
        self.data = data_json
        try:
            self.tipo_ecf = int(self.data['Encabezado']['IdDoc']['TipoeCF'])
        except (KeyError, ValueError):
            # Fallback or raise error, though usually we assume valid structure if we got here
            self.tipo_ecf = 0
            
        self.root = etree.Element("ECF")

    def build(self):
        # 1. ENCABEZADO
        self._build_encabezado()
        
        # 2. DETALLE DE ITEMS
        self._build_detalles()
        
        # 3. SUBTOTALES (Opcional)
        if 'Subtotales' in self.data:
            self._build_subtotales()

        # 4. DESCUENTOS O RECARGOS (Opcional)
        if 'DescuentosORecargos' in self.data:
            self._build_descuentos_recargos()
            
        # 5. PAGINACIÓN (Opcional)
        if 'Paginacion' in self.data:
            self._build_paginacion()

        # 6. OTRA MONEDA (Opcional)
        if 'OtraMoneda' in self.data['Encabezado']:
            self._build_otra_moneda()

        # 7. REFERENCIAS (Hook for subclasses)
        self._build_informacion_referencia()
            
        # 8. FECHA HORA FIRMA
        self._build_fecha_hora_firma()
        
        # 9. SIGNATURE (Placeholder)
        self._build_signature()

        return self.root

    def get_xml_string(self):
        return etree.tostring(self.root, pretty_print=True, encoding='UTF-8', xml_declaration=True).decode('utf-8')

    # --- MÉTODOS DE CONSTRUCCIÓN ---

    def _build_encabezado(self):
        encabezado = etree.SubElement(self.root, "Encabezado")
        
        # <Version>
        etree.SubElement(encabezado, "Version").text = "1.0"
        
        # <IdDoc> - Hook para subclases
        self._build_id_doc(encabezado)

        # <Emisor>
        self._build_emisor(encabezado)

        # <Comprador>
        self._build_comprador(encabezado)

        # <InformacionesAdicionales> (Optional, hook)
        self._build_informaciones_adicionales(encabezado)

        # <Transporte> (Optional, hook)
        self._build_transporte(encabezado)

        # <Totales>
        self._build_totales(encabezado)
        
    def _build_id_doc(self, encabezado_node):
        """Implementación base de IdDoc (para series 31, 32, etc regulares)"""
        id_doc_data = self.data['Encabezado']['IdDoc']
        id_doc = etree.SubElement(encabezado_node, "IdDoc")
        
        etree.SubElement(id_doc, "TipoeCF").text = str(id_doc_data['TipoeCF'])
        etree.SubElement(id_doc, "eNCF").text = id_doc_data['eNCF']
        
        # Hook for FechaVencimientoSecuencia (ecf 4x)
        self._build_fecha_vencimiento_secuencia(id_doc)
        
        if 'IndicadorMontoGravado' in id_doc_data:
            etree.SubElement(id_doc, "IndicadorMontoGravado").text = str(id_doc_data['IndicadorMontoGravado'])
            
        etree.SubElement(id_doc, "TipoIngresos").text = "{:02d}".format(int(id_doc_data['TipoIngresos']))
        etree.SubElement(id_doc, "TipoPago").text = str(id_doc_data['TipoPago'])
        
        if 'FechaLimitePago' in id_doc_data:
            etree.SubElement(id_doc, "FechaLimitePago").text = self._fmt_date(id_doc_data['FechaLimitePago'])

    def _build_fecha_vencimiento_secuencia(self, id_doc_node):
        """Overridden in 4x builders"""
        pass

    def _build_emisor(self, encabezado_node):
        emisor_data = self.data['Encabezado']['Emisor']
        emisor = etree.SubElement(encabezado_node, "Emisor")
        etree.SubElement(emisor, "RNCEmisor").text = str(emisor_data['RNCEmisor'])
        etree.SubElement(emisor, "RazonSocialEmisor").text = emisor_data['RazonSocialEmisor']
        if 'NombreComercial' in emisor_data:
            etree.SubElement(emisor, "NombreComercial").text = emisor_data['NombreComercial']
        if 'Sucursal' in emisor_data:
            etree.SubElement(emisor, "Sucursal").text = emisor_data['Sucursal']
        etree.SubElement(emisor, "DireccionEmisor").text = emisor_data['DireccionEmisor']
        # Municipio/Provincia should go here if available
        # TablaTelefonoEmisor
        # CorreoEmisor
        # WebSite
        # ActividadEconomica
        # CodigoVendedor
        # NumeroFacturaInterna
        # NumeroPedidoInterno
        # ZonaVenta
        # RutaVenta
        # InformacionAdicionalEmisor
        etree.SubElement(emisor, "FechaEmision").text = self._fmt_date(emisor_data['FechaEmision'])

    def _build_comprador(self, encabezado_node):
        comprador_data = self.data['Encabezado'].get('Comprador')
        if comprador_data:
            comprador = etree.SubElement(encabezado_node, "Comprador")
            if 'RNCComprador' in comprador_data and comprador_data['RNCComprador']:
                etree.SubElement(comprador, "RNCComprador").text = str(comprador_data['RNCComprador'])
            if 'IdentificadorExtranjero' in comprador_data:
                etree.SubElement(comprador, "IdentificadorExtranjero").text = comprador_data['IdentificadorExtranjero']
            if 'RazonSocialComprador' in comprador_data:
                etree.SubElement(comprador, "RazonSocialComprador").text = comprador_data['RazonSocialComprador']
            # Add other Comprador fields if needed

    def _build_totales(self, encabezado_node):
        totales_data = self.data['Encabezado']['Totales']
        totales = etree.SubElement(encabezado_node, "Totales")
        
        if 'MontoGravadoTotal' in totales_data:
            etree.SubElement(totales, "MontoGravadoTotal").text = self._fmt_dec(totales_data['MontoGravadoTotal'])
        if 'MontoGravadoI1' in totales_data:
            etree.SubElement(totales, "MontoGravadoI1").text = self._fmt_dec(totales_data['MontoGravadoI1'])
        if 'MontoGravadoI2' in totales_data:
            etree.SubElement(totales, "MontoGravadoI2").text = self._fmt_dec(totales_data['MontoGravadoI2'])
        if 'MontoExento' in totales_data:
            etree.SubElement(totales, "MontoExento").text = self._fmt_dec(totales_data['MontoExento'])
            
        etree.SubElement(totales, "TotalITBIS").text = self._fmt_dec(totales_data['TotalITBIS'])
        
        if 'TotalITBIS1' in totales_data:
            etree.SubElement(totales, "TotalITBIS1").text = self._fmt_dec(totales_data['TotalITBIS1'])
        if 'TotalITBIS2' in totales_data:
            etree.SubElement(totales, "TotalITBIS2").text = self._fmt_dec(totales_data['TotalITBIS2'])
            
        etree.SubElement(totales, "MontoTotal").text = self._fmt_dec(totales_data['MontoTotal'])
        
        if 'MontoNoFacturable' in totales_data:
            etree.SubElement(totales, "MontoNoFacturable").text = self._fmt_dec(totales_data['MontoNoFacturable'])
        if 'MontoPeriodo' in totales_data:
            etree.SubElement(totales, "MontoPeriodo").text = self._fmt_dec(totales_data['MontoPeriodo'])
            
        if 'TotalITBISRetenido' in totales_data:
             etree.SubElement(totales, "TotalITBISRetenido").text = self._fmt_dec(totales_data['TotalITBISRetenido'])
        if 'TotalISRRetencion' in totales_data:
             etree.SubElement(totales, "TotalISRRetencion").text = self._fmt_dec(totales_data['TotalISRRetencion'])

    def _build_otra_moneda(self):
        om_data = self.data['Encabezado']['OtraMoneda']
        encabezado_node = self.root.find("Encabezado")
        om_node = etree.SubElement(encabezado_node, "OtraMoneda")

        etree.SubElement(om_node, "TipoMoneda").text = str(om_data['TipoMoneda'])
        etree.SubElement(om_node, "TipoCambio").text = "{:.4f}".format(float(om_data['TipoCambio']))
        
        fields = [
            "MontoGravadoTotalOtraMoneda", "MontoGravado1OtraMoneda", 
            "MontoExentoOtraMoneda", "TotalITBISOtraMoneda",
            "TotalITBIS1OtraMoneda", "MontoTotalOtraMoneda"
        ]
        
        for field in fields:
            if field in om_data:
                etree.SubElement(om_node, field).text = self._fmt_dec(om_data[field])

    def _build_detalles(self):
        detalles_node = etree.SubElement(self.root, "DetallesItems")
        items = self.data.get('DetallesItems', [])
        
        for item_data in items:
            item = etree.SubElement(detalles_node, "Item")
            
            etree.SubElement(item, "NumeroLinea").text = str(item_data['NumeroLinea'])
            etree.SubElement(item, "IndicadorFacturacion").text = str(item_data['IndicadorFacturacion'])
            etree.SubElement(item, "NombreItem").text = item_data['NombreItem']
            
            if 'IndicadorBienoServicio' in item_data:
                etree.SubElement(item, "IndicadorBienoServicio").text = str(item_data['IndicadorBienoServicio'])

            if 'DescripcionItem' in item_data:
                etree.SubElement(item, "DescripcionItem").text = item_data['DescripcionItem']
                
            etree.SubElement(item, "CantidadItem").text = self._fmt_dec(item_data['CantidadItem'])
            etree.SubElement(item, "PrecioUnitarioItem").text = self._fmt_dec(item_data['PrecioUnitarioItem'])
            
            if 'DescuentoMonto' in item_data:
                 etree.SubElement(item, "DescuentoMonto").text = self._fmt_dec(item_data['DescuentoMonto'])

            if 'OtraMonedaDetalle' in item_data:
                om_det = item_data['OtraMonedaDetalle']
                om_node = etree.SubElement(item, "OtraMonedaDetalle") 
                etree.SubElement(om_node, "PrecioOtraMoneda").text = self._fmt_dec(om_det['PrecioOtraMoneda'])
                etree.SubElement(om_node, "MontoItemOtraMoneda").text = self._fmt_dec(om_det['MontoItemOtraMoneda'])
                 
            etree.SubElement(item, "MontoItem").text = self._fmt_dec(item_data['MontoItem'])
            
            self._build_detalles_item_extensions(item, item_data)

    def _build_detalles_item_extensions(self, item_node, item_data):
        pass

    def _build_informacion_referencia(self):
        pass

    # --- OPTIONAL BLOCKS IMPLEMENTATION ---

    def _build_subtotales(self):
        subtotales_data = self.data.get('Subtotales')
        if not subtotales_data: return

        subtotales_node = etree.SubElement(self.root, "Subtotales")
        for sub_data in subtotales_data.get('Subtotal', []):
            sub_node = etree.SubElement(subtotales_node, "Subtotal")
            
            if 'NumeroSubTotal' in sub_data:
                etree.SubElement(sub_node, "NumeroSubTotal").text = str(sub_data['NumeroSubTotal'])
            if 'DescripcionSubtotal' in sub_data:
                etree.SubElement(sub_node, "DescripcionSubtotal").text = sub_data['DescripcionSubtotal']
            if 'Orden' in sub_data:
                etree.SubElement(sub_node, "Orden").text = str(sub_data['Orden'])
            if 'SubTotalMontoGravadoTotal' in sub_data:
                etree.SubElement(sub_node, "SubTotalMontoGravadoTotal").text = self._fmt_dec(sub_data['SubTotalMontoGravadoTotal'])
            if 'SubTotalMontoGravadoI3' in sub_data:
                etree.SubElement(sub_node, "SubTotalMontoGravadoI3").text = self._fmt_dec(sub_data['SubTotalMontoGravadoI3'])
            if 'SubTotaITBIS' in sub_data:
                etree.SubElement(sub_node, "SubTotaITBIS").text = self._fmt_dec(sub_data['SubTotaITBIS'])
            if 'SubTotaITBIS3' in sub_data:
                etree.SubElement(sub_node, "SubTotaITBIS3").text = self._fmt_dec(sub_data['SubTotaITBIS3'])
            if 'MontoSubTotal' in sub_data:
                etree.SubElement(sub_node, "MontoSubTotal").text = self._fmt_dec(sub_data['MontoSubTotal'])
            if 'Lineas' in sub_data:
                etree.SubElement(sub_node, "Lineas").text = str(sub_data['Lineas'])

    def _build_descuentos_recargos(self):
        dr_data = self.data.get('DescuentosORecargos')
        if not dr_data: return

        dr_node = etree.SubElement(self.root, "DescuentosORecargos")
        for item in dr_data.get('DescuentoORecargo', []):
            item_node = etree.SubElement(dr_node, "DescuentoORecargo")
            
            etree.SubElement(item_node, "NumeroLinea").text = str(item['NumeroLinea'])
            etree.SubElement(item_node, "TipoAjuste").text = item['TipoAjuste']
            if 'DescripcionDescuentooRecargo' in item:
                etree.SubElement(item_node, "DescripcionDescuentooRecargo").text = item['DescripcionDescuentooRecargo']
            if 'TipoValor' in item:
                etree.SubElement(item_node, "TipoValor").text = item['TipoValor']
            if 'ValorDescuentooRecargo' in item:
                etree.SubElement(item_node, "ValorDescuentooRecargo").text = self._fmt_dec(item['ValorDescuentooRecargo'])
            if 'MontoDescuentooRecargo' in item:
                etree.SubElement(item_node, "MontoDescuentooRecargo").text = self._fmt_dec(item['MontoDescuentooRecargo'])
            if 'MontoDescuentooRecargoOtraMoneda' in item:
                etree.SubElement(item_node, "MontoDescuentooRecargoOtraMoneda").text = self._fmt_dec(item['MontoDescuentooRecargoOtraMoneda'])
            if 'IndicadorFacturacionDescuentooRecargo' in item:
                etree.SubElement(item_node, "IndicadorFacturacionDescuentooRecargo").text = str(item['IndicadorFacturacionDescuentooRecargo'])

    def _build_paginacion(self):
        pag_data = self.data.get('Paginacion')
        if not pag_data: return

        pag_node = etree.SubElement(self.root, "Paginacion")
        for pagina in pag_data.get('Pagina', []):
            p_node = etree.SubElement(pag_node, "Pagina")
            
            etree.SubElement(p_node, "PaginaNo").text = str(pagina['PaginaNo'])
            etree.SubElement(p_node, "NoLineaDesde").text = str(pagina['NoLineaDesde'])
            etree.SubElement(p_node, "NoLineaHasta").text = str(pagina['NoLineaHasta'])
            
            if 'SubtotalMontoGravadoPagina' in pagina:
                etree.SubElement(p_node, "SubtotalMontoGravadoPagina").text = self._fmt_dec(pagina['SubtotalMontoGravadoPagina'])
            if 'SubtotalItbisPagina' in pagina:
                etree.SubElement(p_node, "SubtotalItbisPagina").text = self._fmt_dec(pagina['SubtotalItbisPagina'])
            if 'MontoSubtotalPagina' in pagina:
                etree.SubElement(p_node, "MontoSubtotalPagina").text = self._fmt_dec(pagina['MontoSubtotalPagina'])
            if 'SubtotalMontoNoFacturablePagina' in pagina:
                 etree.SubElement(p_node, "SubtotalMontoNoFacturablePagina").text = self._fmt_dec(pagina['SubtotalMontoNoFacturablePagina'])

    def _build_informaciones_adicionales(self, encabezado_node):
        info_data = self.data['Encabezado'].get('InformacionesAdicionales')
        if not info_data: return

        info_node = etree.SubElement(encabezado_node, "InformacionesAdicionales")
        
        # Standard fields commonly available
        if 'FechaEmbarque' in info_data:
            etree.SubElement(info_node, "FechaEmbarque").text = self._fmt_date(info_data['FechaEmbarque'])
        if 'NumeroEmbarque' in info_data:
            etree.SubElement(info_node, "NumeroEmbarque").text = info_data['NumeroEmbarque']
        if 'NumeroContenedor' in info_data:
            etree.SubElement(info_node, "NumeroContenedor").text = info_data['NumeroContenedor']
        if 'NumeroReferencia' in info_data:
            etree.SubElement(info_node, "NumeroReferencia").text = str(info_data['NumeroReferencia'])
        if 'PesoBruto' in info_data:
            etree.SubElement(info_node, "PesoBruto").text = self._fmt_dec(info_data['PesoBruto'])
        if 'PesoNeto' in info_data:
            etree.SubElement(info_node, "PesoNeto").text = self._fmt_dec(info_data['PesoNeto'])
        if 'UnidadPesoBruto' in info_data:
            etree.SubElement(info_node, "UnidadPesoBruto").text = str(info_data['UnidadPesoBruto'])
        if 'UnidadPesoNeto' in info_data:
             etree.SubElement(info_node, "UnidadPesoNeto").text = str(info_data['UnidadPesoNeto'])
        
        # Add simpler hook for extended subclass fields
        self._build_informaciones_adicionales_extensions(info_node, info_data)

    def _build_informaciones_adicionales_extensions(self, node, data):
        """Hook for subclasses to add more fields to InformacionesAdicionales"""
        pass

    def _build_transporte(self, encabezado_node):
        transporte_data = self.data['Encabezado'].get('Transporte')
        if not transporte_data: return

        t_node = etree.SubElement(encabezado_node, "Transporte")
        
        if 'Conductor' in transporte_data:
            etree.SubElement(t_node, "Conductor").text = transporte_data['Conductor']
        if 'DocumentoTransporte' in transporte_data:
            etree.SubElement(t_node, "DocumentoTransporte").text = str(transporte_data['DocumentoTransporte'])
        if 'Ficha' in transporte_data:
            etree.SubElement(t_node, "Ficha").text = transporte_data['Ficha']
        if 'Placa' in transporte_data:
            etree.SubElement(t_node, "Placa").text = transporte_data['Placa']
        if 'RutaTransporte' in transporte_data:
            etree.SubElement(t_node, "RutaTransporte").text = transporte_data['RutaTransporte']
        if 'ZonaTransporte' in transporte_data:
            etree.SubElement(t_node, "ZonaTransporte").text = transporte_data['ZonaTransporte']
        if 'NumeroAlbaran' in transporte_data:
            etree.SubElement(t_node, "NumeroAlbaran").text = transporte_data['NumeroAlbaran']

    def _build_fecha_hora_firma(self):
        fechahora_node = etree.SubElement(self.root, "FechaHoraFirma")
        # Format required: DD-MM-YYYY HH:MM:SS
        fechahora_node.text = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    def _build_signature(self):
        # Placeholder for Digital Signature to satisfy XSD (minOccurs=1 for xs:any)
        # In a real scenario, this is replaced by the actual signature process.
        sig = etree.SubElement(self.root, "Signature")
        sig.set("xmlns", "http://www.w3.org/2000/09/xmldsig#")

    def _fmt_dec(self, value):
        if value is None: return "0.00"
        return "{:.2f}".format(float(value))

    def _fmt_date(self, date_str):
        if not date_str: return ""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y")
        except ValueError:
            return date_str
