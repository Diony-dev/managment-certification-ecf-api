from . import ecf_bp
from flask import request, jsonify, current_app as app
from app.services.xml_builder import ECFBuilderFactory
from app.services.validate_xml import XMLValidator

@ecf_bp.route('/ecf', methods=['POST', 'GET'])
def create_ecf():
    json_data = request.json
    try:
        # Instanciamos el builder adecuado usando el Factory
        builder = ECFBuilderFactory.get_builder(json_data)
        
        # Construimos el árbol
        builder.build()
        
        # Obtenemos el string
        xml_str = builder.get_xml_string()

        # --- VALIDACIÓN ---
        """        # Asumiendo que tu XSD está en app/models/ecf_schema.xsd
        xsd_path = "app/models/schemas/e-CF 34 v.1.0 (1).xsd"
        app.logger.info(f"Validando XML contra XSD: {xsd_path}")
        app.logger.info(f"XML a validar: {xml_str}")
        validator = XMLValidator(xml_str.encode('utf-8'), xsd_path)
        is_valid = validator.validate()
        """

        xml_str = xml_str.encode('utf-8')
    
        
        # Opcional: Retornar los errores junto con el XML para depurar
       
        
        app.logger.info("XML validado correctamente contra el XSD.")
        
        # Retornamos texto plano (o XML) para que lo veas en Postman
        return app.response_class(xml_str, mimetype='application/xml')
        
    except ValueError as e:
        app.logger.error(f"Error al generar ECF: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error al generar ECF: {str(e)}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    
