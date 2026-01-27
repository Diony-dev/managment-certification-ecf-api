from app.services.xml_builder import ECFBuilderFactory
import json
from datetime import datetime

def get_base_mock_data(tipo_ecf, encf):
    data = {
        "Encabezado": {
            "IdDoc": {
                "TipoeCF": tipo_ecf,
                "eNCF": encf,
                "IndicadorMontoGravado": 0,
                "TipoIngresos": 1,
                "TipoPago": 1,
                "FechaLimitePago": "2023-12-31"
            },
            "Emisor": {
                "RNCEmisor": "101010101",
                "RazonSocialEmisor": "Emisor Test",
                "FechaEmision": "2023-10-27",
                "DireccionEmisor": "Calle Principal 123"
            },
            "Comprador": {
                "RNCComprador": "202020202",
                "RazonSocialComprador": "Comprador Test"
            },
            "Totales": {
                "TotalITBIS": 18.00,
                "MontoTotal": 118.00
            },
            "OtraMoneda": {
                "TipoMoneda": "USD",
                "TipoCambio": 58.50
            }
        },
        "DetallesItems": [
            {
                "NumeroLinea": 1,
                "IndicadorFacturacion": 1,
                "NombreItem": "Item Test",
                "CantidadItem": 1,
                "PrecioUnitarioItem": 100.00,
                "MontoItem": 100.00
            }
        ]
    }
    return data

def test_builder(tipo, name):
    print(f"Testing {name} ({tipo})...")
    data = get_base_mock_data(tipo, f"E{tipo}00000001")
    
    # Specific adjustments
    if tipo == 33 or tipo == 34:
        data['InformacionReferencia'] = {
            "NCFModificado": "B0100000001",
            "CodigoModificacion": 1,
            "RazonModificacion": "Error en precio"
        }
    
    if tipo == 32:
        # Test optional RNC: Remove it to verify it works
        if 'RNCComprador' in data['Encabezado']['Comprador']:
            del data['Encabezado']['Comprador']['RNCComprador']

    if tipo == 46:
        # Test Export specific fields
        data['Encabezado']['InformacionesAdicionales'] = {
            "TotalFob": 1000.00,
            "RegimenAduanero": "Export"
        }
        data['DetallesItems'][0]['Mineria'] = {
            "PesoNetoKilogramo": 50.00
        }

    if tipo == 47:
        # Test Foreign Payment specifics
        # 1. Comprador differs
        data['Encabezado']['Comprador'] = {
            "IdentificadorExtranjero": "EXT123456",
            "RazonSocialComprador": "Foreign Corp"
        }
        # 2. Retencion in item
        data['DetallesItems'][0]['Retencion'] = {
             "IndicadorAgenteRetencionoPercepcion": 1,
             "MontoISRRetenido": 10.00
        }
        # 3. Totales
        data['Encabezado']['Totales']['TotalISRRetencion'] = 10.00
        
    if tipo in [41, 43, 44, 45, 46, 47]:
        data['Encabezado']['IdDoc']['FechaVencimientoSecuencia'] = "2024-12-31"
        
    try:
        builder = ECFBuilderFactory.get_builder(data)
        xml_root = builder.build()
        xml_str = builder.get_xml_string()
        
        # Simple verification
        if f"<TipoeCF>{tipo}</TipoeCF>" in xml_str:
            print("  OK: TipoeCF found")
        else:
            print("  FAIL: TipoeCF mismatch")
            
        if tipo == 41 or tipo == 43:
            if 'TipoIngresos' in data['Encabezado']['IdDoc']:
                del data['Encabezado']['IdDoc']['TipoIngresos']

        import re
        # Verify TipoIngresos format (01, etc) - Skip for 41 and 43
        if tipo not in [41, 43]:
            if re.search(r"<TipoIngresos>0[1-6]</TipoIngresos>", xml_str):
                 print("  OK: TipoIngresos format corrected (01..06)")
            else:
                 print("  FAIL: TipoIngresos format incorrect (likely single digit)")
        else:
             if "<TipoIngresos>" not in xml_str:
                 print(f"  OK: TipoIngresos correctly absent for ECF {tipo}")
             else:
                 print(f"  FAIL: TipoIngresos present for ECF {tipo}")

        # Verify FechaHoraFirma format: DD-MM-YYYY HH:MM:SS
        if re.search(r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}", xml_str):
             print("  OK: FechaHoraFirma format corrected")
        else:
             print("  FAIL: FechaHoraFirma format incorrect")
            
        if tipo == 32:
            if "<RNCComprador>" not in xml_str:
                print("  OK: RNCComprador correctly absent (Optional test)")
            else:
                 print("  FAIL: RNCComprador present when removed")

        if tipo == 46:
            if "<TotalFob>" in xml_str and "<Mineria>" in xml_str:
                print("  OK: Export fields (TotalFob, Mineria) present")
            else:
                print("  FAIL: Export fields missing")
                
        if tipo == 47:
            if "<IdentificadorExtranjero>" in xml_str and "<Retencion>" in xml_str:
                print("  OK: Foreign Payment fields (IdentificadorExtranjero, Retencion) present")
            else:
                 print("  FAIL: Foreign Payment fields missing")

        if tipo in [41, 43, 44, 45, 46, 47]:
            if "<FechaVencimientoSecuencia>" in xml_str:
                print("  OK: FechaVencimientoSecuencia present")
            else:
                print("  FAIL: FechaVencimientoSecuencia missing!")
        else:
            if "<FechaVencimientoSecuencia>" in xml_str:
                print("  FAIL: FechaVencimientoSecuencia present when it shouldn't be!")
            else:
                print("  OK: FechaVencimientoSecuencia correctly absent")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

def main():
    test_builder(31, "Factura Credito Fiscal")
    test_builder(32, "Factura Consumo")
    test_builder(33, "Nota Debito")
    test_builder(34, "Nota Credito")
    test_builder(41, "Compras")
    test_builder(43, "Gastos Menores")
    test_builder(44, "Regimenes Especiales")
    test_builder(45, "Gubernamental")
    test_builder(46, "Exportacion")
    test_builder(47, "Pagos Exterior")

if __name__ == "__main__":
    main()
