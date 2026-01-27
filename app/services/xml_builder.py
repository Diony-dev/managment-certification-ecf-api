from .xml_generation.manager import ECFBuilderManager
from .xml_generation.base_builder import BaseECFBuilder

# Delegate to the new manager
class ECFBuilderFactory:
    @staticmethod
    def get_builder(data_json):
        return ECFBuilderManager.get_builder(data_json)

# Re-export BaseECFBuilder if anyone was importing it directly
# (though ideally they should use the factory)