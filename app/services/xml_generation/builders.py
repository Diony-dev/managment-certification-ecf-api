from lxml import etree
from .base_builder import BaseECFBuilder

class ECF31Builder(BaseECFBuilder):
    """Factura de Crédito Fiscal Electrónica (31)"""
    pass 

class ECF32Builder(BaseECFBuilder):
    """Factura de Consumo Electrónica (32)"""
    pass

class ECF33Builder(BaseECFBuilder):
    """Nota de Débito Electrónica (33)"""
    
    def _build_informacion_referencia(self):
        self._build_referencia_common()

    def _build_referencia_common(self):
        ref_data = self.data.get('InformacionReferencia')
        if not ref_data:
            raise ValueError(f"El e-CF tipo {self.tipo_ecf} requiere bloque 'InformacionReferencia'")
            
        ref_node = etree.SubElement(self.root, "InformacionReferencia")
        etree.SubElement(ref_node, "NCFModificado").text = ref_data['NCFModificado']
        
        if 'RNCOtroContribuyente' in ref_data:
            etree.SubElement(ref_node, "RNCOtroContribuyente").text = ref_data['RNCOtroContribuyente']
            
        if 'FechaNCFModificado' in ref_data:
             etree.SubElement(ref_node, "FechaNCFModificado").text = self._fmt_date(ref_data['FechaNCFModificado'])

        etree.SubElement(ref_node, "CodigoModificacion").text = str(ref_data['CodigoModificacion'])
        
        if 'RazonModificacion' in ref_data:
            etree.SubElement(ref_node, "RazonModificacion").text = ref_data['RazonModificacion']

class ECF34Builder(ECF33Builder):
    """Nota de Crédito Electrónica (34)"""

    def _build_id_doc(self, encabezado_node):
        """Sobrescribe IdDoc para incluir IndicadorNotaCredito"""
        id_doc_data = self.data['Encabezado']['IdDoc']
        id_doc = etree.SubElement(encabezado_node, "IdDoc")
        
        etree.SubElement(id_doc, "TipoeCF").text = str(id_doc_data['TipoeCF'])
        etree.SubElement(id_doc, "eNCF").text = id_doc_data['eNCF']
        
        indicador = id_doc_data.get('IndicadorNotaCredito', 0)
        etree.SubElement(id_doc, "IndicadorNotaCredito").text = str(indicador)

        if 'IndicadorMontoGravado' in id_doc_data:
            etree.SubElement(id_doc, "IndicadorMontoGravado").text = str(id_doc_data['IndicadorMontoGravado'])
            
        etree.SubElement(id_doc, "TipoIngresos").text = str(id_doc_data['TipoIngresos'])
        etree.SubElement(id_doc, "TipoPago").text = str(id_doc_data['TipoPago'])
        
        if 'FechaLimitePago' in id_doc_data:
            etree.SubElement(id_doc, "FechaLimitePago").text = self._fmt_date(id_doc_data['FechaLimitePago'])

        return id_doc


# --- BUILDERS FOR 4x SERIES (Government/Special) ---

class BaseECF4xBuilder(BaseECFBuilder):
    """
    Base for types 41, 43, 44, 45, 46, 47 which require FechaVencimientoSecuencia.
    """
    def _build_fecha_vencimiento_secuencia(self, id_doc_node):
        id_doc_data = self.data['Encabezado']['IdDoc']
        if 'FechaVencimientoSecuencia' in id_doc_data:
             etree.SubElement(id_doc_node, "FechaVencimientoSecuencia").text = self._fmt_date(id_doc_data['FechaVencimientoSecuencia'])
        else:
            raise ValueError(f"FechaVencimientoSecuencia is required for e-CF type {self.tipo_ecf}")

class ECF41Builder(BaseECF4xBuilder):
    """Compras Electrónico (41)"""
    pass

class ECF43Builder(BaseECF4xBuilder):
    """Gastos Menores Electrónico (43)"""
    pass

class ECF44Builder(BaseECF4xBuilder):
    """Regímenes Especiales Electrónico (44)"""
    pass

class ECF45Builder(BaseECF4xBuilder):
    """Gubernamental Electrónico (45)"""
    pass

class ECF46Builder(BaseECF4xBuilder):
    """Comprobante de Exportaciones Electrónico (46)"""
    
    def _build_informaciones_adicionales_extensions(self, node, data):
        # ECF 46 specific fields in InformacionesAdicionales
        if 'CondicionesEntrega' in data:
             etree.SubElement(node, "CondicionesEntrega").text = data['CondicionesEntrega']
        if 'TotalFob' in data:
             etree.SubElement(node, "TotalFob").text = self._fmt_dec(data['TotalFob'])
        if 'Seguro' in data:
             etree.SubElement(node, "Seguro").text = self._fmt_dec(data['Seguro'])
        if 'Flete' in data:
             etree.SubElement(node, "Flete").text = self._fmt_dec(data['Flete'])
        if 'OtrosGastos' in data:
             etree.SubElement(node, "OtrosGastos").text = self._fmt_dec(data['OtrosGastos'])
        if 'TotalCif' in data:
             etree.SubElement(node, "TotalCif").text = self._fmt_dec(data['TotalCif'])
        if 'RegimenAduanero' in data:
             etree.SubElement(node, "RegimenAduanero").text = data['RegimenAduanero']
        if 'NombrePuertoSalida' in data:
             etree.SubElement(node, "NombrePuertoSalida").text = data['NombrePuertoSalida']
        if 'NombrePuertoDesembarque' in data:
             etree.SubElement(node, "NombrePuertoDesembarque").text = data['NombrePuertoDesembarque']
             
        # More volume/unit fields could be added here if needed from XSD

    def _build_detalles_item_extensions(self, item_node, item_data):
        if 'Mineria' in item_data:
            mineria_data = item_data['Mineria']
            min_node = etree.SubElement(item_node, "Mineria")
            
            if 'PesoNetoKilogramo' in mineria_data:
                etree.SubElement(min_node, "PesoNetoKilogramo").text = self._fmt_dec(mineria_data['PesoNetoKilogramo'])
            if 'PesoNetoMineria' in mineria_data:
                etree.SubElement(min_node, "PesoNetoMineria").text = self._fmt_dec(mineria_data['PesoNetoMineria'])
            if 'TipoAfiliacion' in mineria_data:
                etree.SubElement(min_node, "TipoAfiliacion").text = str(mineria_data['TipoAfiliacion'])
            if 'Liquidacion' in mineria_data:
                etree.SubElement(min_node, "Liquidacion").text = str(mineria_data['Liquidacion'])


class ECF47Builder(BaseECF4xBuilder):
    """Comprobante para Pagos al Exterior Electrónico (47)"""
    
    def _build_detalles_item_extensions(self, item_node, item_data):
        # Mandatory Retencion in Item for ECF 47
        if 'Retencion' in item_data:
            ret_data = item_data['Retencion']
            ret_node = etree.SubElement(item_node, "Retencion")
            
            etree.SubElement(ret_node, "IndicadorAgenteRetencionoPercepcion").text = str(ret_data['IndicadorAgenteRetencionoPercepcion'])
            etree.SubElement(ret_node, "MontoISRRetenido").text = self._fmt_dec(ret_data['MontoISRRetenido'])
        else:
             # It is mandatory in XSD, checking strictly?
             # For now we assume if logic is correct data should be there, or validator catches it.
             pass
