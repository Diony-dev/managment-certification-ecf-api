from lxml import etree

class XMLValidator:
    def __init__(self, xml_string, xsd_path):
        self.xml_string = xml_string
        self.xsd_path = xsd_path
        self.errors = []

    def validate(self):
        try:
            # 1. Cargar el XSD
            xmlschema_doc = etree.parse(self.xsd_path)
            xmlschema = etree.XMLSchema(xmlschema_doc)
            
            # 2. Cargar el XML a validar
            xml_doc = etree.fromstring(self.xml_string)
            
            # 3. Validar
            xmlschema.assertValid(xml_doc)
            
            # Si llega aquí, es válido
            return True
            
        except etree.XMLSyntaxError as e:
            self.errors.append(f"Error de sintaxis XML: {str(e)}")
            return False
        except etree.DocumentInvalid as e:
            # Esta es la clave: lxml nos da los errores detallados
            for error in xmlschema.error_log:
                self.errors.append(f"Línea {error.line}, Columna {error.column}: {error.message}")
            return False
        except Exception as e:
            self.errors.append(f"Error inesperado: {str(e)}")
            return False

    def get_errors(self):
        return self.errors