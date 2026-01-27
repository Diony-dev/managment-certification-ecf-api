from lxml import etree
from app.models.semilla import Semilla
from app.services.auth.generate_key import generate_key
class SemillaBuilder:
    def __init__(self):
        self.semilla = Semilla(generate_key())      
    def build(self):
        root = etree.Element("SemillaModel")

        valorNode = etree.SubElement(root, "Valor")
        valorNode.text = self.semilla.valor

        fechaNode = etree.SubElement(root, "Fecha")
        fechaNode.text = self.semilla.fecha.strftime("%Y-%m-%d %H:%M:%S")

        return root
    def get_xml_string(self):
        return etree.tostring(self.build(), pretty_print=True).decode('utf-8')
        
